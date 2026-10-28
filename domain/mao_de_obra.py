"""Item de mão de obra."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from .item_os import ItemOS
from .validators import decimal_valor, formatar_brl

if TYPE_CHECKING:
    from .mecanico import Mecanico


class MaoDeObra(ItemOS):
    def __init__(
        self,
        descricao: str,
        horas: Decimal | int | float | str,
        taxa_horaria: Decimal | int | float | str,
        mecanico: "Mecanico | None" = None,
    ) -> None:
        taxa = decimal_valor(taxa_horaria, "Taxa horária", minimo=Decimal("0"))
        super().__init__(descricao, Decimal("1"), taxa)
        self._horas = decimal_valor(
            horas, "Horas", minimo=Decimal("0.01"), casas="0.01"
        )
        self._taxa_horaria = taxa
        self._mecanico = mecanico

    @property
    def horas(self) -> Decimal:
        return self._horas

    @property
    def taxa_horaria(self) -> Decimal:
        return self._taxa_horaria

    @property
    def mecanico(self) -> "Mecanico | None":
        return self._mecanico

    @property
    def executor(self) -> "Mecanico | None":
        return self._mecanico

    def calcular_subtotal(self) -> Decimal:
        return (self._horas * self._taxa_horaria).quantize(Decimal("0.01"))

    def tipo(self) -> str:
        return "MAO_DE_OBRA"

    def descrever(self) -> str:
        executor = f" • {self._mecanico.nome}" if self._mecanico else ""
        return (
            f"Mão de obra: {self.descricao} ({self._horas} h × "
            f"{formatar_brl(self._taxa_horaria)}){executor} — "
            f"{formatar_brl(self.subtotal)}"
        )
