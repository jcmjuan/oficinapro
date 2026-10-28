"""Classe base abstrata para pessoas do domínio."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .validators import formatar_telefone, normalizar_telefone, texto_obrigatorio, validar_email


class Pessoa(ABC):
    """Dados comuns de clientes e mecânicos."""

    def __init__(self, nome: str, telefone: str, email: str | None = None) -> None:
        self._id: int | None = None
        self._nome = texto_obrigatorio(nome, "Nome", 3)
        self._telefone = normalizar_telefone(telefone)
        self._email = validar_email(email)
        self.__validar_contato()

    def __validar_contato(self) -> None:
        if not self._nome or not self._telefone:
            raise ValueError("Contato incompleto.")

    @property
    def id(self) -> int | None:
        return self._id

    @id.setter
    def id(self, valor: int | None) -> None:
        self._id = valor

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def telefone(self) -> str:
        return self._telefone

    @property
    def telefone_formatado(self) -> str:
        return formatar_telefone(self._telefone)

    @property
    def email(self) -> str | None:
        return self._email

    @abstractmethod
    def tipo(self) -> str:
        """Tipo concreto da pessoa."""

    def atualizar_contato(
        self,
        *,
        nome: str | None = None,
        telefone: str | None = None,
        email: str | None = None,
    ) -> None:
        if nome is not None:
            self._nome = texto_obrigatorio(nome, "Nome", 3)
        if telefone is not None:
            self._telefone = normalizar_telefone(telefone)
        if email is not None:
            self._email = validar_email(email)
        self.__validar_contato()

    def resumo(self) -> str:
        return f"{self._nome} ({self.tipo()})"

    def __str__(self) -> str:
        return self._nome
