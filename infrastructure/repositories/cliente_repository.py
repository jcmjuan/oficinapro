"""Repositório de clientes."""

from __future__ import annotations

import re
import sqlite3

from domain.cliente import Cliente
from domain.exceptions import DuplicadoError, NaoEncontradoError

from ..database import Database
from .mappers import cliente_de_row, veiculo_de_row


class ClienteRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def _carregar_veiculos(self, cliente: Cliente) -> None:
        if cliente.id is None:
            return
        linhas = self.db.buscar_todos(
            "SELECT * FROM veiculo WHERE cliente_id = ? ORDER BY placa",
            (cliente.id,),
        )
        for linha in linhas:
            veiculo_de_row(linha, cliente)

    def salvar(self, cliente: Cliente) -> Cliente:
        try:
            with self.db.transacao() as conn:
                if cliente.id is None:
                    cursor = conn.execute(
                        """
                        INSERT INTO cliente
                            (nome, cpf_cnpj, telefone, email, endereco,
                             data_nascimento, observacoes, ativo)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            cliente.nome,
                            cliente.documento,
                            cliente.telefone,
                            cliente.email,
                            cliente.endereco,
                            cliente.data_nascimento.isoformat()
                            if cliente.data_nascimento
                            else None,
                            cliente.observacoes,
                            1 if cliente.ativo else 0,
                        ),
                    )
                    cliente.id = int(cursor.lastrowid)
                else:
                    conn.execute(
                        """
                        UPDATE cliente SET
                            nome = ?, cpf_cnpj = ?, telefone = ?, email = ?,
                            endereco = ?, data_nascimento = ?, observacoes = ?,
                            ativo = ?, atualizado_em = CURRENT_TIMESTAMP
                        WHERE id = ?
                        """,
                        (
                            cliente.nome,
                            cliente.documento,
                            cliente.telefone,
                            cliente.email,
                            cliente.endereco,
                            cliente.data_nascimento.isoformat()
                            if cliente.data_nascimento
                            else None,
                            cliente.observacoes,
                            1 if cliente.ativo else 0,
                            cliente.id,
                        ),
                    )
        except sqlite3.IntegrityError as exc:
            raise DuplicadoError(
                f"Já existe cliente com o CPF/CNPJ {cliente.cpf_cnpj}."
            ) from exc
        return cliente

    def buscar_por_id(self, cliente_id: int) -> Cliente:
        linha = self.db.buscar_um("SELECT * FROM cliente WHERE id = ?", (cliente_id,))
        if linha is None:
            raise NaoEncontradoError(f"Cliente {cliente_id} não encontrado.")
        cliente = cliente_de_row(linha)
        self._carregar_veiculos(cliente)
        return cliente

    def buscar_por_documento(self, documento: str) -> Cliente | None:
        digitos = re.sub(r"\D", "", documento)
        linha = self.db.buscar_um(
            "SELECT * FROM cliente WHERE cpf_cnpj = ?", (digitos,)
        )
        if linha is None:
            return None
        cliente = cliente_de_row(linha)
        self._carregar_veiculos(cliente)
        return cliente

    def listar(self, busca: str = "", *, apenas_ativos: bool = True) -> list[Cliente]:
        sql = "SELECT * FROM cliente"
        condicoes = []
        parametros: list = []
        if apenas_ativos:
            condicoes.append("ativo = 1")
        if busca.strip():
            termo = f"%{busca.strip()}%"
            digitos = re.sub(r"\D", "", busca)
            if digitos:
                condicoes.append("(nome LIKE ? OR cpf_cnpj LIKE ? OR telefone LIKE ? OR email LIKE ?)")
                parametros.extend([termo, f"%{digitos}%", termo, termo])
            else:
                condicoes.append("(nome LIKE ? OR telefone LIKE ? OR email LIKE ?)")
                parametros.extend([termo, termo, termo])
        if condicoes:
            sql += " WHERE " + " AND ".join(condicoes)
        sql += " ORDER BY nome COLLATE NOCASE"
        clientes = []
        for linha in self.db.buscar_todos(sql, tuple(parametros)):
            cliente = cliente_de_row(linha)
            self._carregar_veiculos(cliente)
            clientes.append(cliente)
        return clientes

    def inativar(self, cliente_id: int) -> None:
        with self.db.transacao() as conn:
            cursor = conn.execute(
                "UPDATE cliente SET ativo = 0, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?",
                (cliente_id,),
            )
            if cursor.rowcount == 0:
                raise NaoEncontradoError(f"Cliente {cliente_id} não encontrado.")

    def reativar(self, cliente_id: int) -> None:
        with self.db.transacao() as conn:
            cursor = conn.execute(
                "UPDATE cliente SET ativo = 1, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?",
                (cliente_id,),
            )
            if cursor.rowcount == 0:
                raise NaoEncontradoError(f"Cliente {cliente_id} não encontrado.")

    def contar(self, *, apenas_ativos: bool = True) -> int:
        sql = "SELECT COUNT(*) FROM cliente"
        if apenas_ativos:
            sql += " WHERE ativo = 1"
        return int(self.db.buscar_um(sql)[0])
