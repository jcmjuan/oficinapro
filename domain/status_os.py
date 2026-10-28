"""Enumeração do ciclo de vida da ordem de serviço."""

from __future__ import annotations

from enum import Enum

from .exceptions import ValidacaoError


class StatusOS(str, Enum):
    ORCAMENTO = "ORCAMENTO"
    APROVADA = "APROVADA"
    EM_EXECUCAO = "EM_EXECUCAO"
    FINALIZADA = "FINALIZADA"
    CANCELADA = "CANCELADA"

    @classmethod
    def from_value(cls, valor: "StatusOS | str") -> "StatusOS":
        if isinstance(valor, cls):
            return valor
        try:
            return cls(str(valor).strip().upper())
        except ValueError as exc:
            raise ValidacaoError(f"Status inválido: {valor}") from exc

    @property
    def rotulo(self) -> str:
        return {
            StatusOS.ORCAMENTO: "Orçamento",
            StatusOS.APROVADA: "Aprovada",
            StatusOS.EM_EXECUCAO: "Em execução",
            StatusOS.FINALIZADA: "Finalizada",
            StatusOS.CANCELADA: "Cancelada",
        }[self]

    @property
    def terminal(self) -> bool:
        return self in (StatusOS.FINALIZADA, StatusOS.CANCELADA)
