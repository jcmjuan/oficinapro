"""Repositório de configurações chave-valor."""

from __future__ import annotations

from ..database import Database


class ConfiguracaoRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def obter(self, chave: str, padrao: str | None = None) -> str | None:
        linha = self.db.buscar_um(
            "SELECT valor FROM configuracao WHERE chave = ?", (chave,)
        )
        return linha["valor"] if linha else padrao

    def definir(self, chave: str, valor: str) -> None:
        with self.db.transacao() as conn:
            conn.execute(
                """
                INSERT INTO configuracao (chave, valor, atualizado_em)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(chave) DO UPDATE SET
                    valor = excluded.valor,
                    atualizado_em = CURRENT_TIMESTAMP
                """,
                (chave, str(valor)),
            )

    def todas(self) -> dict[str, str]:
        return {
            linha["chave"]: linha["valor"]
            for linha in self.db.buscar_todos(
                "SELECT chave, valor FROM configuracao ORDER BY chave"
            )
        }

    def remover(self, chave: str) -> None:
        with self.db.transacao() as conn:
            conn.execute("DELETE FROM configuracao WHERE chave = ?", (chave,))
