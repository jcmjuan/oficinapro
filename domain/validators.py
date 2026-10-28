"""Validadores e normalizadores compartilhados pelo domínio."""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from .exceptions import ValidacaoError

_DOCUMENTO_DIGITOS = re.compile(r"\D")
_PLACA_ANTIGA = re.compile(r"^[A-Z]{3}[0-9]{4}$")
_PLACA_MERCOSUL = re.compile(r"^[A-Z]{3}[0-9][A-Z][0-9]{2}$")
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_NUMERO_OS = re.compile(r"^\d{4}-\d{4}$")

_CENTAVOS = Decimal("0.01")


def texto_obrigatorio(valor: str | None, campo: str, minimo: int = 1) -> str:
    if valor is None:
        raise ValidacaoError(f"{campo} é obrigatório.")
    texto = str(valor).strip()
    if len(texto) < minimo:
        raise ValidacaoError(f"{campo} deve ter pelo menos {minimo} caractere(s).")
    return texto


def decimal_valor(
    valor: Decimal | int | float | str | None,
    campo: str,
    *,
    minimo: Decimal | None = None,
    maximo: Decimal | None = None,
    casas: str = "0.01",
) -> Decimal:
    if valor is None or valor == "":
        raise ValidacaoError(f"{campo} é obrigatório.")
    try:
        numero = Decimal(str(valor)).quantize(Decimal(casas), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError) as exc:
        raise ValidacaoError(f"{campo} deve ser um número válido.") from exc
    if minimo is not None and numero < minimo:
        raise ValidacaoError(f"{campo} deve ser maior ou igual a {minimo}.")
    if maximo is not None and numero > maximo:
        raise ValidacaoError(f"{campo} deve ser menor ou igual a {maximo}.")
    return numero


def normalizar_telefone(valor: str | None) -> str:
    texto = texto_obrigatorio(valor, "Telefone")
    digitos = re.sub(r"\D", "", texto)
    if not 8 <= len(digitos) <= 13:
        raise ValidacaoError("Telefone deve ter entre 8 e 13 dígitos.")
    return digitos


def validar_email(valor: str | None) -> str | None:
    if valor is None or not str(valor).strip():
        return None
    texto = str(valor).strip().lower()
    if not _EMAIL.match(texto):
        raise ValidacaoError("E-mail inválido.")
    return texto


def normalizar_documento(valor: str | None) -> str:
    texto = texto_obrigatorio(valor, "CPF/CNPJ")
    digitos = _DOCUMENTO_DIGITOS.sub("", texto)
    if len(digitos) not in (11, 14):
        raise ValidacaoError("CPF deve ter 11 dígitos e CNPJ deve ter 14 dígitos.")
    return digitos


def formatar_documento(digitos: str) -> str:
    if len(digitos) == 11:
        return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"
    if len(digitos) == 14:
        return f"{digitos[:2]}.{digitos[2:5]}.{digitos[5:8]}/{digitos[8:12]}-{digitos[12:]}"
    return digitos


def formatar_telefone(valor: str) -> str:
    digitos = re.sub(r"\D", "", valor or "")
    if len(digitos) == 13 and digitos.startswith("55"):
        digitos = digitos[2:]
    if len(digitos) == 11:
        return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"
    if len(digitos) == 10:
        return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
    return valor


def normalizar_placa(valor: str | None) -> str:
    texto = texto_obrigatorio(valor, "Placa").upper()
    limpa = re.sub(r"[^A-Z0-9]", "", texto)
    if not (_PLACA_ANTIGA.match(limpa) or _PLACA_MERCOSUL.match(limpa)):
        raise ValidacaoError("Placa inválida. Use o padrão ABC-1234 ou ABC-1D23.")
    return f"{limpa[:3]}-{limpa[3:]}"


def placa_sem_formatacao(placa: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", placa.upper())


def normalizar_numero_os(valor: str | None) -> str:
    texto = texto_obrigatorio(valor, "Número da OS")
    if not _NUMERO_OS.match(texto):
        raise ValidacaoError("Número da OS deve seguir o padrão AAAA-NNNN.")
    return texto


def parse_data(valor: date | datetime | str | None, campo: str = "Data") -> date | None:
    if valor is None or valor == "":
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    texto = str(valor).strip()
    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue
    raise ValidacaoError(f"{campo} deve estar no formato AAAA-MM-DD ou DD/MM/AAAA.")


def parse_datetime(valor: datetime | str | None, campo: str = "Data/hora") -> datetime | None:
    if valor is None or valor == "":
        return None
    if isinstance(valor, datetime):
        return valor
    texto = str(valor).strip()
    for formato in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto, formato)
        except ValueError:
            continue
    raise ValidacaoError(f"{campo} inválida.")


def formatar_brl(valor: Decimal | int | float | str) -> str:
    numero = Decimal(str(valor)).quantize(_CENTAVOS, rounding=ROUND_HALF_UP)
    texto = f"{numero:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def apenas_digitos(valor: str) -> str:
    return re.sub(r"\D", "", valor)
