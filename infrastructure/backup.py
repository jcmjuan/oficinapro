"""Backup e restauração do banco SQLite."""

from __future__ import annotations

import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

from domain.exceptions import OficinaProError

from .database import Database


class BackupService:
    def __init__(self, db: Database) -> None:
        self.db = db

    def fazer_backup(self, destino: str | Path | None = None) -> Path:
        if destino is None:
            pasta = Path("backups")
            pasta.mkdir(parents=True, exist_ok=True)
            carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
            destino = pasta / f"oficinapro_{carimbo}.db"
        return self.db.backup(destino)

    @staticmethod
    def validar(caminho: str | Path) -> str:
        caminho = Path(caminho)
        if not caminho.exists():
            raise OficinaProError(f"Backup não encontrado: {caminho}")
        conn = sqlite3.connect(str(caminho))
        try:
            resultado = conn.execute("PRAGMA integrity_check").fetchone()
        finally:
            conn.close()
        status = str(resultado[0]) if resultado else "unknown"
        if status != "ok":
            raise OficinaProError(f"Backup inválido: {status}")
        return status

    def restaurar(self, origem: str | Path) -> Path:
        if self.db.caminho is None:
            raise OficinaProError("Não é possível restaurar um banco em memória.")
        origem = Path(origem)
        self.validar(origem)
        self.db.conn.close()
        shutil.copy2(origem, self.db.caminho)
        for sufixo in ("-wal", "-shm"):
            extra = Path(str(self.db.caminho) + sufixo)
            if extra.exists():
                extra.unlink()
        self.db.reabrir()
        return self.db.caminho
