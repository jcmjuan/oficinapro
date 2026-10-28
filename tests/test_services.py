"""Testes dos serviços de aplicação, relatórios e PDF."""

from __future__ import annotations

import os
import tempfile
import unittest
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from domain.exceptions import RegraNegocioError
from domain.status_os import StatusOS

from application.configuracao_service import ConfiguracaoService
from application.orcamento_service import OrcamentoService
from application.ordem_servico_service import OrdemServicoService
from application.relatorio_service import RelatorioService
from infrastructure.database import Database
from infrastructure.pdf.orcamento_pdf import PdfGenerator
from infrastructure.repositories.cliente_repository import ClienteRepository
from infrastructure.repositories.configuracao_repository import ConfiguracaoRepository
from infrastructure.repositories.mecanico_repository import MecanicoRepository
from infrastructure.repositories.oficina_repository import OficinaRepository
from infrastructure.repositories.ordem_servico_repository import OrdemServicoRepository
from infrastructure.repositories.veiculo_repository import VeiculoRepository
from infrastructure.seed import seed_demo


class TestServices(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self.tmp.name, "teste.db"))
        seed_demo(self.db)
        self.clientes = ClienteRepository(self.db)
        self.mecanicos = MecanicoRepository(self.db)
        self.veiculos = VeiculoRepository(self.db)
        self.ordens = OrdemServicoRepository(self.db)
        self.oficinas = OficinaRepository(self.db)
        self.config = ConfiguracaoRepository(self.db)
        self.os_service = OrdemServicoService(
            self.clientes, self.veiculos, self.mecanicos, self.ordens, self.oficinas
        )

    def tearDown(self):
        self.db.fechar()
        self.tmp.cleanup()

    def test_criar_ordem_e_ciclo_completo(self):
        ana = self.clientes.listar("Ana")[0]
        veiculo = ana.veiculos[0]
        mecanico = self.mecanicos.listar()[0]
        ordem = self.os_service.criar_ordem(
            ana.id,
            veiculo.id,
            mecanico.id,
            observacoes="Teste de integração",
            data_abertura=datetime(2026, 10, 26, 9, 0),
        )
        self.assertEqual(ordem.numero, "2026-0043")
        self.assertEqual(ordem.status, StatusOS.ORCAMENTO)
        self.os_service.adicionar_peca(ordem.numero, "Filtro de ar", 1, 60)
        self.os_service.adicionar_mao_de_obra(
            ordem.numero, "Troca de filtro", Decimal("0.5"), 120
        )
        self.assertEqual(self.os_service.obter(ordem.numero).total, Decimal("120.00"))
        self.os_service.aplicar_desconto(ordem.numero, 20)
        self.os_service.aprovar(ordem.numero, "teste")
        self.os_service.iniciar(ordem.numero, "teste")
        km = veiculo.km + 50
        finalizada = self.os_service.finalizar(
            ordem.numero, km_saida=km, usuario="teste"
        )
        self.assertEqual(finalizada.status, StatusOS.FINALIZADA)
        self.assertEqual(finalizada.total, Decimal("100.00"))
        self.assertEqual(self.veiculos.buscar_por_id(veiculo.id).km, km)
        self.assertEqual(len(finalizada.historico), 4)

    def test_criar_ordem_com_veiculo_de_outro_cliente(self):
        ana = self.clientes.listar("Ana")[0]
        carlos = self.clientes.listar("Carlos")[0]
        mecanico = self.mecanicos.listar()[0]
        with self.assertRaises(RegraNegocioError):
            self.os_service.criar_ordem(
                ana.id, carlos.veiculos[0].id, mecanico.id
            )

    def test_relatorio_reproduz_totais_da_etapa2(self):
        relatorio = RelatorioService(self.ordens)
        dados = relatorio.resumo(date(2026, 10, 1), date(2026, 10, 31))
        self.assertEqual(dados["quantidade_os"], 18)
        self.assertEqual(dados["faturamento"], Decimal("18450.00"))
        self.assertEqual(dados["mao_obra"], Decimal("6320.00"))
        self.assertEqual(dados["pecas"], Decimal("12130.00"))
        self.assertEqual(dados["comissoes"], Decimal("743.00"))
        comissoes = {item["nome"]: item for item in dados["mecanicos"]}
        self.assertEqual(comissoes["Marcos Silva"]["comissao"], Decimal("360.00"))
        self.assertEqual(comissoes["Rafael Costa"]["comissao"], Decimal("230.00"))
        self.assertEqual(comissoes["Diego Almeida"]["comissao"], Decimal("153.00"))
        self.assertEqual(comissoes["Marcos Silva"]["quantidade_os"], 8)

    def test_exportacao_csv(self):
        relatorio = RelatorioService(self.ordens)
        destino = Path(self.tmp.name) / "comissoes.csv"
        relatorio.exportar_comissoes_csv(
            destino, date(2026, 10, 1), date(2026, 10, 31)
        )
        self.assertTrue(destino.exists())
        texto = destino.read_text(encoding="utf-8-sig")
        self.assertIn("Marcos Silva", texto)
        self.assertIn("360,00", texto)

    def test_whatsapp(self):
        orcamento = OrcamentoService(self.ordens, self.oficinas)
        mensagem = orcamento.mensagem_whatsapp("2026-0042")
        self.assertIn("2026-0042", mensagem)
        self.assertIn("R$ 1.240,00", mensagem)
        link = orcamento.link_whatsapp("2026-0042")
        self.assertTrue(link.startswith("https://wa.me/5511987654321?text="))
        self.assertIn("2026-0042", link)

    def test_pdf_quando_chrome_disponivel(self):
        pdf = PdfGenerator()
        if not pdf.disponivel:
            self.skipTest("Chrome/Chromium indisponível neste ambiente.")
        destino = Path(self.tmp.name) / "orcamento.pdf"
        orcamento = OrcamentoService(self.ordens, self.oficinas, pdf)
        resultado = orcamento.gerar_pdf("2026-0042", destino)
        self.assertTrue(resultado.exists())
        self.assertGreater(resultado.stat().st_size, 1000)

    def test_configuracao_e_backup(self):
        servico = ConfiguracaoService(self.config, self.oficinas, self.db)
        self.assertEqual(servico.obter_oficina().nome, "DevSolo Studio")
        servico.definir("tema", "claro")
        self.assertEqual(servico.obter("tema"), "claro")
        backup = servico.fazer_backup(Path(self.tmp.name) / "backup.db")
        self.assertTrue(backup.exists())
        self.assertEqual(servico.backup.validar(backup), "ok")


if __name__ == "__main__":
    unittest.main()
