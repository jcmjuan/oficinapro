"""Enumeração dos tipos de item de uma ordem de serviço."""

from __future__ import annotations

from enum import Enum

from .exceptions import ValidacaoError


class TipoItem(str, Enum):
    PECA = "PECA"
    MAO_DE_OBRA = "MAO_DE_OBRA"

    @classmethod
    def from_value(cls, valor: "TipoItem | str") -> "TipoItem":
        if isinstance(valor, cls):
            return valor
        try:
            return cls(str(valor).strip().upper())
        except ValueError as exc:
            raise ValidacaoError(f"Tipo de item inválido: {valor}") from exc

    @property
    def rotulo(self) -> str:
        return {
            TipoItem.PECA: "Peça",
            TipoItem.MAO_DE_OBRA: "Mão de obra",
        }[self]
