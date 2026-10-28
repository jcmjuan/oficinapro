"""Repositório de mecânicos."""

from __future__ import annotations

import sqlite3

from domain.exceptions import DuplicadoError, NaoEncontradoError
from domain.mecanico import Mecanico

from ..database import Database
from .mappers import mecanico_de_row


class MecanicoRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def salvar(self, mecanico: Mecanico) -> Mecanico:
        try:
            with self.db.transacao() as conn:
                if mecanico.id is None:
                    cursor = conn.execute(
                        """
                        INSERT INTO mecanico
                            (nome, telefone, email, registro, taxa_comissao,
                             especialidade, ativo)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            mecanico.nome,
                            mecanico.telefone,
                            mecanico.email,
                            mecanico.registro,
                            str(mecanico.taxa_comissao),
                            mecanico.especialidade,
                            1 if mecanico.ativo else 0,
                        ),
                    )
                    mecanico.id = int(cursor.lastrowid)
                else:
                    conn.execute(
                        """
                        UPDATE mecanico SET
                            nome = ?, telefone = ?, email = ?, registro = ?,
                            taxa_comissao = ?, especialidade = ?, ativo = ?,
                            atualizado_em = CURRENT_TIMESTAMP
                        WHERE id = ?
                        """,
                        (
                            mecanico.nome,
                            mecanico.telefone,
                            mecanico.email,
                            mecanico.registro,
                            str(mecanico.taxa_comissao),
                            mecanico.especialidade,
                            1 if mecanico.ativo else 0,
                            mecanico.id,
                        ),
                    )
        except sqlite3.IntegrityError as exc:
            raise DuplicadoError(
                f"Já existe mecânico com o registro {mecanico.registro}."
            ) from exc
        return mecanico

    def buscar_por_id(self, mecanico_id: int) -> Mecanico:
        linha = self.db.buscar_um("SELECT * FROM mecanico WHERE id = ?", (mecanico_id,))
        if linha is None:
            raise NaoEncontradoError(f"Mecânico {mecanico_id} não encontrado.")
        return mecanico_de_row(linha)

    def buscar_por_registro(self, registro: str) -> Mecanico | None:
        linha = self.db.buscar_um(
            "SELECT * FROM mecanico WHERE registro = ?", (registro.strip().upper(),)
        )
        return mecanico_de_row(linha) if linha else None

    def listar(self, *, apenas_ativos: bool = True) -> list[Mecanico]:
        sql = "SELECT * FROM mecanico"
        if apenas_ativos:
            sql += " WHERE ativo = 1"
        sql += " ORDER BY nome COLLATE NOCASE"
        return [mecanico_de_row(linha) for linha in self.db.buscar_todos(sql)]

    def inativar(self, mecanico_id: int) -> None:
        with self.db.transacao() as conn:
            cursor = conn.execute(
                "UPDATE mecanico SET ativo = 0, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?",
                (mecanico_id,),
            )
            if cursor.rowcount == 0:
                raise NaoEncontradoError(f"Mecânico {mecanico_id} não encontrado.")

    def reativar(self, mecanico_id: int) -> None:
        with self.db.transacao() as conn:
            cursor = conn.execute(
                "UPDATE mecanico SET ativo = 1, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?",
                (mecanico_id,),
            )
            if cursor.rowcount == 0:
                raise NaoEncontradoError(f"Mecânico {mecanico_id} não encontrado.")

    def contar(self, *, apenas_ativos: bool = True) -> int:
        sql = "SELECT COUNT(*) FROM mecanico"
        if apenas_ativos:
            sql += " WHERE ativo = 1"
        return int(self.db.buscar_um(sql)[0])
