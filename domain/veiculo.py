"""Veículo atendido pela oficina."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .exceptions import ValidacaoError
from .validators import normalizar_placa, placa_sem_formatacao, texto_obrigatorio

if TYPE_CHECKING:
    from .cliente import Cliente


class Veiculo:
    def __init__(
        self,
        placa: str,
        marca: str,
        modelo: str,
        ano: int,
        km: int = 0,
        cliente: "Cliente | None" = None,
        *,
        cor: str | None = None,
        combustivel: str | None = None,
        observacoes: str = "",
    ) -> None:
        self._id: int | None = None
        self._placa = normalizar_placa(placa)
        self._marca = texto_obrigatorio(marca, "Marca", 2)
        self._modelo = texto_obrigatorio(modelo, "Modelo", 1)
        self._ano = self._validar_ano(ano)
        self._km = self._validar_km(km)
        self._cor = (cor or "").strip()
        self._combustivel = (combustivel or "").strip()
        self._observacoes = (observacoes or "").strip()
        self._cliente: "Cliente | None" = None
        if cliente is not None:
            self.vincular_cliente(cliente)

    @staticmethod
    def _validar_ano(ano: int) -> int:
        try:
            valor = int(ano)
        except (TypeError, ValueError) as exc:
            raise ValidacaoError("Ano do veículo inválido.") from exc
        if not 1900 <= valor <= 2100:
            raise ValidacaoError("Ano do veículo deve estar entre 1900 e 2100.")
        return valor

    @staticmethod
    def _validar_km(km: int) -> int:
        try:
            valor = int(km)
        except (TypeError, ValueError) as exc:
            raise ValidacaoError("Quilometragem inválida.") from exc
        if valor < 0:
            raise ValidacaoError("Quilometragem não pode ser negativa.")
        return valor

    @property
    def id(self) -> int | None:
        return self._id

    @id.setter
    def id(self, valor: int | None) -> None:
        self._id = valor

    @property
    def placa(self) -> str:
        return self._placa

    @property
    def placa_limpa(self) -> str:
        return placa_sem_formatacao(self._placa)

    @property
    def marca(self) -> str:
        return self._marca

    @property
    def modelo(self) -> str:
        return self._modelo

    @property
    def ano(self) -> int:
        return self._ano

    @property
    def km(self) -> int:
        return self._km

    @property
    def cor(self) -> str:
        return self._cor

    @property
    def combustivel(self) -> str:
        return self._combustivel

    @property
    def observacoes(self) -> str:
        return self._observacoes

    @property
    def cliente(self) -> "Cliente | None":
        return self._cliente

    def vincular_cliente(self, cliente: "Cliente | None") -> None:
        if self._cliente is cliente:
            return
        if self._cliente is not None:
            self._cliente._remover_veiculo(self)
        self._cliente = cliente
        if cliente is not None:
            cliente._adicionar_veiculo(self)

    def atualizar_km(self, novo_km: int, *, permitir_reducao: bool = False) -> None:
        valor = self._validar_km(novo_km)
        if not permitir_reducao and valor < self._km:
            raise ValidacaoError(
                f"Quilometragem não pode diminuir de {self._km} para {valor}."
            )
        self._km = valor

    def atualizar_dados(
        self,
        *,
        marca: str | None = None,
        modelo: str | None = None,
        ano: int | None = None,
        cor: str | None = None,
        combustivel: str | None = None,
        observacoes: str | None = None,
    ) -> None:
        if marca is not None:
            self._marca = texto_obrigatorio(marca, "Marca", 2)
        if modelo is not None:
            self._modelo = texto_obrigatorio(modelo, "Modelo", 1)
        if ano is not None:
            self._ano = self._validar_ano(ano)
        if cor is not None:
            self._cor = cor.strip()
        if combustivel is not None:
            self._combustivel = combustivel.strip()
        if observacoes is not None:
            self._observacoes = observacoes.strip()

    def descricao(self) -> str:
        return f"{self._marca} {self._modelo} {self._placa} ({self._ano})"

    def __str__(self) -> str:
        return f"{self._marca} {self._modelo} • {self._placa}"

    def __repr__(self) -> str:
        return f"Veiculo(id={self.id!r}, placa={self.placa!r}, cliente={self.cliente.nome if self.cliente else None!r})"
