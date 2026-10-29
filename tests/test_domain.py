"""Testes de domínio: entidades, valores e ciclo de vida da OS."""

from __future__ import annotations

import unittest
from datetime import datetime
from decimal import Decimal

from domain.cliente import Cliente
from domain.exceptions import RegraNegocioError, TransicaoInvalida, ValidacaoError
from domain.item_os import ItemOS
from domain.mao_de_obra import MaoDeObra
from domain.mecanico import Mecanico
from domain.oficina import Oficina
from domain.ordem_servico import OrdemServico
from domain.peca import Peca
from domain.pessoa import Pessoa
from domain.status_os import StatusOS
from domain.tipo_item import TipoItem
from domain.validators import (
    formatar_brl,
    formatar_documento,
    formatar_telefone,
    normalizar_placa,
)
from domain.veiculo import Veiculo


def base():
    cliente = Cliente(
        "Ana Paula Ribeiro",
        "(11) 98765-4321",
        "123.456.789-00",
        email="ana@email.com",
    )
    mecanico = Mecanico(
        "Marcos Silva",
        "(11) 98888-7777",
        "MEC-001",
        Decimal("0.12"),
    )
    veiculo = Veiculo("ABC-1D23", "Honda", "Civic", 2019, 62480, cliente)
    return cliente, mecanico, veiculo


def os_exemplo(cliente, mecanico, veiculo) -> OrdemServico:
    ordem = OrdemServico(
        "2026-0042",
        cliente,
        veiculo,
        mecanico,
        data_abertura=datetime(2026, 10, 24, 9, 30),
    )
    for item in (
        Peca("Filtro de óleo", 1, 45),
        Peca("Óleo de motor 5W30", 1, 180),
        MaoDeObra("Troca de óleo e filtros", Decimal("1.50"), 120, mecanico),
        MaoDeObra("Alinhamento e balanceamento", Decimal("1.00"), 120, mecanico),
        Peca("Pastilha de freio dianteira", 1, 320),
        MaoDeObra("Substituição de pastilhas", Decimal("1.50"), 120, mecanico),
        Peca("Correia dentada", 1, 215),
    ):
        ordem.adicionar_item(item)
    return ordem


class TestValidadores(unittest.TestCase):
    def test_placa_mercosul_e_antiga(self):
        self.assertEqual(normalizar_placa("abc1d23"), "ABC-1D23")
        self.assertEqual(normalizar_placa("ABC-1234"), "ABC-1234")
        with self.assertRaises(ValidacaoError):
            normalizar_placa("ABC-12")

    def test_formatacao_documento_telefone_brl(self):
        self.assertEqual(formatar_documento("12345678900"), "123.456.789-00")
        self.assertEqual(formatar_documento("12345678000190"), "12.345.678/0001-90")
        self.assertEqual(formatar_telefone("11987654321"), "(11) 98765-4321")
        self.assertEqual(formatar_brl(Decimal("1240")), "R$ 1.240,00")

    def test_cliente_valida_documento(self):
        with self.assertRaises(ValidacaoError):
            Cliente("Ana", "(11) 98765-4321", "123")


class TestEntidades(unittest.TestCase):
    def test_pessoa_abstrata(self):
        with self.assertRaises(TypeError):
            Pessoa("Ana", "(11) 98765-4321")

    def test_relacionamento_cliente_veiculo(self):
        cliente, _, veiculo = base()
        self.assertIs(veiculo.cliente, cliente)
        self.assertIn(veiculo, cliente.veiculos)
        outro = Cliente("Carlos", "(11) 97654-3210", "234.567.890-11")
        outro.adicionar_veiculo(veiculo)
        self.assertIs(veiculo.cliente, outro)
        self.assertNotIn(veiculo, cliente.veiculos)

    def test_comissao_mecanico(self):
        _, mecanico, _ = base()
        self.assertEqual(mecanico.calcular_comissao(Decimal("3000")), Decimal("360.00"))
        with self.assertRaises(ValidacaoError):
            Mecanico("X", "(11) 98888-7777", "MEC-X", Decimal("1.5"))

    def test_itens_polimorficos(self):
        _, mecanico, _ = base()
        peca = Peca("Filtro", 2, 45)
        mao = MaoDeObra("Serviço", Decimal("1.5"), 120, mecanico)
        self.assertIsInstance(peca, ItemOS)
        self.assertIsInstance(mao, ItemOS)
        self.assertIs(peca.tipo(), TipoItem.PECA)
        self.assertIs(mao.tipo(), TipoItem.MAO_DE_OBRA)
        self.assertEqual(peca.calcular_subtotal(), Decimal("90.00"))
        self.assertEqual(mao.calcular_subtotal(), Decimal("180.00"))
        self.assertEqual(peca.rotulo_tipo, "Peça")
        self.assertEqual(mao.rotulo_tipo, "Mão de obra")
        self.assertEqual(peca.quantidade_formatada, "2.00")
        self.assertEqual(mao.quantidade_formatada, "1.50 h")
        self.assertEqual(peca.quantidade_documento, "2")
        self.assertEqual(mao.quantidade_documento, "1.5 h")
        self.assertIsNone(peca.base_comissao)
        self.assertEqual(mao.base_comissao, Decimal("180.00"))
        self.assertIs(mao.executor, mecanico)
        self.assertIn("Filtro", peca.descrever())

    def test_tipo_item_invalido(self):
        with self.assertRaises(ValidacaoError):
            TipoItem.from_value("SERVICO")
        self.assertIs(TipoItem.from_value("peca"), TipoItem.PECA)

    def test_quilometragem_nao_diminui(self):
        _, _, veiculo = base()
        veiculo.atualizar_km(63000)
        self.assertEqual(veiculo.km, 63000)
        with self.assertRaises(ValidacaoError):
            veiculo.atualizar_km(62000)


