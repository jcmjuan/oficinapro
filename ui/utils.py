"""Utilitários de formatação e integração com o sistema operacional."""

from __future__ import annotations

import subprocess
import sys
import webbrowser
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from domain.status_historico import StatusHistorico
from domain.validators import formatar_brl


def formatar_data(valor: date | datetime | None) -> str:
    if valor is None:
        return "—"
    return valor.strftime("%d/%m/%Y")


def formatar_data_hora(valor: datetime | None) -> str:
    if valor is None:
        return "—"
    return valor.strftime("%d/%m/%Y %H:%M")


def descricao_transicao(registro: StatusHistorico) -> str:
    anterior = registro.status_anterior.rotulo if registro.status_anterior else "—"
    return f"{anterior} → {registro.status_novo.rotulo}"


def iniciais(nome: str) -> str:
    partes = [parte for parte in (nome or "").split() if parte]
    if not partes:
        return "?"
    if len(partes) == 1:
        return partes[0][:2].upper()
    return (partes[0][0] + partes[-1][0]).upper()


def truncar(texto: str, limite: int) -> str:
    texto = texto or ""
    return texto if len(texto) <= limite else texto[: limite - 1] + "…"


def para_decimal(valor: str | int | float | Decimal) -> Decimal:
    """Aceita 1.234,56, 1234,56 e 1234.56."""
    if isinstance(valor, Decimal):
        return valor
    if isinstance(valor, (int, float)):
        return Decimal(str(valor))
    texto = str(valor or "").strip()
    if not texto:
        raise ValueError("Informe um valor.")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    return Decimal(texto)


def para_inteiro(valor: str | int) -> int:
    if isinstance(valor, int):
        return valor
    texto = str(valor or "").strip()
    if not texto:
        raise ValueError("Informe um número inteiro.")
    return int(texto)


def abrir_arquivo(caminho: str | Path) -> None:
    caminho = str(Path(caminho).resolve())
    if sys.platform.startswith("win"):
        import os

        os.startfile(caminho)  # type: ignore[attr-defined]
        return
    if sys.platform == "darwin":
        subprocess.Popen(["open", caminho])
        return
    subprocess.Popen(["xdg-open", caminho])


def abrir_url(url: str) -> None:
    webbrowser.open(url, new=2)


def formatar_percentual(valor: Decimal | float | int) -> str:
    numero = float(valor) * 100
    texto = f"{numero:.1f}".rstrip("0").rstrip(".")
    return f"{texto}%"


def limpar_texto(valor: str | None) -> str:
    return (valor or "").strip()


def parse_decimal_opcional(valor: str) -> Decimal | None:
    if not (valor or "").strip():
        return None
    try:
        return para_decimal(valor)
    except (InvalidOperation, ValueError):
        return None
