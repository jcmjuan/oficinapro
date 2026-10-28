"""Cliente da oficina."""

from __future__ import annotations

from datetime import date

from .pessoa import Pessoa
from .validators import formatar_documento, normalizar_documento, parse_data, texto_obrigatorio


class Cliente(Pessoa):
    def __init__(
        self,
        nome: str,
        telefone: str,
        cpf_cnpj: str,
        *,
        email: str | None = None,
        endereco: str | None = None,
        data_nascimento: date | str | None = None,
        observacoes: str = "",
        ativo: bool = True,
    ) -> None:
        super().__init__(nome, telefone, email)
        self._documento = normalizar_documento(cpf_cnpj)
        self._endereco = (endereco or "").strip()
        self._data_nascimento = parse_data(data_nascimento, "Data de nascimento")
        self._observacoes = (observacoes or "").strip()
        self._ativo = bool(ativo)
        self._veiculos: list = []

    @property
    def documento(self) -> str:
        """CPF/CNPJ somente com dígitos, usado na persistência."""
        return self._documento

    @property
    def cpf_cnpj(self) -> str:
        return formatar_documento(self._documento)

    @property
    def endereco(self) -> str:
        return self._endereco

    @property
    def data_nascimento(self) -> date | None:
        return self._data_nascimento

    @property
    def observacoes(self) -> str:
        return self._observacoes

    @property
    def ativo(self) -> bool:
        return self._ativo

    @property
    def veiculos(self) -> tuple:
        return tuple(self._veiculos)

    def _adicionar_veiculo(self, veiculo) -> None:
        if veiculo not in self._veiculos:
            self._veiculos.append(veiculo)

    def _remover_veiculo(self, veiculo) -> None:
        if veiculo in self._veiculos:
            self._veiculos.remove(veiculo)

    def adicionar_veiculo(self, veiculo) -> None:
        veiculo.vincular_cliente(self)

    def remover_veiculo(self, veiculo) -> None:
        if veiculo.cliente is self:
            veiculo.vincular_cliente(None)

    def inativar(self) -> None:
        self._ativo = False

    def reativar(self) -> None:
        self._ativo = True

    def atualizar_dados(
        self,
        *,
        nome: str | None = None,
        telefone: str | None = None,
        email: str | None = None,
        endereco: str | None = None,
        data_nascimento: date | str | None = None,
        observacoes: str | None = None,
    ) -> None:
        self.atualizar_contato(nome=nome, telefone=telefone, email=email)
        if endereco is not None:
            self._endereco = texto_obrigatorio(endereco, "Endereço", 3)
        if data_nascimento is not None:
            self._data_nascimento = parse_data(data_nascimento, "Data de nascimento")
        if observacoes is not None:
            self._observacoes = observacoes.strip()

    def tipo(self) -> str:
        return "Cliente"

    def __repr__(self) -> str:
        return f"Cliente(id={self.id!r}, nome={self.nome!r}, documento={self.documento!r})"