class TestOrdemServico(unittest.TestCase):
    def test_totais_e_desconto(self):
        cliente, mecanico, veiculo = base()
        ordem = os_exemplo(cliente, mecanico, veiculo)
        self.assertEqual(ordem.quantidade_itens, 7)
        self.assertEqual(ordem.subtotal, Decimal("1240.00"))
        self.assertEqual(ordem.subtotal_pecas, Decimal("760.00"))
        self.assertEqual(ordem.subtotal_mao_obra, Decimal("480.00"))
        self.assertEqual(ordem.total, Decimal("1240.00"))
        ordem.aplicar_desconto(40)
        self.assertEqual(ordem.total, Decimal("1200.00"))
        with self.assertRaises(RegraNegocioError):
            ordem.aplicar_desconto(1300)

    def test_nao_aprova_sem_itens(self):
        cliente, mecanico, veiculo = base()
        ordem = OrdemServico("2026-0001", cliente, veiculo, mecanico)
        with self.assertRaises(RegraNegocioError):
            ordem.aprovar()

    def test_ciclo_completo_e_historico(self):
        cliente, mecanico, veiculo = base()
        ordem = os_exemplo(cliente, mecanico, veiculo)
        ordem.aprovar("teste", data_hora=datetime(2026, 10, 24, 10, 0))
        self.assertEqual(ordem.status, StatusOS.APROVADA)
        ordem.iniciar("teste", data_hora=datetime(2026, 10, 24, 11, 0))
        self.assertEqual(ordem.status, StatusOS.EM_EXECUCAO)
        ordem.finalizar(
            62500,
            "teste",
            data_hora=datetime(2026, 10, 25, 9, 0),
        )
        self.assertEqual(ordem.status, StatusOS.FINALIZADA)
        self.assertEqual(veiculo.km, 62500)
        self.assertEqual(len(ordem.historico), 4)
        self.assertEqual(ordem.historico[-1].status_novo, StatusOS.FINALIZADA)
        self.assertIsNotNone(ordem.data_finalizacao)
        with self.assertRaises(TransicaoInvalida):
            ordem.iniciar()

    def test_nao_altera_itens_fora_de_orcamento(self):
        cliente, mecanico, veiculo = base()
        ordem = os_exemplo(cliente, mecanico, veiculo)
        ordem.aprovar()
        with self.assertRaises(RegraNegocioError):
            ordem.adicionar_item(Peca("Novo", 1, 10))
        with self.assertRaises(RegraNegocioError):
            ordem.aplicar_desconto(10)

    def test_cancelamento_exige_motivo(self):
        cliente, mecanico, veiculo = base()
        ordem = os_exemplo(cliente, mecanico, veiculo)
        with self.assertRaises(ValidacaoError):
            ordem.cancelar("")
        ordem.cancelar("Cliente desistiu", "teste")
        self.assertEqual(ordem.status, StatusOS.CANCELADA)
        self.assertEqual(ordem.motivo_cancelamento, "Cliente desistiu")

    def test_transicao_invalida(self):
        cliente, mecanico, veiculo = base()
        ordem = os_exemplo(cliente, mecanico, veiculo)
        with self.assertRaises(TransicaoInvalida):
            ordem.iniciar()

    def test_oficina_emite_numeros_unicos(self):
        cliente, mecanico, veiculo = base()
        oficina = Oficina("DevSolo Studio", "12.345.678/0001-90")
        primeira = oficina.emitir_ordem_servico(
            cliente, veiculo, mecanico, data_abertura=datetime(2026, 10, 26)
        )
        segunda = oficina.emitir_ordem_servico(
            cliente, veiculo, mecanico, data_abertura=datetime(2026, 10, 26)
        )
        self.assertEqual(primeira.numero, "2026-0001")
        self.assertEqual(segunda.numero, "2026-0002")

    def test_encapsulamento_do_total(self):
        cliente, mecanico, veiculo = base()
        ordem = os_exemplo(cliente, mecanico, veiculo)
        with self.assertRaises(AttributeError):
            ordem.total = Decimal("1.00")


if __name__ == "__main__":
    unittest.main()
