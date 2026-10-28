"""Registro imutável de transição de status."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .status_os import StatusOS


@dataclass(frozen=True)
class StatusHistorico:
    status_anterior: StatusOS | None
    status_novo: StatusOS
    data_hora: datetime
    usuario: str = ""
    motivo: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status_novo", StatusOS.from_value(self.status_novo))
        if self.status_anterior is not None:
            object.__setattr__(
                self, "status_anterior", StatusOS.from_value(self.status_anterior)
            )
        if not isinstance(self.data_hora, datetime):
            raise TypeError("data_hora deve ser datetime.")

    def descricao(self) -> str:
        anterior = self.status_anterior.rotulo if self.status_anterior else "—"
        return (
            f"{anterior} → {self.status_novo.rotulo} em "
            f"{self.data_hora:%d/%m/%Y %H:%M}"
        )
