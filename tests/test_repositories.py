"""Testes de persistência SQLite e backup."""

from __future__ import annotations

import os
import tempfile
import unittest
from datetime import datetime
from decimal import Decimal

from domain.cliente import Cliente
from domain.exceptions import DuplicadoError
from domain.mao_de_obra import MaoDeObra
from domain.mecanico import Mecanico
from domain.ordem_servico import OrdemServico
from domain.peca import Peca
from domain.status_os import StatusOS
from domain.veiculo import Veiculo

from infrastructure.backup import BackupService
from infrastructure.database import Database
from infrastructure.repositories.cliente_repository import ClienteRepository
from infrastructure.repositories.mecanico_repository import MecanicoRepository
from infrastructure.repositories.ordem_servico_repository import OrdemServicoRepository
from infrastructure.repositories.veiculo_repository import VeiculoRepository


class TestRepositories(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self.tmp.name, "teste.db"))
        self.clientes = ClienteRepository(self.db)
        self.mecanicos = MecanicoRepository(self.db)
        self.veiculos = VeiculoRepository(self.db)
        self.ordens = OrdemServicoRepository(self.db)

    def tearDown(self):
        self.db.fechar()
        self.tmp.cleanup()

    def _base(self):
        cliente = self.clientes.salvar(
            Cliente("Ana Paula Ribeiro", "(11) 98765-4321", "123.456.789-00")
        )
        mecanico = self.mecanicos.salvar(
            Mecanico("Marcos Silva", "(11) 98888-7777", "MEC-001", Decimal("0.12"))
        )
        veiculo = self.veiculos.salvar(
            Veiculo("ABC-1D23", "Honda", "Civic", 2019, 62480, cliente)
        )
        return cliente, mecanico, veiculo

    def test_cliente_crud_e_duplicidade(self):
        cliente = self.clientes.salvar(
            Cliente("Ana Paula Ribeiro", "(11) 98765-4321", "123.456.789-00")
        )
        self.assertIsNotNone(cliente.id)
        self.assertEqual(self.clientes.contar(), 1)
        encontrado = self.clientes.buscar_por_id(cliente.id)
        self.assertEqual(encontrado.nome, "Ana Paula Ribeiro")
        self.assertEqual(encontrado.cpf_cnpj, "123.456.789-00")
        self.assertEqual(self.clientes.buscar_por_documento("123.456.789-00").id, cliente.id)
        self.assertEqual(len(self.clientes.listar("Ana")), 1)
        with self.assertRaises(DuplicadoError):
            self.clientes.salvar(
                Cliente("Outra Ana", "(11) 90000-0000", "123.456.789-00")
            )

    def test_veiculo_crud_e_duplicidade(self):
        cliente, _, veiculo = self._base()
        self.assertIsNotNone(veiculo.id)
        encontrado = self.veiculos.buscar_por_placa("abc1d23")
        self.assertEqual(encontrado.id, veiculo.id)
        self.assertEqual(encontrado.cliente.id, cliente.id)
        self.assertEqual(len(self.veiculos.listar(cliente_id=cliente.id)), 1)
        self.veiculos.atualizar_km(veiculo.id, 63000)
        self.assertEqual(self.veiculos.buscar_por_id(veiculo.id).km, 63000)
        with self.assertRaises(DuplicadoError):
            self.veiculos.salvar(
                Veiculo("ABC-1D23", "Honda", "Fit", 2020, 1000, cliente)
            )

    def test_ordem_servico_roundtrip(self):
        cliente, mecanico, veiculo = self._base()
        ordem = OrdemServico(
            "2026-0042",
            cliente,
            veiculo,
            mecanico,
            data_abertura=datetime(2026, 10, 24, 9, 30),
            observacoes="Revisão completa",
        )
        ordem.adicionar_item(Peca("Filtro de óleo", 1, 45))
        ordem.adicionar_item(MaoDeObra("Troca de óleo", Decimal("1.5"), 120, mecanico))
        self.ordens.salvar(ordem)
        carregada = self.ordens.buscar_por_numero("2026-0042")
        self.assertIsNotNone(carregada)
        self.assertEqual(carregada.total, Decimal("225.00"))
        self.assertEqual(carregada.quantidade_itens, 2)
        self.assertEqual(len(carregada.historico), 1)
        self.assertEqual(carregada.observacoes, "Revisão completa")
        self.assertIsInstance(carregada.itens[0], Peca)
        self.assertIsInstance(carregada.itens[1], MaoDeObra)
        self.assertEqual(self.ordens.proximo_numero(2026), "2026-0043")
        self.assertEqual(len(self.ordens.listar(status=StatusOS.ORCAMENTO)), 1)
        self.assertEqual(self.ordens.contar_por_status()["ORCAMENTO"], 1)

    def test_historico_append_only(self):
        cliente, mecanico, veiculo = self._base()
        ordem = OrdemServico("2026-0042", cliente, veiculo, mecanico)
        ordem.adicionar_item(Peca("Filtro", 1, 45))
        self.ordens.salvar(ordem)
        ordem.aprovar("teste", data_hora=datetime(2026, 10, 24, 10, 0))
        self.ordens.salvar(ordem)
        self.ordens.salvar(ordem)
        carregada = self.ordens.obter("2026-0042")
        self.assertEqual(len(carregada.historico), 2)
        linhas = self.db.buscar_todos(
            "SELECT * FROM status_historico WHERE ordem_servico_id = ?", (ordem.id,)
        )
        self.assertEqual(len(linhas), 2)

    def test_backup_e_restauracao(self):
        self._base()
        backup = os.path.join(self.tmp.name, "backup.db")
        BackupService(self.db).fazer_backup(backup)
        self.clientes.salvar(
            Cliente("Carlos Lima", "(11) 97654-3210", "234.567.890-11")
        )
        self.assertEqual(self.clientes.contar(), 2)
        BackupService(self.db).restaurar(backup)
        self.assertEqual(self.clientes.contar(), 1)


if __name__ == "__main__":
    unittest.main()
