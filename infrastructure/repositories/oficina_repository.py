"""Repositório da configuração da oficina."""

from __future__ import annotations

import sqlite3

from domain.exceptions import DuplicadoError, NaoEncontradoError
from domain.oficina import Oficina

from ..database import Database


class OficinaRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def salvar(self, oficina: Oficina) -> Oficina:
        try:
            with self.db.transacao() as conn:
                if oficina.id is None:
                    linha = conn.execute(
                        "SELECT id FROM oficina WHERE cnpj = ?", (oficina.documento,)
                    ).fetchone()
                    if linha:
                        oficina.id = int(linha["id"])
                if oficina.id is None:
                    cursor = conn.execute(
                        """
                        INSERT INTO oficina
                            (nome, cnpj, telefone, endereco,
                             taxa_horaria_padrao, comissao_padrao)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            oficina.nome,
                            oficina.documento,
                            oficina.telefone,
                            oficina.endereco,
                            str(oficina.taxa_horaria_padrao),
                            str(oficina.comissao_padrao),
                        ),
                    )
                    oficina.id = int(cursor.lastrowid)
                else:
                    conn.execute(
                        """
                        UPDATE oficina SET
                            nome = ?, cnpj = ?, telefone = ?, endereco = ?,
                            taxa_horaria_padrao = ?, comissao_padrao = ?,
                            atualizado_em = CURRENT_TIMESTAMP
                        WHERE id = ?
                        """,
                        (
                            oficina.nome,
                            oficina.documento,
                            oficina.telefone,
                            oficina.endereco,
                            str(oficina.taxa_horaria_padrao),
                            str(oficina.comissao_padrao),
                            oficina.id,
                        ),
                    )
        except sqlite3.IntegrityError as exc:
            raise DuplicadoError(
                f"Já existe oficina com o CNPJ {oficina.cnpj}."
            ) from exc
        return oficina

    def obter(self) -> Oficina:
        linha = self.db.buscar_um("SELECT * FROM oficina ORDER BY id LIMIT 1")
        if linha is None:
            raise NaoEncontradoError("Oficina não configurada.")
        oficina = Oficina(
            linha["nome"],
            linha["cnpj"],
            telefone=linha["telefone"],
            endereco=linha["endereco"],
            taxa_horaria_padrao=linha["taxa_horaria_padrao"],
            comissao_padrao=linha["comissao_padrao"],
        )
        oficina.id = int(linha["id"])
        return oficina
