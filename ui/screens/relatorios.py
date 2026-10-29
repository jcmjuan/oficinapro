"""Tela de relatórios e comissões."""

from __future__ import annotations

from datetime import date
from tkinter import filedialog, messagebox

import customtkinter as ctk

from domain.validators import formatar_brl, parse_data

from ..components import Badge, Card, DataTable, ProgressLine, SectionHeader, StatCard, SummaryRow, button_style
from ..theme import COLORS
from ..utils import formatar_data, formatar_percentual, iniciais
from .base import BaseScreen


class RelatoriosScreen(BaseScreen):
    def __init__(self, master, app):
        super().__init__(master, app, "Relatórios", "Desempenho e comissões da oficina")
        self.header.add_button("Exportar CSV", self._exportar_csv, kind="secondary", width=120)
        self.inicio, self.fim = app.context.relatorio_service.periodo_mes_atual()

        self.scroll = ctk.CTkScrollableFrame(
            self.content,
            fg_color="transparent",
            scrollbar_button_color=COLORS["slate_light"],
        )
        self.scroll.grid(row=0, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

        filtro = Card(self.scroll)
        filtro.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        filtro.grid_columnconfigure(4, weight=1)
        ctk.CTkLabel(
            filtro,
            text="Período",
            font=self.app.fonts.small_bold,
            text_color=COLORS["text"],
        ).grid(row=0, column=0, sticky="w", padx=(16, 8), pady=14)
        self.inicio_entry = ctk.CTkEntry(
            filtro,
            width=110,
            height=32,
            corner_radius=7,
            font=self.app.fonts.small,
            border_color=COLORS["border"],
        )
        self.inicio_entry.grid(row=0, column=1, sticky="w")
        self.inicio_entry.insert(0, formatar_data(self.inicio))
        ctk.CTkLabel(
            filtro,
            text="até",
            font=self.app.fonts.small,
            text_color=COLORS["muted"],
        ).grid(row=0, column=2, padx=6)
        self.fim_entry = ctk.CTkEntry(
            filtro,
            width=110,
            height=32,
            corner_radius=7,
            font=self.app.fonts.small,
            border_color=COLORS["border"],
        )
        self.fim_entry.grid(row=0, column=3, sticky="w")
        self.fim_entry.insert(0, formatar_data(self.fim))
        ctk.CTkButton(
            filtro,
            text="Atualizar",
            command=self._aplicar_periodo,
            width=90,
            height=32,
            corner_radius=8,
            font=self.app.fonts.button_small,
            **button_style("primary"),
        ).grid(row=0, column=5, padx=6)
        ctk.CTkButton(
            filtro,
            text="Mês atual",
            command=self._mes_atual,
            width=86,
            height=32,
            corner_radius=8,
            font=self.app.fonts.button_small,
            **button_style("secondary"),
        ).grid(row=0, column=6, padx=(0, 16))

        stats = ctk.CTkFrame(self.scroll, fg_color="transparent")
        stats.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        for col in range(3):
            stats.grid_columnconfigure(col, weight=1, uniform="stats")
        self.card_faturamento = StatCard(stats, app, "Faturamento", accent=COLORS["primary"], symbol="R$")
        self.card_faturamento.grid(row=0, column=0, sticky="nsew", padx=(0, 7), pady=(0, 7))
        self.card_mao = StatCard(stats, app, "Mão de obra", accent=COLORS["info"], symbol="MO")
        self.card_mao.grid(row=0, column=1, sticky="nsew", padx=7, pady=(0, 7))
        self.card_pecas = StatCard(stats, app, "Peças", accent=COLORS["purple"], symbol="PÇ")
        self.card_pecas.grid(row=0, column=2, sticky="nsew", padx=(7, 0), pady=(0, 7))
        self.card_comissoes = StatCard(stats, app, "Comissões", accent=COLORS["success"], symbol="%")
        self.card_comissoes.grid(row=1, column=0, sticky="nsew", padx=(0, 7), pady=(7, 0))
        self.card_ticket = StatCard(stats, app, "Ticket médio", accent=COLORS["warning"], symbol="TM")
        self.card_ticket.grid(row=1, column=1, sticky="nsew", padx=7, pady=(7, 0))
        self.card_os = StatCard(stats, app, "OS finalizadas", accent=COLORS["slate"], symbol="OS")
        self.card_os.grid(row=1, column=2, sticky="nsew", padx=(7, 0), pady=(7, 0))

        body = ctk.CTkFrame(self.scroll, fg_color="transparent")
        body.grid(row=2, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        self.table = DataTable(
            body,
            app,
            [
                ("Mecânico", 3),
                ("OS", 1),
                ("Mão de obra", 2),
                ("Taxa", 1),
                ("Comissão", 2),
                ("Status", 1),
            ],
            title="Comissões por mecânico",
            subtitle="Base: mão de obra das OS finalizadas no período",
            empty_text="Nenhuma OS finalizada no período.",
        )
        self.table.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        right = ctk.CTkFrame(body, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        composicao = Card(right)
        composicao.grid(row=0, column=0, sticky="ew")
        SectionHeader(composicao, self.app, "Composição do faturamento", "Peças e mão de obra").pack(fill="x", padx=16, pady=(14, 8))
        self.composicao_body = ctk.CTkFrame(composicao, fg_color="transparent")
        self.composicao_body.pack(fill="x", padx=16, pady=(0, 14))
        self.composicao_lines = {}
        for chave, rotulo, cor in (
            ("pecas", "Peças", COLORS["purple"]),
            ("mao_obra", "Mão de obra", COLORS["info"]),
        ):
            linha = ProgressLine(self.composicao_body, self.app, rotulo, 0, 0, cor)
            linha.pack(fill="x", pady=4)
            self.composicao_lines[chave] = linha
        self.composicao_total = ctk.CTkLabel(
            self.composicao_body,
            text="",
            font=self.app.fonts.small_bold,
            text_color=COLORS["text"],
            anchor="w",
        )
        self.composicao_total.pack(fill="x", pady=(6, 0))

        periodo = Card(right)
        periodo.grid(row=1, column=0, sticky="ew", pady=(14, 0))
        SectionHeader(periodo, self.app, "Período analisado", "").pack(fill="x", padx=16, pady=(14, 8))
        corpo_periodo = ctk.CTkFrame(periodo, fg_color="transparent")
        corpo_periodo.pack(fill="x", padx=16, pady=(0, 14))
        self.periodo_rows = {}
        for chave, rotulo in (
            ("inicio", "Início"),
            ("fim", "Fim"),
            ("os", "OS finalizadas"),
            ("comissoes", "Total de comissões"),
        ):
            row = SummaryRow(corpo_periodo, self.app, rotulo)
            row.pack(fill="x", pady=2)
            self.periodo_rows[chave] = row

    def _aplicar_periodo(self) -> None:
        try:
            inicio = parse_data(self.inicio_entry.get(), "Início")
            fim = parse_data(self.fim_entry.get(), "Fim")
            if inicio is None or fim is None:
                raise ValueError("Informe as duas datas.")
            if inicio > fim:
                raise ValueError("A data inicial não pode ser posterior à final.")
            self.inicio, self.fim = inicio, fim
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Período inválido", str(exc), parent=self)

    def _mes_atual(self) -> None:
        self.inicio, self.fim = self.app.context.relatorio_service.periodo_mes_atual()
        self.inicio_entry.delete(0, "end")
        self.inicio_entry.insert(0, formatar_data(self.inicio))
        self.fim_entry.delete(0, "end")
        self.fim_entry.insert(0, formatar_data(self.fim))
        self.refresh()

    def refresh(self, **kwargs) -> None:
        try:
            dados = self.app.context.relatorio_service.resumo_formatado(self.inicio, self.fim)
        except Exception as exc:
            messagebox.showerror("Não foi possível calcular", str(exc), parent=self)
            return
        self.header.set_title(
            "Relatórios",
            f"{formatar_data(dados['inicio'])} a {formatar_data(dados['fim'])} • dados consolidados",
        )
        self.card_faturamento.set_values(dados["faturamento_fmt"], f"{dados['quantidade_os']} OS finalizadas")
        self.card_mao.set_values(dados["mao_obra_fmt"], self._percentual(dados["mao_obra"], dados["faturamento"]))
        self.card_pecas.set_values(dados["pecas_fmt"], self._percentual(dados["pecas"], dados["faturamento"]))
        self.card_comissoes.set_values(dados["comissoes_fmt"], f"{len(dados['mecanicos'])} mecânicos")
        self.card_ticket.set_values(dados["ticket_medio_fmt"], "média por OS")
        self.card_os.set_values(str(dados["quantidade_os"]), "no período")

        self.table.set_rows(dados["mecanicos"], self._render_linha)
        self.periodo_rows["inicio"].set_value(formatar_data(dados["inicio"]))
        self.periodo_rows["fim"].set_value(formatar_data(dados["fim"]))
        self.periodo_rows["os"].set_value(str(dados["quantidade_os"]))
        self.periodo_rows["comissoes"].set_value(dados["comissoes_fmt"])

        total = dados["faturamento"]
        self.composicao_lines["pecas"].set_values(int(dados["pecas"]), int(total))
        self.composicao_lines["mao_obra"].set_values(int(dados["mao_obra"]), int(total))
        self.composicao_total.configure(text=f"Total: {dados['faturamento_fmt']}")

    @staticmethod
    def _percentual(parte, total) -> str:
        if not total:
            return "0% do faturamento"
        return f"{(parte / total * 100):.0f}% do faturamento"

    def _render_linha(self, frame, item, _indice, pady) -> None:
        mecanico = item["mecanico"]
        pessoa = ctk.CTkFrame(frame, fg_color="transparent")
        pessoa.grid(row=0, column=0, sticky="w", padx=(12, 6), pady=pady)
        ctk.CTkLabel(
            pessoa,
            text=iniciais(mecanico.nome),
            width=32,
            height=32,
            corner_radius=16,
            fg_color=COLORS["surface_alt"],
            text_color=COLORS["primary"],
            font=self.app.fonts.tiny,
        ).pack(side="left", padx=(0, 8))
        nomes = ctk.CTkFrame(pessoa, fg_color="transparent")
        nomes.pack(side="left")
        ctk.CTkLabel(nomes, text=item["nome"], font=self.app.fonts.small_bold, text_color=COLORS["text"], anchor="w").pack(anchor="w")
        ctk.CTkLabel(nomes, text=item["registro"], font=self.app.fonts.tiny, text_color=COLORS["muted"], anchor="w").pack(anchor="w")

        ctk.CTkLabel(frame, text=str(item["quantidade_os"]), font=self.app.fonts.small, text_color=COLORS["text"], anchor="w").grid(row=0, column=1, sticky="w", padx=6, pady=pady)
        ctk.CTkLabel(frame, text=formatar_brl(item["mao_obra"]), font=self.app.fonts.small, text_color=COLORS["text"], anchor="w").grid(row=0, column=2, sticky="w", padx=6, pady=pady)
        ctk.CTkLabel(frame, text=formatar_percentual(item["taxa"]), font=self.app.fonts.small, text_color=COLORS["muted"], anchor="w").grid(row=0, column=3, sticky="w", padx=6, pady=pady)
        ctk.CTkLabel(frame, text=formatar_brl(item["comissao"]), font=self.app.fonts.small_bold, text_color=COLORS["text"], anchor="w").grid(row=0, column=4, sticky="w", padx=6, pady=pady)
        Badge(frame, "A pagar", COLORS["success_bg"], COLORS["success"], self.app).grid(row=0, column=5, sticky="w", padx=(6, 12), pady=pady)

    def _exportar_csv(self) -> None:
        caminho = filedialog.asksaveasfilename(
            parent=self,
            title="Exportar comissões",
            defaultextension=".csv",
            initialfile=f"comissoes_{self.inicio:%Y-%m}.csv",
            filetypes=[("CSV", "*.csv")],
        )
        if not caminho:
            return
        try:
            destino = self.app.context.relatorio_service.exportar_comissoes_csv(
                caminho, self.inicio, self.fim
            )
            self.app.notify(f"CSV exportado: {destino}")
        except Exception as exc:
            messagebox.showerror("Não foi possível exportar", str(exc), parent=self)
