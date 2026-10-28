"""Item de peça."""

from __future__ import annotations

from decimal import Decimal

from .item_os import ItemOS
from .validators import formatar_brl


class Peca(ItemOS):
    def __init__(
        self,
        descricao: str,
        quantidade: Decimal | int | float | str,
        valor_unitario: Decimal | int | float | str,
        codigo: str | None = None,
        fornecedor: str | None = None,
    ) -> None:
        super().__init__(descricao, quantidade, valor_unitario)
        self._codigo = (codigo or "").strip()
        self._fornecedor = (fornecedor or "").strip()

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def fornecedor(self) -> str:
        return self._fornecedor

    def calcular_subtotal(self) -> Decimal:
        return (self.quantidade * self.valor_unitario).quantize(Decimal("0.01"))

    def tipo(self) -> str:
        return "PECA"

    def descrever(self) -> str:
        return (
            f"Peça: {self.descricao} ({self.quantidade} × "
            f"{formatar_brl(self.valor_unitario)}) — {formatar_brl(self.subtotal)}"
        )
