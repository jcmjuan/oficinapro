"""Editor de ordem de serviço."""

from __future__ import annotations

from tkinter import messagebox

import customtkinter as ctk

from domain.status_os import StatusOS
from domain.tipo_item import TipoItem
from domain.validators import formatar_brl

from ..components import Badge, Card, SectionHeader, SummaryRow, button_style, clear_children, divider, status_badge
from ..dialogs import ItemMaoObraDialog, ItemPecaDialog, PromptDialog
from ..theme import COLORS
from ..utils import descricao_transicao, formatar_data, formatar_data_hora, para_decimal
from .base import BaseScreen


class EditorOSScreen(BaseScreen):
    def __init__(self, master, app):
        super().__init__(master, app, "Ordem de Serviço", "Detalhes, itens e ciclo de vida")
        self.header.add_button("Voltar", self._voltar, kind="ghost", width=80)
        self.header.add_button("PDF", self._pdf, kind="secondary", width=70)
        self.header.add_button("WhatsApp", self._whatsapp, kind="secondary", width=100)
        self.header.add_button("Documento", self._documento, kind="primary", width=110)
        self.numero: str | None = None
        self.ordem = None
        self.scroll = ctk.CTkScrollableFrame(
            self.content,
            fg_color="transparent",
            scrollbar_button_color=COLORS["slate_light"],
        )
        self.scroll.grid(row=0, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

    def on_show(self, **kwargs) -> None:
        self.numero = kwargs.get("numero")
        self.refresh()

    def refresh(self, **kwargs) -> None:
        clear_children(self.scroll)
        if not self.numero:
            self._estado_vazio()
            return
        try:
            self.ordem = self.app.context.ordem_service.obter(self.numero)
        except Exception as exc:
            self._estado_vazio(str(exc))
            return
        self.header.set_title(
            f"OS {self.ordem.numero}",
            f"{self.ordem.cliente.nome} • {self.ordem.veiculo.marca} {self.ordem.veiculo.modelo} • {self.ordem.veiculo.placa}",
        )
        self._resumo()
        self._itens()
        self._rodape()
        self._historico()

    def _estado_vazio(self, mensagem: str = "Selecione uma OS na fila de atendimento.") -> None:
        card = Card(self.scroll)
        card.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            card,
            text="Nenhuma OS carregada",
            font=self.app.fonts.h2,
            text_color=COLORS["text"],
        ).pack(pady=(26, 4))
        ctk.CTkLabel(
            card,
            text=mensagem,
            font=self.app.fonts.small,
            text_color=COLORS["muted"],
            wraplength=420,
        ).pack(pady=(0, 14))
        ctk.CTkButton(
            card,
            text="Nova OS",
            command=self.app.nova_os,
            width=130,
            height=34,
            corner_radius=8,
            font=self.app.fonts.button,
            **button_style("primary"),
        ).pack(pady=(0, 24))

    def _resumo(self) -> None:
        ordem = self.ordem
        card = Card(self.scroll)
        card.pack(fill="x", pady=(0, 12))
        card.grid_columnconfigure(0, weight=1)

        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.grid(row=0, column=0, columnspan=4, sticky="ew", padx=18, pady=(16, 8))
        topo.grid_columnconfigure(0, weight=1)
        esquerda = ctk.CTkFrame(topo, fg_color="transparent")
        esquerda.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            esquerda,
            text=f"OS {ordem.numero}",
            font=self.app.fonts.h2,
            text_color=COLORS["text"],
            anchor="w",
        ).pack(side="left")
        status_badge(esquerda, ordem.status, self.app).pack(side="left", padx=(10, 0))
        ctk.CTkLabel(
            topo,
            text=formatar_brl(ordem.total),
            font=self.app.fonts.h2,
            text_color=COLORS["text"],
            anchor="e",
        ).grid(row=0, column=1, sticky="e")

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.grid(row=1, column=0, columnspan=4, sticky="ew", padx=18, pady=(0, 16))
        for col in range(4):
            info.grid_columnconfigure(col, weight=1)
        self._bloco(info, 0, "Cliente", ordem.cliente.nome, ordem.cliente.telefone_formatado, ordem.cliente.cpf_cnpj)
        self._bloco(
            info,
            1,
            "Veículo",
            f"{ordem.veiculo.marca} {ordem.veiculo.modelo}",
            f"{ordem.veiculo.placa} • {ordem.veiculo.ano}",
            f"{ordem.veiculo.km:,} km".replace(",", "."),
        )
        self._bloco(info, 2, "Responsável", ordem.mecanico.nome, ordem.mecanico.registro, ordem.mecanico.especialidade)
        self._bloco(
            info,
            3,
            "Abertura",
            formatar_data(ordem.data_abertura),
            formatar_data(ordem.data_finalizacao) if ordem.data_finalizacao else "Em andamento",
            f"Criada por {ordem.criado_por}" if ordem.criado_por else "",
        )

    def _bloco(self, master, col: int, titulo: str, linha1: str, linha2: str, linha3: str = "") -> None:
        bloco = ctk.CTkFrame(master, fg_color="transparent")
        bloco.grid(row=0, column=col, sticky="nw", padx=(0, 12))
        ctk.CTkLabel(bloco, text=titulo.upper(), font=self.app.fonts.tiny, text_color=COLORS["muted"], anchor="w").pack(anchor="w")
        ctk.CTkLabel(bloco, text=linha1, font=self.app.fonts.small_bold, text_color=COLORS["text"], anchor="w").pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(bloco, text=linha2, font=self.app.fonts.small, text_color=COLORS["muted"], anchor="w").pack(anchor="w")
        if linha3:
            ctk.CTkLabel(bloco, text=linha3, font=self.app.fonts.small, text_color=COLORS["muted"], anchor="w").pack(anchor="w")

    def _itens(self) -> None:
        ordem = self.ordem
        card = Card(self.scroll)
        card.pack(fill="x", pady=(0, 12))
        cabecalho = ctk.CTkFrame(card, fg_color="transparent")
        cabecalho.pack(fill="x", padx=16, pady=(14, 8))
        cabecalho.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            cabecalho,
            text="Itens da OS",
            font=self.app.fonts.h3,
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            cabecalho,
            text="Peças e serviços que compõem o orçamento",
            font=self.app.fonts.small,
            text_color=COLORS["muted"],
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(1, 0))
        botoes = ctk.CTkFrame(cabecalho, fg_color="transparent")
        botoes.grid(row=0, column=1, rowspan=2, sticky="e")
        editavel = ordem.status is StatusOS.ORCAMENTO
        ctk.CTkButton(
            botoes,
            text="+ Peça",
            command=self._adicionar_peca,
            width=80,
            height=30,
            corner_radius=8,
            font=self.app.fonts.button_small,
            state="normal" if editavel else "disabled",
            **button_style("secondary"),
        ).pack(side="left", padx=3)
        ctk.CTkButton(
            botoes,
            text="+ Mão de obra",
            command=self._adicionar_mao,
            width=116,
            height=30,
            corner_radius=8,
            font=self.app.fonts.button_small,
            state="normal" if editavel else "disabled",
            **button_style("secondary"),
        ).pack(side="left", padx=3)

        header = ctk.CTkFrame(card, fg_color=COLORS["surface_alt"], corner_radius=0)
        header.pack(fill="x", padx=16)
        for col, (titulo, weight) in enumerate(
            [("Tipo", 1), ("Descrição", 4), ("Qtd/Horas", 1), ("Unitário", 1), ("Subtotal", 1), ("", 0)]
        ):
            header.grid_columnconfigure(col, weight=weight)
            ctk.CTkLabel(
                header,
                text=titulo.upper(),
                font=self.app.fonts.tiny,
                text_color=COLORS["muted"],
                anchor="w",
            ).grid(row=0, column=col, sticky="w", padx=8, pady=7)

        if not ordem.itens:
            ctk.CTkLabel(
                card,
                text="Nenhum item adicionado. Use os botões acima para montar o orçamento.",
                font=self.app.fonts.small,
                text_color=COLORS["muted"],
            ).pack(pady=24)
        for indice, item in enumerate(ordem.itens):
            linha = ctk.CTkFrame(card, fg_color="transparent", corner_radius=0)
            linha.pack(fill="x", padx=16)
            for col, weight in enumerate([1, 4, 1, 1, 1, 0]):
                linha.grid_columnconfigure(col, weight=weight)
            eh_peca = item.tipo() is TipoItem.PECA
            bg, fg = (
                (COLORS["purple_bg"], COLORS["purple"])
                if eh_peca
                else (COLORS["warning_bg"], COLORS["warning"])
            )
            Badge(linha, item.rotulo_tipo, bg, fg, self.app).grid(row=0, column=0, sticky="w", padx=8, pady=8)
            descricao = ctk.CTkFrame(linha, fg_color="transparent")
            descricao.grid(row=0, column=1, sticky="w", padx=8, pady=8)
            ctk.CTkLabel(
                descricao,
                text=item.descricao,
                font=self.app.fonts.small,
                text_color=COLORS["text"],
                anchor="w",
            ).pack(anchor="w")
            detalhe = item.detalhe
            if detalhe:
                ctk.CTkLabel(
                    descricao,
                    text=detalhe,
                    font=self.app.fonts.tiny,
                    text_color=COLORS["muted"],
                    anchor="w",
                ).pack(anchor="w")
            qtd = item.quantidade_formatada
            ctk.CTkLabel(linha, text=qtd, font=self.app.fonts.small, text_color=COLORS["text"], anchor="w").grid(row=0, column=2, sticky="w", padx=8, pady=8)
            ctk.CTkLabel(linha, text=formatar_brl(item.valor_unitario), font=self.app.fonts.small, text_color=COLORS["text"], anchor="w").grid(row=0, column=3, sticky="w", padx=8, pady=8)
            ctk.CTkLabel(linha, text=formatar_brl(item.subtotal), font=self.app.fonts.small_bold, text_color=COLORS["text"], anchor="w").grid(row=0, column=4, sticky="w", padx=8, pady=8)
            if editavel:
                ctk.CTkButton(
                    linha,
                    text="×",
                    command=lambda i=indice: self._remover_item(i),
                    width=26,
                    height=26,
                    corner_radius=6,
                    font=self.app.fonts.small_bold,
                    **button_style("danger"),
                ).grid(row=0, column=5, sticky="e", padx=(0, 8), pady=8)
            if indice < len(ordem.itens) - 1:
                divider(card).pack(fill="x", padx=16)

    def _rodape(self) -> None:
        ordem = self.ordem
        bottom = ctk.CTkFrame(self.scroll, fg_color="transparent")
        bottom.pack(fill="x", pady=(0, 12))
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)

        obs = Card(bottom)
        obs.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        SectionHeader(obs, self.app, "Observações", "Relato do cliente e combinados").pack(fill="x", padx=16, pady=(14, 8))
        self.obs_text = ctk.CTkTextbox(
            obs,
            height=120,
            corner_radius=8,
            font=self.app.fonts.body,
            border_width=1,
            border_color=COLORS["border"],
            fg_color=COLORS["surface"],
        )
        self.obs_text.pack(fill="x", padx=16)
        self.obs_text.insert("1.0", ordem.observacoes)
        ctk.CTkButton(
            obs,
            text="Salvar observações",
            command=self._salvar_observacoes,
            width=140,
            height=32,
            corner_radius=8,
            font=self.app.fonts.button_small,
            **button_style("secondary"),
        ).pack(anchor="e", padx=16, pady=(8, 14))

        financeiro = Card(bottom)
        financeiro.grid(row=0, column=1, sticky="nsew", padx=(7, 0))
        SectionHeader(financeiro, self.app, "Resumo financeiro", "Cálculo automático da OS").pack(fill="x", padx=16, pady=(14, 8))
        corpo = ctk.CTkFrame(financeiro, fg_color="transparent")
        corpo.pack(fill="x", padx=16)
        SummaryRow(corpo, self.app, "Peças", formatar_brl(ordem.subtotal_pecas)).pack(fill="x", pady=1)
        SummaryRow(corpo, self.app, "Mão de obra", formatar_brl(ordem.subtotal_mao_obra)).pack(fill="x", pady=1)
        SummaryRow(corpo, self.app, "Subtotal", formatar_brl(ordem.subtotal)).pack(fill="x", pady=1)
        divider(corpo).pack(fill="x", pady=6)

        desconto_frame = ctk.CTkFrame(corpo, fg_color="transparent")
        desconto_frame.pack(fill="x", pady=(0, 4))
        desconto_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            desconto_frame,
            text="Desconto (R$)",
            font=self.app.fonts.small,
            text_color=COLORS["muted"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        self.desconto_entry = ctk.CTkEntry(
            desconto_frame,
            width=110,
            height=30,
            corner_radius=7,
            font=self.app.fonts.small,
            border_color=COLORS["border"],
        )
        self.desconto_entry.grid(row=0, column=1, sticky="e")
        self.desconto_entry.insert(0, f"{ordem.desconto:.2f}".replace(".", ","))
        self.desconto_entry.configure(state="normal" if ordem.status is StatusOS.ORCAMENTO else "disabled")
        ctk.CTkButton(
            desconto_frame,
            text="Aplicar",
            command=self._aplicar_desconto,
            width=64,
            height=30,
            corner_radius=7,
            font=self.app.fonts.button_small,
            state="normal" if ordem.status is StatusOS.ORCAMENTO else "disabled",
            **button_style("secondary"),
        ).grid(row=0, column=2, sticky="e", padx=(6, 0))

        divider(corpo).pack(fill="x", pady=6)
        SummaryRow(corpo, self.app, "Total", formatar_brl(ordem.total), strong=True).pack(fill="x", pady=(0, 8))

        acoes = ctk.CTkFrame(financeiro, fg_color="transparent")
        acoes.pack(fill="x", padx=16, pady=(0, 14))
        if ordem.status is StatusOS.ORCAMENTO:
            ctk.CTkButton(acoes, text="Aprovar OS", command=self._aprovar, height=34, corner_radius=8, font=self.app.fonts.button, **button_style("success")).pack(fill="x", pady=3)
            ctk.CTkButton(acoes, text="Cancelar OS", command=self._cancelar, height=32, corner_radius=8, font=self.app.fonts.button_small, **button_style("danger")).pack(fill="x", pady=3)
        elif ordem.status is StatusOS.APROVADA:
            ctk.CTkButton(acoes, text="Iniciar execução", command=self._iniciar, height=34, corner_radius=8, font=self.app.fonts.button, **button_style("primary")).pack(fill="x", pady=3)
            ctk.CTkButton(acoes, text="Cancelar OS", command=self._cancelar, height=32, corner_radius=8, font=self.app.fonts.button_small, **button_style("danger")).pack(fill="x", pady=3)
        elif ordem.status is StatusOS.EM_EXECUCAO:
            ctk.CTkButton(acoes, text="Finalizar OS", command=self._finalizar, height=34, corner_radius=8, font=self.app.fonts.button, **button_style("success")).pack(fill="x", pady=3)
            ctk.CTkButton(acoes, text="Cancelar OS", command=self._cancelar, height=32, corner_radius=8, font=self.app.fonts.button_small, **button_style("danger")).pack(fill="x", pady=3)
        elif ordem.status is StatusOS.FINALIZADA:
            ctk.CTkLabel(
                acoes,
                text=f"OS finalizada em {formatar_data(ordem.data_finalizacao)}",
                font=self.app.fonts.small,
                text_color=COLORS["success"],
            ).pack(pady=4)
            ctk.CTkButton(acoes, text="Abrir recibo", command=self._documento, height=32, corner_radius=8, font=self.app.fonts.button_small, **button_style("secondary")).pack(fill="x", pady=3)
        elif ordem.status is StatusOS.CANCELADA:
            ctk.CTkLabel(
                acoes,
                text=f"OS cancelada em {formatar_data(ordem.data_cancelamento)}\n{ordem.motivo_cancelamento or ''}",
                font=self.app.fonts.small,
                text_color=COLORS["danger"],
                justify="left",
            ).pack(anchor="w", pady=4)

    def _historico(self) -> None:
        ordem = self.ordem
        card = Card(self.scroll)
        card.pack(fill="x", pady=(0, 12))
        SectionHeader(card, self.app, "Histórico de status", "Trilha append-only de transições").pack(fill="x", padx=16, pady=(14, 8))
        corpo = ctk.CTkFrame(card, fg_color="transparent")
        corpo.pack(fill="x", padx=16, pady=(0, 14))
        for registro in ordem.historico:
            linha = ctk.CTkFrame(corpo, fg_color="transparent")
            linha.pack(fill="x", pady=2)
            linha.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(
                linha,
                text=formatar_data_hora(registro.data_hora),
                font=self.app.fonts.tiny,
                text_color=COLORS["muted"],
                width=110,
                anchor="w",
            ).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(
                linha,
                text=descricao_transicao(registro),
                font=self.app.fonts.small,
                text_color=COLORS["text"],
                anchor="w",
            ).grid(row=0, column=1, sticky="w", padx=8)
            detalhe = " • ".join(parte for parte in (registro.usuario, registro.motivo) if parte)
            if detalhe:
                ctk.CTkLabel(
                    linha,
                    text=detalhe,
                    font=self.app.fonts.tiny,
                    text_color=COLORS["muted"],
                    anchor="e",
                ).grid(row=0, column=2, sticky="e")

    def _adicionar_peca(self) -> None:
        if not self.ordem:
            return
        dialogo = ItemPecaDialog(self, self.app, self.ordem.numero)
        self.wait_window(dialogo)
        if dialogo.result:
            self.app.notify("Peça adicionada ao orçamento.")
            self.app.refresh_screens()

    def _adicionar_mao(self) -> None:
        if not self.ordem:
            return
        dialogo = ItemMaoObraDialog(self, self.app, self.ordem.numero, self.ordem)
        self.wait_window(dialogo)
        if dialogo.result:
            self.app.notify("Mão de obra adicionada ao orçamento.")
            self.app.refresh_screens()

    def _remover_item(self, indice: int) -> None:
        if not self.ordem:
            return
        if not messagebox.askyesno("Remover item", "Remover este item do orçamento?", parent=self):
            return
        try:
            self.app.context.ordem_service.remover_item(self.ordem.numero, indice)
            self.app.notify("Item removido.")
            self.app.refresh_screens()
        except Exception as exc:
            messagebox.showerror("Não foi possível remover", str(exc), parent=self)

    def _aplicar_desconto(self) -> None:
        if not self.ordem:
            return
        try:
            valor = para_decimal(self.desconto_entry.get())
            self.app.context.ordem_service.aplicar_desconto(self.ordem.numero, valor)
            self.app.notify("Desconto aplicado.")
            self.app.refresh_screens()
        except Exception as exc:
            messagebox.showerror("Desconto inválido", str(exc), parent=self)

    def _salvar_observacoes(self) -> None:
        if not self.ordem:
            return
        try:
            self.app.context.ordem_service.atualizar_observacoes(
                self.ordem.numero,
                self.obs_text.get("1.0", "end").strip(),
            )
            self.app.notify("Observações salvas.")
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Não foi possível salvar", str(exc), parent=self)

    def _aprovar(self) -> None:
        if not self.ordem:
            return
        if not messagebox.askyesno("Aprovar OS", "Aprovar este orçamento e liberar a execução?", parent=self):
            return
        try:
            self.app.context.ordem_service.aprovar(self.ordem.numero, usuario="interface")
            self.app.notify("OS aprovada.")
            self.app.refresh_screens()
        except Exception as exc:
            messagebox.showerror("Não foi possível aprovar", str(exc), parent=self)

    def _iniciar(self) -> None:
        if not self.ordem:
            return
        if not messagebox.askyesno("Iniciar execução", "Iniciar a execução desta OS?", parent=self):
            return
        try:
            self.app.context.ordem_service.iniciar(self.ordem.numero, usuario="interface")
            self.app.notify("Execução iniciada.")
            self.app.refresh_screens()
        except Exception as exc:
            messagebox.showerror("Não foi possível iniciar", str(exc), parent=self)

    def _finalizar(self) -> None:
        if not self.ordem:
            return
        dialogo = PromptDialog(
            self,
            self.app,
            "Finalizar OS",
            "Quilometragem de saída",
            initial=str(self.ordem.veiculo.km),
            numeric=True,
            confirm_text="Finalizar",
        )
        self.wait_window(dialogo)
        if dialogo.result is None:
            return
        try:
            self.app.context.ordem_service.finalizar(
                self.ordem.numero,
                km_saida=dialogo.result,
                usuario="interface",
            )
            self.app.notify("OS finalizada.")
            self.app.refresh_screens()
        except Exception as exc:
            messagebox.showerror("Não foi possível finalizar", str(exc), parent=self)

    def _cancelar(self) -> None:
        if not self.ordem:
            return
        dialogo = PromptDialog(
            self,
            self.app,
            "Cancelar OS",
            "Motivo do cancelamento",
            multiline=True,
            confirm_text="Cancelar OS",
        )
        self.wait_window(dialogo)
        if dialogo.result is None:
            return
        try:
            self.app.context.ordem_service.cancelar(
                self.ordem.numero,
                dialogo.result,
                usuario="interface",
            )
            self.app.notify("OS cancelada.")
            self.app.refresh_screens()
        except Exception as exc:
            messagebox.showerror("Não foi possível cancelar", str(exc), parent=self)

    def _voltar(self) -> None:
        self.app.show_screen("ordens")

    def _documento(self) -> None:
        if self.ordem:
            self.app.abrir_documento(self.ordem)

    def _pdf(self) -> None:
        if self.ordem:
            self.app.gerar_pdf(self.ordem.numero)

    def _whatsapp(self) -> None:
        if self.ordem:
            self.app.abrir_whatsapp(self.ordem.numero)
