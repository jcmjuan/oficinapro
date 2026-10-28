"""Mecânico da oficina."""

from __future__ import annotations

from decimal import Decimal

from .pessoa import Pessoa
from .validators import decimal_valor, texto_obrigatorio


class Mecanico(Pessoa):
    def __init__(
        self,
        nome: str,
        telefone: str,
        registro: str,
        taxa_comissao: Decimal | int | float | str = Decimal("0.10"),
        *,
        email: str | None = None,
        especialidade: str | None = None,
        ativo: bool = True,
    ) -> None:
        super().__init__(nome, telefone, email)
        self._registro = texto_obrigatorio(registro, "Registro", 2).upper()
        self._taxa_comissao = decimal_valor(
            taxa_comissao,
            "Taxa de comissão",
            minimo=Decimal("0"),
            maximo=Decimal("1"),
            casas="0.0001",
        )
        self._especialidade = (especialidade or "").strip()
        self._ativo = bool(ativo)

    @property
    def registro(self) -> str:
        return self._registro

    @property
    def taxa_comissao(self) -> Decimal:
        return self._taxa_comissao

    @property
    def especialidade(self) -> str:
        return self._especialidade

    @property
    def ativo(self) -> bool:
        return self._ativo

    def calcular_comissao(self, base_mao_obra: Decimal | int | float | str) -> Decimal:
        base = decimal_valor(base_mao_obra, "Base de mão de obra", minimo=Decimal("0"))
        return (base * self._taxa_comissao).quantize(Decimal("0.01"))

    def atualizar_dados(
        self,
        *,
        nome: str | None = None,
        telefone: str | None = None,
        email: str | None = None,
        registro: str | None = None,
        taxa_comissao: Decimal | int | float | str | None = None,
        especialidade: str | None = None,
    ) -> None:
        """Atualiza os dados cadastrais do mecânico."""
        self.atualizar_contato(nome=nome, telefone=telefone, email=email)
        if registro is not None:
            self._registro = texto_obrigatorio(registro, "Registro", 2).upper()
        if taxa_comissao is not None:
            self._taxa_comissao = decimal_valor(
                taxa_comissao,
                "Taxa de comissão",
                minimo=Decimal("0"),
                maximo=Decimal("1"),
                casas="0.0001",
            )
        if especialidade is not None:
            self._especialidade = especialidade.strip()

    def inativar(self) -> None:
        self._ativo = False

    def reativar(self) -> None:
        self._ativo = True

    def tipo(self) -> str:
        return "Mecanico"

    def __repr__(self) -> str:
        return f"Mecanico(id={self.id!r}, nome={self.nome!r}, registro={self.registro!r})"
