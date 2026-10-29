"""Dashboard: indicadores, status e ordens recentes."""

from __future__ import annotations

from datetime import date

import customtkinter as ctk

from domain.status_os import StatusOS

from ..components import Card, DataTable, ProgressLine, SectionHeader, StatCard, SummaryRow, button_style, status_badge
from ..theme import COLORS, status_style
from ..utils import formatar_brl, formatar_data
from .base import BaseScreen


class DashboardScreen(BaseScreen):
    def __init__(self, master, app):
        super().__init__(master, app, "Dashboard", "Visão geral da oficina")
        self.header.add_button("Novo cliente", self._novo_cliente, kind="secondary", width=120)
        self.header.add_button("Nova OS", self.app.nova_os, kind="primary", width=110, symbol="+")

        self.scroll = ctk.CTkScrollableFrame(
            self.content,
            fg_color="transparent",
            scrollbar_button_color=COLORS["slate_light"],
        )
        self.scroll.grid(row=0, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

        stats = ctk.CTkFrame(self.scroll, fg_color="transparent")
        stats.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        for col in range(4):
            stats.grid_columnconfigure(col, weight=1, uniform="stat")
        self.card_faturamento = StatCard(stats, app, "Faturamento do mês", accent=COLORS["primary"], symbol="R$")
        self.card_faturamento.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        self.card_mao_obra = StatCard(stats, app, "Mão de obra", accent=COLORS["info"], symbol="MO")
        self.card_mao_obra.grid(row=0, column=1, sticky="nsew", padx=7)
        self.card_pecas = StatCard(stats, app, "Peças", accent=COLORS["purple"], symbol="PÇ")
        self.card_pecas.grid(row=0, column=2, sticky="nsew", padx=7)
        self.card_comissoes = StatCard(stats, app, "Comissões", accent=COLORS["success"], symbol="%")
        self.card_comissoes.grid(row=0, column=3, sticky="nsew", padx=(7, 0))

        body = ctk.CTkFrame(self.scroll, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        self.recent = DataTable(
            body,
            app,
            [("Nº", 1), ("Cliente", 3), ("Veículo", 2), ("Status", 2), ("Total", 2), ("", 1)],
            title="Ordens de serviço recentes",
            subtitle="Últimos atendimentos registrados",
            empty_text="Nenhuma ordem de serviço cadastrada.",
        )
        self.recent.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        right = ctk.CTkFrame(body, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        self.status_card = Card(right)
        self.status_card.grid(row=0, column=0, sticky="ew")
        SectionHeader(self.status_card, app, "Status das OS", "Distribuição atual da fila").pack(fill="x", padx=16, pady=(14, 8))
        self.status_body = ctk.CTkFrame(self.status_card, fg_color="transparent")
        self.status_body.pack(fill="x", padx=16, pady=(0, 14))
        self.status_lines = {}
        for status in StatusOS:
            _, cor = status_style(status)
            linha = ProgressLine(self.status_body, self.app, status.rotulo, 0, 0, cor)
            linha.pack(fill="x", pady=3)
            self.status_lines[status] = linha
        self.status_total = ctk.CTkLabel(
            self.status_body,
            text="",
            font=app.fonts.tiny,
            text_color=COLORS["muted"],
            anchor="w",
        )
        self.status_total.pack(fill="x", pady=(6, 0))

        self.resumo_card = Card(right)
        self.resumo_card.grid(row=1, column=0, sticky="ew", pady=(14, 0))
        SectionHeader(self.resumo_card, app, "Resumo rápido", "Indicadores do período").pack(fill="x", padx=16, pady=(14, 8))
        resumo_body = ctk.CTkFrame(self.resumo_card, fg_color="transparent")
        resumo_body.pack(fill="x", padx=16, pady=(0, 14))
        self.resumo_rows = {}
        for chave, rotulo in (
            ("ticket", "Ticket médio"),
            ("finalizadas", "OS finalizadas"),
            ("clientes", "Clientes ativos"),
            ("veiculos", "Veículos"),
        ):
            row = SummaryRow(resumo_body, app, rotulo)
            row.pack(fill="x", pady=2)
            self.resumo_rows[chave] = row

    def _novo_cliente(self) -> None:
        self.app.novo_cliente()

    def refresh(self, **kwargs) -> None:
        contexto = self.app.context
        resumo = contexto.relatorio_service.resumo_formatado()
        dashboard = contexto.ordem_service.resumo_dashboard()
        contagem = dashboard["contagem"]
        total = sum(contagem.values())

        self.header.set_title(
            "Dashboard",
            f"Visão geral da oficina • {date.today():%d/%m/%Y}",
        )
        self.card_faturamento.set_values(
            resumo["faturamento_fmt"],
            f"{resumo['quantidade_os']} OS finalizadas no mês",
        )
        self.card_mao_obra.set_values(
            resumo["mao_obra_fmt"],
            f"{self._percentual(resumo['mao_obra'], resumo['faturamento'])} do faturamento",
        )
        self.card_pecas.set_values(
            resumo["pecas_fmt"],
            f"{self._percentual(resumo['pecas'], resumo['faturamento'])} do faturamento",
        )
        self.card_comissoes.set_values(
            resumo["comissoes_fmt"],
            f"{len(resumo['mecanicos'])} mecânicos no período",
        )

        for status, linha in self.status_lines.items():
            linha.set_values(contagem.get(status.value, 0), total)
        self.status_total.configure(
            text=f"{total} ordens no total • {dashboard['abertas']} em aberto"
        )

        self.resumo_rows["ticket"].set_value(resumo["ticket_medio_fmt"])
        self.resumo_rows["finalizadas"].set_value(str(resumo["quantidade_os"]))
        self.resumo_rows["clientes"].set_value(str(contexto.clientes.contar()))
        self.resumo_rows["veiculos"].set_value(str(contexto.veiculos.contar()))

        ultimas = contexto.ordens.ultimas(8)
        self.recent.set_rows(ultimas, self._render_recent)

    @staticmethod
    def _percentual(parte, total) -> str:
        if not total:
            return "0%"
        return f"{(parte / total * 100):.0f}%"

    def _render_recent(self, frame, ordem, _indice, pady) -> None:
        ctk.CTkLabel(
            frame,
            text=f"#{ordem.numero}",
            font=self.app.fonts.small_bold,
            text_color=COLORS["primary"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=(12, 6), pady=pady)
        ctk.CTkLabel(
            frame,
            text=ordem.cliente.nome,
            font=self.app.fonts.small,
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=1, sticky="w", padx=6, pady=pady)
        veiculo = ctk.CTkFrame(frame, fg_color="transparent")
        veiculo.grid(row=0, column=2, sticky="w", padx=6, pady=pady)
        ctk.CTkLabel(
            veiculo,
            text=f"{ordem.veiculo.marca} {ordem.veiculo.modelo}",
            font=self.app.fonts.small,
            text_color=COLORS["text"],
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            veiculo,
            text=ordem.veiculo.placa,
            font=self.app.fonts.tiny,
            text_color=COLORS["muted"],
            anchor="w",
        ).pack(anchor="w")
        status_badge(frame, ordem.status, self.app).grid(row=0, column=3, sticky="w", padx=6, pady=pady)
        ctk.CTkLabel(
            frame,
            text=formatar_brl(ordem.total),
            font=self.app.fonts.small_bold,
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=4, sticky="w", padx=6, pady=pady)
        ctk.CTkButton(
            frame,
            text="Abrir",
            command=lambda numero=ordem.numero: self.app.abrir_os(numero),
            width=64,
            height=28,
            corner_radius=7,
            font=self.app.fonts.button_small,
            **button_style("secondary"),
        ).grid(row=0, column=5, sticky="e", padx=(6, 12), pady=pady)
