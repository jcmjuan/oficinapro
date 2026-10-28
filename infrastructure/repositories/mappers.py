"""Conversão de linhas SQLite para entidades de domínio."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from domain.cliente import Cliente
from domain.mecanico import Mecanico
from domain.status_historico import StatusHistorico
from domain.status_os import StatusOS
from domain.veiculo import Veiculo


def _bool(valor) -> bool:
    return bool(int(valor)) if valor is not None else False


def cliente_de_row(row: sqlite3.Row) -> Cliente:
    cliente = Cliente(
        row["nome"],
        row["telefone"],
        row["cpf_cnpj"],
        email=row["email"],
        endereco=row["endereco"],
        data_nascimento=row["data_nascimento"],
        observacoes=row["observacoes"] or "",
        ativo=_bool(row["ativo"]),
    )
    cliente.id = row["id"]
    return cliente


def mecanico_de_row(row: sqlite3.Row) -> Mecanico:
    mecanico = Mecanico(
        row["nome"],
        row["telefone"],
        row["registro"],
        row["taxa_comissao"],
        email=row["email"],
        especialidade=row["especialidade"],
        ativo=_bool(row["ativo"]),
    )
    mecanico.id = row["id"]
    return mecanico


def veiculo_de_row(row: sqlite3.Row, cliente: Cliente | None = None) -> Veiculo:
    veiculo = Veiculo(
        row["placa"],
        row["marca"],
        row["modelo"],
        row["ano"],
        row["km"],
        cliente,
        cor=row["cor"],
        combustivel=row["combustivel"],
        observacoes=row["observacoes"] or "",
    )
    veiculo.id = row["id"]
    return veiculo


def datetime_de_texto(valor: str | None) -> datetime | None:
    if not valor:
        return None
    texto = str(valor).strip()
    for formato in (
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(texto, formato)
        except ValueError:
            continue
    raise ValueError(f"Data/hora inválida no banco: {valor!r}")


def datetime_para_texto(valor: datetime | None) -> str | None:
    return valor.strftime("%Y-%m-%d %H:%M:%S") if valor else None


def historico_de_row(row: sqlite3.Row) -> StatusHistorico:
    anterior = row["status_anterior"]
    return StatusHistorico(
        status_anterior=StatusOS.from_value(anterior) if anterior else None,
        status_novo=StatusOS.from_value(row["status_novo"]),
        data_hora=datetime_de_texto(row["data_hora"]),
        usuario=row["usuario"] or "",
        motivo=row["motivo"] or "",
    )
