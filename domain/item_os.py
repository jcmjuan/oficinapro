"""Contrato base para itens de uma ordem de serviço."""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal

from .validators import decimal_valor, formatar_brl, texto_obrigatorio


class ItemOS(ABC):
    def __init__(
        self,
        descricao: str,
        quantidade: Decimal | int | float | str = Decimal("1"),
        valor_unitario: Decimal | int | float | str = Decimal("0.00"),
    ) -> None:
        self._id: int | None = None
        self._descricao = texto_obrigatorio(descricao, "Descrição", 2)
        self._quantidade = decimal_valor(
            quantidade, "Quantidade", minimo=Decimal("0.01"), casas="0.01"
        )
        self._valor_unitario = decimal_valor(
            valor_unitario, "Valor unitário", minimo=Decimal("0"), casas="0.01"
        )

    @property
    def id(self) -> int | None:
        return self._id

    @id.setter
    def id(self, valor: int | None) -> None:
        self._id = valor

    @property
    def descricao(self) -> str:
        return self._descricao

    @property
    def quantidade(self) -> Decimal:
        return self._quantidade

    @property
    def valor_unitario(self) -> Decimal:
        return self._valor_unitario

    @abstractmethod
    def calcular_subtotal(self) -> Decimal:
        """Calcula o subtotal conforme o tipo concreto."""

    @abstractmethod
    def tipo(self) -> str:
        """Identifica o tipo do item para persistência e exibição."""

    @property
    def subtotal(self) -> Decimal:
        return self.calcular_subtotal()

    def descrever(self) -> str:
        return f"{self._descricao} — {formatar_brl(self.subtotal)}"

    def __str__(self) -> str:
        return self.descrever()
