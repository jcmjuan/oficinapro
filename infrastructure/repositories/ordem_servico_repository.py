"""Repositório de ordens de serviço e seus itens/histórico."""

from __future__ import annotations

import sqlite3
from datetime import date, datetime
from decimal import Decimal

from domain.exceptions import NaoEncontradoError, RegraNegocioError, ValidacaoError
from domain.item_os import ItemOS
from domain.mao_de_obra import MaoDeObra
from domain.ordem_servico import OrdemServico
from domain.peca import Peca
from domain.status_os import StatusOS
from domain.tipo_item import TipoItem

from ..database import Database
from .mappers import (
    cliente_de_row,
    datetime_de_texto,
    datetime_para_texto,
    historico_de_row,
    mecanico_de_row,
    veiculo_de_row,
)


class OrdemServicoRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def _proximo_numero(self, ano: int) -> str:
        prefixo = f"{ano}-%"
        linha = self.db.buscar_um(
            "SELECT numero FROM ordem_servico WHERE numero LIKE ? ORDER BY numero DESC LIMIT 1",
            (prefixo,),
        )
        sequencia = 0
        if linha:
            try:
                sequencia = int(str(linha["numero"]).split("-")[1])
            except (IndexError, ValueError):
                sequencia = 0
        return f"{ano}-{sequencia + 1:04d}"

    def proximo_numero(self, ano: int | None = None) -> str:
        return self._proximo_numero(int(ano or datetime.now().year))

    def existe(self, numero: str) -> bool:
        linha = self.db.buscar_um(
            "SELECT 1 FROM ordem_servico WHERE numero = ?", (numero,)
        )
        return linha is not None

    def salvar(self, ordem: OrdemServico) -> OrdemServico:
        if ordem.cliente.id is None:
            raise RegraNegocioError("Cliente da OS precisa estar salvo.")
        if ordem.veiculo.id is None:
            raise RegraNegocioError("Veículo da OS precisa estar salvo.")
        if ordem.mecanico.id is None:
            raise RegraNegocioError("Mecânico da OS precisa estar salvo.")
        with self.db.transacao() as conn:
            conn.execute(
                """
                INSERT INTO ordem_servico
                    (numero, cliente_id, veiculo_id, mecanico_id, status,
                     desconto, data_abertura, data_aprovacao, data_inicio,
                     data_finalizacao, data_cancelamento, motivo_cancelamento,
                     observacoes, criado_por)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(numero) DO UPDATE SET
                    cliente_id = excluded.cliente_id,
                    veiculo_id = excluded.veiculo_id,
                    mecanico_id = excluded.mecanico_id,
                    status = excluded.status,
                    desconto = excluded.desconto,
                    data_abertura = excluded.data_abertura,
                    data_aprovacao = excluded.data_aprovacao,
                    data_inicio = excluded.data_inicio,
                    data_finalizacao = excluded.data_finalizacao,
                    data_cancelamento = excluded.data_cancelamento,
                    motivo_cancelamento = excluded.motivo_cancelamento,
                    observacoes = excluded.observacoes,
                    criado_por = excluded.criado_por,
                    atualizado_em = CURRENT_TIMESTAMP
                """,
                (
                    ordem.numero,
                    ordem.cliente.id,
                    ordem.veiculo.id,
                    ordem.mecanico.id,
                    ordem.status.value,
                    str(ordem.desconto),
                    datetime_para_texto(ordem.data_abertura),
                    datetime_para_texto(ordem.data_aprovacao),
                    datetime_para_texto(ordem.data_inicio),
                    datetime_para_texto(ordem.data_finalizacao),
                    datetime_para_texto(ordem.data_cancelamento),
                    ordem.motivo_cancelamento,
                    ordem.observacoes,
                    ordem.criado_por,
                ),
            )
            linha = conn.execute(
                "SELECT id FROM ordem_servico WHERE numero = ?", (ordem.numero,)
            ).fetchone()
            if linha is None:
                raise RegraNegocioError("Não foi possível persistir a OS.")
            ordem.id = int(linha["id"])
            conn.execute(
                "DELETE FROM item_os WHERE ordem_servico_id = ?", (ordem.id,)
            )
            for item in ordem.itens:
                if isinstance(item, Peca):
                    cursor = conn.execute(
                        """
                        INSERT INTO item_os
                            (ordem_servico_id, tipo, descricao, quantidade,
                             valor_unitario, codigo_peca, fornecedor)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            ordem.id,
                            item.tipo().value,
                            item.descricao,
                            str(item.quantidade),
                            str(item.valor_unitario),
                            item.codigo,
                            item.fornecedor,
                        ),
                    )
                elif isinstance(item, MaoDeObra):
                    cursor = conn.execute(
                        """
                        INSERT INTO item_os
                            (ordem_servico_id, tipo, descricao, quantidade,
                             valor_unitario, horas, taxa_horaria, mecanico_id)
                        VALUES (?, ?, ?, '1.00', ?, ?, ?, ?)
                        """,
                        (
                            ordem.id,
                            item.tipo().value,
                            item.descricao,
                            str(item.taxa_horaria),
                            str(item.horas),
                            str(item.taxa_horaria),
                            item.mecanico.id if item.mecanico else None,
                        ),
                    )
                else:
                    raise RegraNegocioError(
                        f"Tipo de item não suportado: {type(item).__name__}"
                    )
                item.id = int(cursor.lastrowid)

            existentes = conn.execute(
                "SELECT COUNT(*) FROM status_historico WHERE ordem_servico_id = ?",
                (ordem.id,),
            ).fetchone()[0]
            for registro in ordem.historico[existentes:]:
                conn.execute(
                    """
                    INSERT INTO status_historico
                        (ordem_servico_id, status_anterior, status_novo,
                         data_hora, usuario, motivo)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        ordem.id,
                        registro.status_anterior.value
                        if registro.status_anterior
                        else None,
                        registro.status_novo.value,
                        datetime_para_texto(registro.data_hora),
                        registro.usuario,
                        registro.motivo,
                    ),
                )
        return ordem

    def _carregar_itens(self, ordem_id: int, mecanico_responsavel) -> list[ItemOS]:
        itens: list[ItemOS] = []
        linhas = self.db.buscar_todos(
            "SELECT * FROM item_os WHERE ordem_servico_id = ? ORDER BY id",
            (ordem_id,),
        )
        for linha in linhas:
            try:
                tipo = TipoItem.from_value(linha["tipo"])
            except ValidacaoError as exc:
                raise RegraNegocioError(
                    f"Tipo de item inválido no banco: {linha['tipo']}"
                ) from exc
            if tipo is TipoItem.PECA:
                item: ItemOS = Peca(
                    linha["descricao"],
                    Decimal(str(linha["quantidade"])),
                    Decimal(str(linha["valor_unitario"])),
                    codigo=linha["codigo_peca"],
                    fornecedor=linha["fornecedor"],
                )
            elif tipo is TipoItem.MAO_DE_OBRA:
                mecanico = mecanico_responsavel
                if linha["mecanico_id"] and (
                    mecanico is None or mecanico.id != linha["mecanico_id"]
                ):
                    mecanico_linha = self.db.buscar_um(
                        "SELECT * FROM mecanico WHERE id = ?", (linha["mecanico_id"],)
                    )
                    mecanico = (
                        mecanico_de_row(mecanico_linha) if mecanico_linha else None
                    )
                item = MaoDeObra(
                    linha["descricao"],
                    Decimal(str(linha["horas"] or "0")),
                    Decimal(str(linha["taxa_horaria"] or linha["valor_unitario"])),
                    mecanico,
                )
            else:
                raise RegraNegocioError(
                    f"Tipo de item não suportado: {tipo.value}"
                )
            item.id = linha["id"]
            itens.append(item)
        return itens

    def buscar_por_numero(self, numero: str) -> OrdemServico | None:
        linha = self.db.buscar_um(
            "SELECT * FROM ordem_servico WHERE numero = ?", (numero,)
        )
        if linha is None:
            return None
        cliente_linha = self.db.buscar_um(
            "SELECT * FROM cliente WHERE id = ?", (linha["cliente_id"],)
        )
        if cliente_linha is None:
            raise NaoEncontradoError(
                f"Cliente {linha['cliente_id']} da OS {numero} não encontrado."
            )
        cliente = cliente_de_row(cliente_linha)
        veiculo_linha = self.db.buscar_um(
            "SELECT * FROM veiculo WHERE id = ?", (linha["veiculo_id"],)
        )
        if veiculo_linha is None:
            raise NaoEncontradoError(
                f"Veículo {linha['veiculo_id']} da OS {numero} não encontrado."
            )
        veiculo = veiculo_de_row(veiculo_linha, cliente)
        mecanico_linha = self.db.buscar_um(
            "SELECT * FROM mecanico WHERE id = ?", (linha["mecanico_id"],)
        )
        if mecanico_linha is None:
            raise NaoEncontradoError(
                f"Mecânico {linha['mecanico_id']} da OS {numero} não encontrado."
            )
        mecanico = mecanico_de_row(mecanico_linha)
        itens = self._carregar_itens(int(linha["id"]), mecanico)
        historico = [
            historico_de_row(registro)
            for registro in self.db.buscar_todos(
                "SELECT * FROM status_historico WHERE ordem_servico_id = ? ORDER BY id",
                (linha["id"],),
            )
        ]
        return OrdemServico(
            numero=linha["numero"],
            cliente=cliente,
            veiculo=veiculo,
            mecanico=mecanico,
            status=linha["status"],
            desconto=linha["desconto"],
            data_abertura=linha["data_abertura"],
            data_aprovacao=linha["data_aprovacao"],
            data_inicio=linha["data_inicio"],
            data_finalizacao=linha["data_finalizacao"],
            data_cancelamento=linha["data_cancelamento"],
            motivo_cancelamento=linha["motivo_cancelamento"],
            observacoes=linha["observacoes"] or "",
            criado_por=linha["criado_por"] or "",
            itens=itens,
            historico=historico,
            id=int(linha["id"]),
        )

    def obter(self, numero: str) -> OrdemServico:
        ordem = self.buscar_por_numero(numero)
        if ordem is None:
            raise NaoEncontradoError(f"OS {numero} não encontrada.")
        return ordem

    def listar(
        self,
        *,
        status: StatusOS | str | None = None,
        cliente_id: int | None = None,
        veiculo_id: int | None = None,
        mecanico_id: int | None = None,
        data_inicio: date | datetime | str | None = None,
        data_fim: date | datetime | str | None = None,
        busca: str = "",
        limite: int | None = None,
    ) -> list[OrdemServico]:
        condicoes = []
        parametros: list = []
        if status is not None:
            condicoes.append("status = ?")
            parametros.append(StatusOS.from_value(status).value)
        if cliente_id is not None:
            condicoes.append("cliente_id = ?")
            parametros.append(cliente_id)
        if veiculo_id is not None:
            condicoes.append("veiculo_id = ?")
            parametros.append(veiculo_id)
        if mecanico_id is not None:
            condicoes.append("mecanico_id = ?")
            parametros.append(mecanico_id)
        if data_inicio is not None:
            condicoes.append("date(data_abertura) >= date(?)")
            parametros.append(str(data_inicio))
        if data_fim is not None:
            condicoes.append("date(data_abertura) <= date(?)")
            parametros.append(str(data_fim))
        if busca.strip():
            termo = f"%{busca.strip()}%"
            condicoes.append(
                "(" 
                "numero LIKE ? "
                "OR cliente_id IN (SELECT id FROM cliente WHERE nome LIKE ?) "
                "OR veiculo_id IN (SELECT id FROM veiculo WHERE placa LIKE ? OR marca LIKE ? OR modelo LIKE ?)"
                ")"
            )
            parametros.extend([termo, termo, termo, termo, termo])
        sql = "SELECT numero FROM ordem_servico"
        if condicoes:
            sql += " WHERE " + " AND ".join(condicoes)
        sql += " ORDER BY numero DESC"
        if limite is not None:
            sql += f" LIMIT {int(limite)}"
        ordens = []
        for linha in self.db.buscar_todos(sql, tuple(parametros)):
            ordem = self.buscar_por_numero(linha["numero"])
            if ordem is not None:
                ordens.append(ordem)
        return ordens

    def listar_finalizadas(
        self,
        inicio: date | datetime | str,
        fim: date | datetime | str,
    ) -> list[OrdemServico]:
        linhas = self.db.buscar_todos(
            """
            SELECT numero FROM ordem_servico
            WHERE status = 'FINALIZADA'
              AND date(data_finalizacao) BETWEEN date(?) AND date(?)
            ORDER BY data_finalizacao, numero
            """,
            (str(inicio), str(fim)),
        )
        ordens = []
        for linha in linhas:
            ordem = self.buscar_por_numero(linha["numero"])
            if ordem is not None:
                ordens.append(ordem)
        return ordens

    def ultimas(self, limite: int = 5) -> list[OrdemServico]:
        return self.listar(limite=limite)

    def contar_por_status(self) -> dict[str, int]:
        resultado = {status.value: 0 for status in StatusOS}
        for linha in self.db.buscar_todos(
            "SELECT status, COUNT(*) AS total FROM ordem_servico GROUP BY status"
        ):
            resultado[linha["status"]] = int(linha["total"])
        return resultado

    def contar(self) -> int:
        return int(self.db.buscar_um("SELECT COUNT(*) FROM ordem_servico")[0])
