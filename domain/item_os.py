"""Contrato base para itens de uma ordem de serviço."""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import TYPE_CHECKING

from .tipo_item import TipoItem
from .validators import decimal_valor, formatar_brl, texto_obrigatorio

if TYPE_CHECKING:
    from .mecanico import Mecanico


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
    def tipo(self) -> TipoItem:
        """Identifica o tipo do item para persistência e exibição."""

    @property
    @abstractmethod
    def quantidade_calculo(self) -> Decimal:
        """Quantidade efetiva do item (unidades ou horas)."""

    @property
    @abstractmethod
    def unidade(self) -> str:
        """Unidade exibida ao lado da quantidade (vazia para peças)."""

    @property
    def quantidade_formatada(self) -> str:
        """Quantidade com unidade, como exibida na interface."""
        return f"{self.quantidade_calculo:g} {self.unidade}".strip()

    @property
    def quantidade_documento(self) -> str:
        """Quantidade compacta, sem zeros à direita, usada nos documentos."""
        texto = f"{self.quantidade_calculo:.2f}".rstrip("0").rstrip(".")
        return f"{texto} {self.unidade}".strip()

    @property
    def rotulo_tipo(self) -> str:
        """Rótulo legível do tipo do item."""
        return self.tipo().rotulo

    @property
    def detalhe(self) -> str:
        """Informação complementar para exibição (código, fornecedor, executor)."""
        return ""

    @property
    def executor(self) -> "Mecanico | None":
        """Mecânico responsável pelo item, quando houver."""
        return None

    @property
    def base_comissao(self) -> Decimal | None:
        """Valor que gera comissão; ``None`` quando o item não gera comissão."""
        return None

    @property
    def subtotal(self) -> Decimal:
        return self.calcular_subtotal()

    def descrever(self) -> str:
        return f"{self._descricao} — {formatar_brl(self.subtotal)}"

    def __str__(self) -> str:
        return self.descrever()
