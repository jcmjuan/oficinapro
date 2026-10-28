"""Conexão e utilidades de banco de dados SQLite."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .migrations import migrate


class Database:
    """Encapsula a conexão SQLite e o ciclo de vida do banco."""

    def __init__(self, caminho: str | Path) -> None:
        self.caminho = Path(caminho) if str(caminho) != ":memory:" else None
        if self.caminho is not None:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(
            str(caminho),
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        self._configurar()
        migrate(self.conn)

    def _configurar(self) -> None:
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA busy_timeout = 5000")
        try:
            self.conn.execute("PRAGMA journal_mode = WAL")
        except sqlite3.DatabaseError:
            # Bancos em memória ou sistemas de arquivos restritos podem não
            # suportar WAL; o modo padrão continua funcional.
            pass

    def reabrir(self) -> None:
        if self.caminho is None:
            raise RuntimeError("Não é possível reabrir um banco em memória.")
        self.conn.close()
        self.conn = sqlite3.connect(
            str(self.caminho),
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        self._configurar()
        migrate(self.conn)

    @contextmanager
    def transacao(self) -> Iterator[sqlite3.Connection]:
        try:
            yield self.conn
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def executar(self, sql: str, parametros: tuple = ()) -> sqlite3.Cursor:
        return self.conn.execute(sql, parametros)

    def buscar_um(self, sql: str, parametros: tuple = ()) -> sqlite3.Row | None:
        return self.conn.execute(sql, parametros).fetchone()

    def buscar_todos(self, sql: str, parametros: tuple = ()) -> list[sqlite3.Row]:
        return list(self.conn.execute(sql, parametros).fetchall())

    def backup(self, destino: str | Path) -> Path:
        destino = Path(destino)
        destino.parent.mkdir(parents=True, exist_ok=True)
        if destino.exists():
            raise FileExistsError(f"O arquivo de backup já existe: {destino}")
        self.conn.commit()
        self.conn.execute("VACUUM INTO ?", (str(destino),))
        return destino

    def integridade(self) -> str:
        linha = self.conn.execute("PRAGMA integrity_check").fetchone()
        return str(linha[0]) if linha else "unknown"

    def fechar(self) -> None:
        self.conn.close()

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.fechar()
