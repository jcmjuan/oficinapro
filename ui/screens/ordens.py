"""Tela de ordens de serviço."""

from __future__ import annotations

import customtkinter as ctk

from domain.status_os import StatusOS

from ..components import DataTable, button_style, status_badge
from ..theme import COLORS
from ..utils import formatar_brl, formatar_data
from .base import BaseScreen


class OrdensScreen(BaseScreen):
    def __init__(self, master, app):
        super().__init__(master, app, "Ordens de Serviço", "Fila de atendimento da oficina")
        self.header.add_button("Nova OS", self.app.nova_os, kind="primary", width=110, symbol="+")
        self.filtros = {"cliente_id": None, "veiculo_id": None, "mecanico_id": None}
        self._search_job = None
        self._labels_status = {
            "Todas": None,
            "Orçamento": StatusOS.ORCAMENTO,
            "Aprovada": StatusOS.APROVADA,
            "Em execução": StatusOS.EM_EXECUCAO,
            "Finalizada": StatusOS.FINALIZADA,
            "Cancelada": StatusOS.CANCELADA,
        }

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
            placeholder_text="Número da OS, cliente ou placa...",
            height=36,
            corner_radius=8,
            font=self.app.fonts.body,
            border_color=COLORS["border"],
            fg_color=COLORS["surface"],
        ).grid(row=0, column=1, sticky="ew")

        filtros = ctk.CTkFrame(self.content, fg_color="transparent")
        filtros.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        filtros.grid_columnconfigure(0, weight=1)
        self.status_seg = ctk.CTkSegmentedButton(
            filtros,
            values=list(self._labels_status),
            command=lambda _valor: self.refresh(),
            font=self.app.fonts.small,
            height=30,
            corner_radius=8,
            fg_color=COLORS["surface"],
            selected_color=COLORS["primary"],
            selected_hover_color=COLORS["primary_hover"],
            unselected_color=COLORS["surface"],
            unselected_hover_color=COLORS["surface_alt"],
            text_color=COLORS["text"],
        )
        self.status_seg.grid(row=0, column=0, sticky="w")
        self.status_seg.set("Todas")
        self.filter_label = ctk.CTkLabel(
            filtros,
            text="",
            font=self.app.fonts.small,
            text_color=COLORS["muted"],
            anchor="e",
        )
        self.filter_label.grid(row=0, column=1, sticky="e", padx=(10, 0))
        self.clear_filter = ctk.CTkButton(
            filtros,
            text="Limpar",
            command=self._limpar_filtro,
            width=66,
            height=28,
            corner_radius=7,
            font=self.app.fonts.button_small,
            **button_style("secondary"),
        )
        self.clear_filter.grid(row=0, column=2, sticky="e", padx=(8, 0))
        self.clear_filter.grid_remove()

        self.table = DataTable(
            self.content,
            app,
            [
                ("Nº", 1),
                ("Cliente", 3),
                ("Veículo", 2),
                ("Status", 2),
                ("Itens", 1),
                ("Total", 2),
                ("Abertura", 1),
                ("Ações", 3),
            ],
            title="Fila de atendimento",
            subtitle="Acompanhe orçamentos, execução e entregas em um só lugar",
            empty_text="Nenhuma ordem de serviço encontrada.",
        )
        self.table.grid(row=2, column=0, sticky="nsew")

    def _on_search(self, *_args) -> None:
        if self._search_job is not None:
            try:
                self.after_cancel(self._search_job)
            except Exception:
                pass
        self._search_job = self.after(250, self._atualizar_tabela)

    def _atualizar_tabela(self) -> None:
        """Atualiza apenas as linhas: a busca não altera os contadores do topo."""
        contexto = self.app.context
        status = self._labels_status.get(self.status_seg.get())
        ordens = contexto.ordens.listar(
            status=status,
            cliente_id=self.filtros["cliente_id"],
            veiculo_id=self.filtros["veiculo_id"],
            mecanico_id=self.filtros["mecanico_id"],
            busca=self.search_var.get(),
        )
        self.table.set_rows(ordens, self._render_row)

    def on_show(self, **kwargs) -> None:
        if any(chave in kwargs for chave in ("status", "cliente_id", "veiculo_id", "mecanico_id")):
            self.filtros = {
                "cliente_id": kwargs.get("cliente_id"),
                "veiculo_id": kwargs.get("veiculo_id"),
                "mecanico_id": kwargs.get("mecanico_id"),
            }
            status = kwargs.get("status")
            if status is not None:
                status_obj = StatusOS.from_value(status)
                for label, valor in self._labels_status.items():
                    if valor is status_obj:
                        self.status_seg.set(label)
                        break
            else:
                self.status_seg.set("Todas")
        else:
            self.filtros = {"cliente_id": None, "veiculo_id": None, "mecanico_id": None}
            self.status_seg.set("Todas")
        self.refresh()

    def _limpar_filtro(self) -> None:
        self.filtros = {"cliente_id": None, "veiculo_id": None, "mecanico_id": None}
        self.refresh()

    def refresh(self, **kwargs) -> None:
        contexto = self.app.context
        contagem = contexto.ordens.contar_por_status()
        abertas = (
            contagem.get(StatusOS.ORCAMENTO.value, 0)
            + contagem.get(StatusOS.APROVADA.value, 0)
            + contagem.get(StatusOS.EM_EXECUCAO.value, 0)
        )
        orcamentos = contagem.get(StatusOS.ORCAMENTO.value, 0)
        texto_abertas = "1 OS aberta" if abertas == 1 else f"{abertas} OS abertas"
        texto_orcamentos = (
            "1 orçamento aguardando aprovação"
            if orcamentos == 1
            else f"{orcamentos} orçamentos aguardando aprovação"
        )
        self.header.set_title(
            "Ordens de Serviço",
            f"{texto_abertas} • {texto_orcamentos}",
        )
        self._atualizar_filtro_label()
        self._atualizar_tabela()

    def _atualizar_filtro_label(self) -> None:
        partes = []
        contexto = self.app.context
        if self.filtros["cliente_id"]:
            try:
                partes.append(contexto.clientes.buscar_por_id(self.filtros["cliente_id"]).nome)
            except Exception:
                pass
        if self.filtros["veiculo_id"]:
            try:
                veiculo = contexto.veiculos.buscar_por_id(self.filtros["veiculo_id"])
                partes.append(f"{veiculo.marca} {veiculo.modelo} • {veiculo.placa}")
            except Exception:
                pass
        if self.filtros["mecanico_id"]:
            try:
                partes.append(contexto.mecanicos.buscar_por_id(self.filtros["mecanico_id"]).nome)
            except Exception:
                pass
        if partes:
            self.filter_label.configure(text="Filtro: " + " / ".join(partes))
            self.clear_filter.grid()
        else:
            self.filter_label.configure(text="")
            self.clear_filter.grid_remove()

    def _render_row(self, frame, ordem, _indice, pady) -> None:
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
            text=str(ordem.quantidade_itens),
            font=self.app.fonts.small,
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=4, sticky="w", padx=6, pady=pady)
        ctk.CTkLabel(
            frame,
            text=formatar_brl(ordem.total),
            font=self.app.fonts.small_bold,
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=5, sticky="w", padx=6, pady=pady)
        ctk.CTkLabel(
            frame,
            text=formatar_data(ordem.data_abertura),
            font=self.app.fonts.small,
            text_color=COLORS["muted"],
            anchor="w",
        ).grid(row=0, column=6, sticky="w", padx=6, pady=pady)

        acoes = ctk.CTkFrame(frame, fg_color="transparent")
        acoes.grid(row=0, column=7, sticky="e", padx=(6, 12), pady=pady)
        ctk.CTkButton(
            acoes,
            text="Abrir",
            command=lambda o=ordem: self.app.abrir_os(o.numero),
            width=58,
            height=27,
            corner_radius=7,
            font=self.app.fonts.button_small,
            **button_style("secondary"),
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            acoes,
            text="PDF",
            command=lambda o=ordem: self.app.gerar_pdf(o.numero),
            width=42,
            height=27,
            corner_radius=7,
            font=self.app.fonts.button_small,
            **button_style("secondary"),
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            acoes,
            text="WhatsApp",
            command=lambda o=ordem: self.app.abrir_whatsapp(o.numero),
            width=70,
            height=27,
            corner_radius=7,
            font=self.app.fonts.button_small,
            **button_style("secondary"),
        ).pack(side="left", padx=2)

    def _documento(self, ordem) -> None:
        self.app.abrir_documento(ordem)
