"""Tela de veículos."""

from __future__ import annotations

from tkinter import messagebox

import customtkinter as ctk

from ..components import DataTable, button_style, status_badge
from ..dialogs import VeiculoDialog
from ..theme import COLORS
from ..utils import formatar_data
from .base import BaseScreen


class VeiculosScreen(BaseScreen):
    def __init__(self, master, app):
        super().__init__(master, app, "Veículos", "Frota atendida pela oficina")
        self.header.add_button("Novo veículo", self._novo, kind="primary", width=130, symbol="+")
        self.cliente_id: int | None = None
        self._search_job = None

        self.content.grid_rowconfigure(0, weight=0)
        self.content.grid_rowconfigure(2, weight=1)
        toolbar = ctk.CTkFrame(self.content, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        toolbar.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            toolbar,
            text="Buscar",
            font=self.app.fonts.small_bold,
            text_color=COLORS["text"],
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        ctk.CTkEntry(
            toolbar,
            textvariable=self.search_var,
            placeholder_text="Placa, marca, modelo ou cliente...",
            height=36,
            corner_radius=8,
            font=self.app.fonts.body,
            border_color=COLORS["border"],
            fg_color=COLORS["surface"],
        ).grid(row=0, column=1, sticky="ew")

        self.filter_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        self.filter_label = ctk.CTkLabel(
            self.filter_frame,
            text="",
            font=self.app.fonts.small,
            text_color=COLORS["muted"],
            anchor="w",
        )
        self.filter_label.pack(side="left")
        self.clear_filter = ctk.CTkButton(
            self.filter_frame,
            text="Limpar filtro",
            command=self._limpar_filtro,
            width=92,
            height=26,
            corner_radius=7,
            font=self.app.fonts.button_small,
            **button_style("secondary"),
        )
        self.filter_frame.grid_remove()

        self.table = DataTable(
            self.content,
            app,
            [
                ("Placa", 1),
                ("Veículo", 3),
                ("Ano", 1),
                ("KM", 1),
                ("Cliente", 3),
                ("Última OS", 2),
                ("Ações", 2),
            ],
            title="Frota atendida",
            subtitle="Consulte o histórico de manutenções por placa e cliente",
            empty_text="Nenhum veículo encontrado.",
        )
        self.table.grid(row=2, column=0, sticky="nsew")

    def _on_search(self, *_args) -> None:
        if self._search_job is not None:
            try:
                self.after_cancel(self._search_job)
            except Exception:
                pass
        self._search_job = self.after(250, self.refresh)

    def on_show(self, **kwargs) -> None:
        self.cliente_id = kwargs.get("cliente_id")
        self.refresh()

    def refresh(self, **kwargs) -> None:
        contexto = self.app.context
        veiculos = contexto.veiculos.listar(
            cliente_id=self.cliente_id,
            busca=self.search_var.get(),
        )
        todos = contexto.veiculos.listar()
        if self.cliente_id:
            try:
                cliente = contexto.clientes.buscar_por_id(self.cliente_id)
                self.filter_label.configure(text=f"Filtro: veículos de {cliente.nome}")
                self.clear_filter.pack(side="left", padx=(10, 0))
                self.filter_frame.grid()
            except Exception:
                self.cliente_id = None
        if not self.cliente_id:
            self.filter_label.configure(text="")
            self.clear_filter.pack_forget()
            self.filter_frame.grid_remove()
        texto_exibidos = "1 exibido" if len(veiculos) == 1 else f"{len(veiculos)} exibidos"
        self.header.set_title(
            "Veículos",
            f"{len(todos)} veículos cadastrados • {texto_exibidos}",
        )
        self.table.set_rows(veiculos, self._render_row)

    def _limpar_filtro(self) -> None:
        self.cliente_id = None
        self.refresh()

    def _render_row(self, frame, veiculo, _indice, pady) -> None:
        ctk.CTkLabel(
            frame,
            text=veiculo.placa,
            font=self.app.fonts.mono,
            text_color=COLORS["text"],
            fg_color=COLORS["surface_alt"],
            corner_radius=5,
            width=82,
            height=28,
        ).grid(row=0, column=0, sticky="w", padx=(12, 6), pady=pady)

        descricao = ctk.CTkFrame(frame, fg_color="transparent")
        descricao.grid(row=0, column=1, sticky="w", padx=6, pady=pady)
        ctk.CTkLabel(
            descricao,
            text=f"{veiculo.marca} {veiculo.modelo}",
            font=self.app.fonts.small_bold,
            text_color=COLORS["text"],
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            descricao,
            text=" • ".join(parte for parte in (veiculo.cor, veiculo.combustivel) if parte) or "—",
            font=self.app.fonts.tiny,
            text_color=COLORS["muted"],
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            frame,
            text=str(veiculo.ano),
            font=self.app.fonts.small,
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=2, sticky="w", padx=6, pady=pady)
        ctk.CTkLabel(
            frame,
            text=f"{veiculo.km:,}".replace(",", "."),
            font=self.app.fonts.small,
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=3, sticky="w", padx=6, pady=pady)
        ctk.CTkLabel(
            frame,
            text=veiculo.cliente.nome if veiculo.cliente else "—",
            font=self.app.fonts.small,
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=4, sticky="w", padx=6, pady=pady)

        ultima = self.app.context.ordens.listar(veiculo_id=veiculo.id, limite=1)
        ultima_cell = ctk.CTkFrame(frame, fg_color="transparent")
        ultima_cell.grid(row=0, column=5, sticky="w", padx=6, pady=pady)
        if ultima:
            ordem = ultima[0]
            status_badge(ultima_cell, ordem.status, self.app).pack(anchor="w")
            ctk.CTkLabel(
                ultima_cell,
                text=formatar_data(ordem.data_abertura),
                font=self.app.fonts.tiny,
                text_color=COLORS["muted"],
                anchor="w",
            ).pack(anchor="w", pady=(2, 0))
        else:
            ctk.CTkLabel(
                ultima_cell,
                text="Sem OS",
                font=self.app.fonts.tiny,
                text_color=COLORS["muted"],
            ).pack(anchor="w")

        acoes = ctk.CTkFrame(frame, fg_color="transparent")
        acoes.grid(row=0, column=6, sticky="e", padx=(6, 12), pady=pady)
        ctk.CTkButton(
            acoes,
            text="Editar",
            command=lambda v=veiculo: self._editar(v),
            width=62,
            height=28,
            corner_radius=7,
            font=self.app.fonts.button_small,
            **button_style("secondary"),
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            acoes,
            text="Histórico",
            command=lambda v=veiculo: self._historico(v),
            width=76,
            height=28,
            corner_radius=7,
            font=self.app.fonts.button_small,
            **button_style("secondary"),
        ).pack(side="left", padx=2)

    def _novo(self) -> None:
        dialogo = VeiculoDialog(self, self.app, cliente_id=self.cliente_id)
        self.wait_window(dialogo)
        if dialogo.result:
            self.app.notify("Veículo cadastrado com sucesso.")
            self.app.refresh_screens()

    def _editar(self, veiculo) -> None:
        dialogo = VeiculoDialog(self, self.app, veiculo)
        self.wait_window(dialogo)
        if dialogo.result:
            self.app.notify("Veículo atualizado.")
            self.app.refresh_screens()

    def _historico(self, veiculo) -> None:
        self.app.show_screen(
            "ordens",
            veiculo_id=veiculo.id,
            cliente_id=veiculo.cliente.id if veiculo.cliente else None,
        )
