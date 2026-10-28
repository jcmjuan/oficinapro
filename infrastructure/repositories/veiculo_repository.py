"""Repositório de veículos."""

from __future__ import annotations

import sqlite3

from domain.exceptions import DuplicadoError, NaoEncontradoError, RegraNegocioError
from domain.validators import normalizar_placa
from domain.veiculo import Veiculo

from ..database import Database
from .mappers import cliente_de_row, veiculo_de_row


class VeiculoRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def _cliente_do_veiculo(self, linha) -> object:
        cliente_linha = self.db.buscar_um(
            "SELECT * FROM cliente WHERE id = ?", (linha["cliente_id"],)
        )
        if cliente_linha is None:
            raise NaoEncontradoError(
                f"Cliente {linha['cliente_id']} do veículo não encontrado."
            )
        return cliente_de_row(cliente_linha)

    def salvar(self, veiculo: Veiculo) -> Veiculo:
        if veiculo.cliente is None or veiculo.cliente.id is None:
            raise RegraNegocioError("O veículo precisa estar vinculado a um cliente salvo.")
        try:
            with self.db.transacao() as conn:
                if veiculo.id is None:
                    cursor = conn.execute(
                        """
                        INSERT INTO veiculo
                            (placa, marca, modelo, ano, km, cor, combustivel,
                             cliente_id, observacoes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            veiculo.placa,
                            veiculo.marca,
                            veiculo.modelo,
                            veiculo.ano,
                            veiculo.km,
                            veiculo.cor,
                            veiculo.combustivel,
                            veiculo.cliente.id,
                            veiculo.observacoes,
                        ),
                    )
                    veiculo.id = int(cursor.lastrowid)
                else:
                    conn.execute(
                        """
                        UPDATE veiculo SET
                            placa = ?, marca = ?, modelo = ?, ano = ?, km = ?,
                            cor = ?, combustivel = ?, cliente_id = ?,
                            observacoes = ?, atualizado_em = CURRENT_TIMESTAMP
                        WHERE id = ?
                        """,
                        (
                            veiculo.placa,
                            veiculo.marca,
                            veiculo.modelo,
                            veiculo.ano,
                            veiculo.km,
                            veiculo.cor,
                            veiculo.combustivel,
                            veiculo.cliente.id,
                            veiculo.observacoes,
                            veiculo.id,
                        ),
                    )
        except sqlite3.IntegrityError as exc:
            raise DuplicadoError(
                f"Já existe veículo com a placa {veiculo.placa}."
            ) from exc
        return veiculo

    def buscar_por_id(self, veiculo_id: int) -> Veiculo:
        linha = self.db.buscar_um("SELECT * FROM veiculo WHERE id = ?", (veiculo_id,))
        if linha is None:
            raise NaoEncontradoError(f"Veículo {veiculo_id} não encontrado.")
        cliente = self._cliente_do_veiculo(linha)
        return veiculo_de_row(linha, cliente)

    def buscar_por_placa(self, placa: str) -> Veiculo | None:
        placa_formatada = normalizar_placa(placa)
        linha = self.db.buscar_um(
            "SELECT * FROM veiculo WHERE placa = ?", (placa_formatada,)
        )
        if linha is None:
            return None
        cliente = self._cliente_do_veiculo(linha)
        return veiculo_de_row(linha, cliente)

    def listar(
        self,
        *,
        cliente_id: int | None = None,
        busca: str = "",
    ) -> list[Veiculo]:
        sql = "SELECT * FROM veiculo"
        condicoes = []
        parametros: list = []
        if cliente_id is not None:
            condicoes.append("cliente_id = ?")
            parametros.append(cliente_id)
        if busca.strip():
            termo = f"%{busca.strip()}%"
            condicoes.append(
                "(placa LIKE ? OR marca LIKE ? OR modelo LIKE ? "
                "OR cliente_id IN (SELECT id FROM cliente WHERE nome LIKE ?))"
            )
            parametros.extend([termo, termo, termo, termo])
        if condicoes:
            sql += " WHERE " + " AND ".join(condicoes)
        sql += " ORDER BY placa"
        veiculos = []
        for linha in self.db.buscar_todos(sql, tuple(parametros)):
            cliente = self._cliente_do_veiculo(linha)
            veiculos.append(veiculo_de_row(linha, cliente))
        return veiculos

    def atualizar_km(self, veiculo_id: int, km: int) -> None:
        with self.db.transacao() as conn:
            cursor = conn.execute(
                "UPDATE veiculo SET km = ?, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?",
                (int(km), veiculo_id),
            )
            if cursor.rowcount == 0:
                raise NaoEncontradoError(f"Veículo {veiculo_id} não encontrado.")

    def contar(self) -> int:
        return int(self.db.buscar_um("SELECT COUNT(*) FROM veiculo")[0])
