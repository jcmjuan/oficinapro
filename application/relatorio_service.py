"""Relatórios gerenciais e de comissões."""

from __future__ import annotations

import csv
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from domain.validators import formatar_brl, parse_data

from infrastructure.repositories.ordem_servico_repository import OrdemServicoRepository


class RelatorioService:
    def __init__(self, os_repo: OrdemServicoRepository) -> None:
        self.ordens = os_repo

    @staticmethod
    def periodo_mes_atual() -> tuple[date, date]:
        hoje = date.today()
        inicio = hoje.replace(day=1)
        if hoje.month == 12:
            fim = hoje.replace(day=31)
        else:
            proximo = hoje.replace(month=hoje.month + 1, day=1)
            fim = date.fromordinal(proximo.toordinal() - 1)
        return inicio, fim

    @staticmethod
    def _normalizar_periodo(
        inicio: date | datetime | str | None,
        fim: date | datetime | str | None,
    ) -> tuple[date, date]:
        if inicio is None or fim is None:
            padrao_inicio, padrao_fim = RelatorioService.periodo_mes_atual()
            inicio = inicio or padrao_inicio
            fim = fim or padrao_fim
        inicio_data = parse_data(inicio, "Início")
        fim_data = parse_data(fim, "Fim")
        assert inicio_data is not None and fim_data is not None
        if inicio_data > fim_data:
            raise ValueError("A data inicial não pode ser posterior à data final.")
        return inicio_data, fim_data

    def comissoes_por_mecanico(
        self,
        inicio: date | datetime | str | None = None,
        fim: date | datetime | str | None = None,
    ) -> list[dict]:
        inicio_data, fim_data = self._normalizar_periodo(inicio, fim)
        ordens = self.ordens.listar_finalizadas(inicio_data, fim_data)
        agregados: dict[object, dict] = {}
        for ordem in ordens:
            for item in ordem.itens:
                base = item.base_comissao
                if base is None:
                    continue
                mecanico = item.executor or ordem.mecanico
                chave = mecanico.id or mecanico.registro or mecanico.nome
                if chave not in agregados:
                    agregados[chave] = {
                        "mecanico": mecanico,
                        "nome": mecanico.nome,
                        "registro": mecanico.registro,
                        "taxa": mecanico.taxa_comissao,
                        "mao_obra": Decimal("0.00"),
                        "ordens": set(),
                    }
                agregados[chave]["mao_obra"] += item.calcular_subtotal()
                agregados[chave]["ordens"].add(ordem.numero)
        resultado = []
        for dados in agregados.values():
            dados["mao_obra"] = dados["mao_obra"].quantize(Decimal("0.01"))
            dados["comissao"] = dados["mecanico"].calcular_comissao(dados["mao_obra"])
            dados["quantidade_os"] = len(dados["ordens"])
            resultado.append(dados)
        resultado.sort(key=lambda item: item["mao_obra"], reverse=True)
        return resultado

    def resumo(
        self,
        inicio: date | datetime | str | None = None,
        fim: date | datetime | str | None = None,
    ) -> dict:
        inicio_data, fim_data = self._normalizar_periodo(inicio, fim)
        ordens = self.ordens.listar_finalizadas(inicio_data, fim_data)
        faturamento = sum((ordem.total for ordem in ordens), Decimal("0.00"))
        mao_obra = sum((ordem.subtotal_mao_obra for ordem in ordens), Decimal("0.00"))
        pecas = sum((ordem.subtotal_pecas for ordem in ordens), Decimal("0.00"))
        comissoes = self.comissoes_por_mecanico(inicio_data, fim_data)
        total_comissoes = sum(
            (item["comissao"] for item in comissoes), Decimal("0.00")
        )
        quantidade = len(ordens)
        return {
            "inicio": inicio_data,
            "fim": fim_data,
            "quantidade_os": quantidade,
            "faturamento": faturamento.quantize(Decimal("0.01")),
            "mao_obra": mao_obra.quantize(Decimal("0.01")),
            "pecas": pecas.quantize(Decimal("0.01")),
            "comissoes": total_comissoes.quantize(Decimal("0.01")),
            "ticket_medio": (
                (faturamento / quantidade).quantize(Decimal("0.01"))
                if quantidade
                else Decimal("0.00")
            ),
            "mecanicos": comissoes,
        }

    def resumo_formatado(
        self,
        inicio: date | datetime | str | None = None,
        fim: date | datetime | str | None = None,
    ) -> dict:
        dados = self.resumo(inicio, fim)
        return {
            **dados,
            "faturamento_fmt": formatar_brl(dados["faturamento"]),
            "mao_obra_fmt": formatar_brl(dados["mao_obra"]),
            "pecas_fmt": formatar_brl(dados["pecas"]),
            "comissoes_fmt": formatar_brl(dados["comissoes"]),
            "ticket_medio_fmt": formatar_brl(dados["ticket_medio"]),
        }

    def exportar_comissoes_csv(
        self,
        destino: str | Path,
        inicio: date | datetime | str | None = None,
        fim: date | datetime | str | None = None,
    ) -> Path:
        inicio_data, fim_data = self._normalizar_periodo(inicio, fim)
        comissoes = self.comissoes_por_mecanico(inicio_data, fim_data)
        destino = Path(destino)
        destino.parent.mkdir(parents=True, exist_ok=True)
        with destino.open("w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(
                [
                    "Mecânico",
                    "Registro",
                    "OS finalizadas",
                    "Mão de obra",
                    "Percentual",
                    "Comissão",
                ]
            )
            for item in comissoes:
                escritor.writerow(
                    [
                        item["nome"],
                        item["registro"],
                        item["quantidade_os"],
                        f"{item['mao_obra']:.2f}".replace(".", ","),
                        f"{(item['taxa'] * 100):.1f}%".replace(".", ","),
                        f"{item['comissao']:.2f}".replace(".", ","),
                    ]
                )
        return destino

    def resumo_status(self) -> dict[str, int]:
        return self.ordens.contar_por_status()

    def ultimas_ordens(self, limite: int = 8):
        return self.ordens.ultimas(limite)
