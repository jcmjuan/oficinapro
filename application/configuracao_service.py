"""Serviço de configuração, backup e restauração."""

from __future__ import annotations

from pathlib import Path

from domain.oficina import Oficina

from infrastructure.backup import BackupService
from infrastructure.database import Database
from infrastructure.repositories.configuracao_repository import ConfiguracaoRepository
from infrastructure.repositories.oficina_repository import OficinaRepository


class ConfiguracaoService:
    def __init__(
        self,
        config_repo: ConfiguracaoRepository,
        oficina_repo: OficinaRepository,
        db: Database,
    ) -> None:
        self.config = config_repo
        self.oficinas = oficina_repo
        self.db = db
        self.backup = BackupService(db)

    def obter(self, chave: str, padrao: str | None = None) -> str | None:
        return self.config.obter(chave, padrao)

    def definir(self, chave: str, valor: str) -> None:
        self.config.definir(chave, valor)

    def todas(self) -> dict[str, str]:
        return self.config.todas()

    def obter_oficina(self) -> Oficina:
        return self.oficinas.obter()

    def salvar_oficina(self, oficina: Oficina) -> Oficina:
        return self.oficinas.salvar(oficina)

    def fazer_backup(self, destino: str | Path | None = None) -> Path:
        return self.backup.fazer_backup(destino)

    def restaurar_backup(self, origem: str | Path) -> Path:
        return self.backup.restaurar(origem)
