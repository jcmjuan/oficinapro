"""Tela de clientes."""

from __future__ import annotations

from tkinter import messagebox

import customtkinter as ctk

from ..components import Badge, DataTable, button_style
from ..dialogs import ClienteDialog
from ..theme import COLORS
from ..utils import iniciais
from .base import BaseScreen


class ClientesScreen(BaseScreen):
    def __init__(self, master, app):
        super().__init__(master, app, "Clientes", "Cadastro de contatos e veículos")
        self.header.add_button("Novo cliente", self._novo, kind="primary", width=130, symbol="+")

        self.content.grid_rowconfigure(0, weight=0)
        self.content.grid_rowconfigure(1, weight=1)
        toolbar = ctk.CTkFrame(self.content, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        toolbar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            toolbar,
            text="Buscar",
            font=self.app.fonts.small_bold,
            text_color=COLORS["text"],
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        self.search = ctk.CTkEntry(
            toolbar,
            textvariable=self.search_var,
            placeholder_text="Nome, telefone, CPF/CNPJ ou e-mail...",
            height=36,
            corner_radius=8,
            font=self.app.fonts.body,
            border_color=COLORS["border"],
            fg_color=COLORS["surface"],
        )
        self.search.grid(row=0, column=1, sticky="ew")
        self.mostrar_inativos = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            toolbar,
            text="Mostrar inativos",
            variable=self.mostrar_inativos,
            command=self.refresh,
            font=self.app.fonts.small,
            text_color=COLORS["muted"],
            progress_color=COLORS["primary"],
            button_color=COLORS["surface"],
        ).grid(row=0, column=2, padx=(14, 0))

        self.table = DataTable(
            self.content,
            app,
            [
                ("Cliente", 4),
                ("Telefone", 2),
                ("E-mail", 3),
                ("Veículos", 1),
                ("Ações", 3),
            ],
            title="Base de clientes",
            subtitle="Contatos, veículos e histórico de atendimentos",
            empty_text="Nenhum cliente encontrado com os filtros atuais.",
        )
        self.table.grid(row=1, column=0, sticky="nsew")
        self._search_job = None

    def _on_search(self, *_args) -> None:
        if self._search_job is not None:
            try:
                self.after_cancel(self._search_job)
            except Exception:
                pass
        self._search_job = self.after(250, self.refresh)

    def refresh(self, **kwargs) -> None:
        contexto = self.app.context
        todos = contexto.clientes.listar(apenas_ativos=False)
        ativos = [c for c in todos if c.ativo]
        clientes = contexto.clientes.listar(
            busca=self.search_var.get(),
            apenas_ativos=not self.mostrar_inativos.get(),
        )
        self.header.set_title(
            "Clientes",
            f"{len(ativos)} clientes ativos • {sum(len(c.veiculos) for c in todos)} veículos vinculados",
        )
        self.table.set_rows(clientes, self._render_row)

    def _render_row(self, frame, cliente, _indice, pady) -> None:
        pessoa = ctk.CTkFrame(frame, fg_color="transparent")
        pessoa.grid(row=0, column=0, sticky="w", padx=(12, 6), pady=pady)
        ctk.CTkLabel(
            pessoa,
            text=iniciais(cliente.nome),
            width=34,
            height=34,
            corner_radius=17,
            fg_color=COLORS["surface_alt"],
            text_color=COLORS["primary"],
            font=self.app.fonts.small_bold,
        ).pack(side="left", padx=(0, 9))
        nomes = ctk.CTkFrame(pessoa, fg_color="transparent")
        nomes.pack(side="left")
        ctk.CTkLabel(
            nomes,
            text=cliente.nome,
            font=self.app.fonts.small_bold,
            text_color=COLORS["text"],
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            nomes,
            text=cliente.cpf_cnpj,
            font=self.app.fonts.tiny,
            text_color=COLORS["muted"],
            anchor="w",
        ).pack(anchor="w")
        if not cliente.ativo:
            Badge(nomes, "Inativo", COLORS["danger_bg"], COLORS["danger"], self.app).pack(anchor="w", pady=(2, 0))

        ctk.CTkLabel(
            frame,
            text=cliente.telefone_formatado,
            font=self.app.fonts.small,
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=1, sticky="w", padx=6, pady=pady)
        ctk.CTkLabel(
            frame,
            text=cliente.email or "—",
            font=self.app.fonts.small,
            text_color=COLORS["muted"],
            anchor="w",
        ).grid(row=0, column=2, sticky="w", padx=6, pady=pady)
        ctk.CTkLabel(
            frame,
            text=str(len(cliente.veiculos)),
            font=self.app.fonts.small_bold,
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=3, sticky="w", padx=6, pady=pady)

        acoes = ctk.CTkFrame(frame, fg_color="transparent")
        acoes.grid(row=0, column=4, sticky="e", padx=(6, 12), pady=pady)
        ctk.CTkButton(
            acoes,
            text="Editar",
            command=lambda c=cliente: self._editar(c),
            width=62,
            height=28,
            corner_radius=7,
            font=self.app.fonts.button_small,
            **button_style("secondary"),
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            acoes,
            text="Veículos",
            command=lambda c=cliente: self._ver_veiculos(c),
            width=72,
            height=28,
            corner_radius=7,
            font=self.app.fonts.button_small,
            **button_style("secondary"),
        ).pack(side="left", padx=2)
        if cliente.ativo:
            ctk.CTkButton(
                acoes,
                text="Inativar",
                command=lambda c=cliente: self._inativar(c),
                width=68,
                height=28,
                corner_radius=7,
                font=self.app.fonts.button_small,
                **button_style("danger"),
            ).pack(side="left", padx=2)
        else:
            ctk.CTkButton(
                acoes,
                text="Reativar",
                command=lambda c=cliente: self._reativar(c),
                width=72,
                height=28,
                corner_radius=7,
                font=self.app.fonts.button_small,
                **button_style("success"),
            ).pack(side="left", padx=2)

    def _novo(self) -> None:
        dialogo = ClienteDialog(self, self.app)
        self.wait_window(dialogo)
        if dialogo.result:
            self.app.notify("Cliente cadastrado com sucesso.")
            self.app.refresh_screens()

    def _editar(self, cliente) -> None:
        dialogo = ClienteDialog(self, self.app, cliente)
        self.wait_window(dialogo)
        if dialogo.result:
            self.app.notify("Cliente atualizado.")
            self.app.refresh_screens()

    def _inativar(self, cliente) -> None:
        if not messagebox.askyesno(
            "Inativar cliente",
            f"Inativar {cliente.nome}? O histórico de OS será preservado.",
            parent=self,
        ):
            return
        try:
            self.app.context.clientes.inativar(cliente.id)
            self.app.notify("Cliente inativado.")
            self.app.refresh_screens()
        except Exception as exc:
            messagebox.showerror("Não foi possível inativar", str(exc), parent=self)

    def _reativar(self, cliente) -> None:
        try:
            self.app.context.clientes.reativar(cliente.id)
            self.app.notify("Cliente reativado.")
            self.app.refresh_screens()
        except Exception as exc:
            messagebox.showerror("Não foi possível reativar", str(exc), parent=self)

    def _ver_veiculos(self, cliente) -> None:
        self.app.show_screen("veiculos", cliente_id=cliente.id)
