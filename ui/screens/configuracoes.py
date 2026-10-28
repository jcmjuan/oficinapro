"""Tela de configurações, equipe e backup."""

from __future__ import annotations

import sqlite3
import sys
from decimal import Decimal
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from domain.oficina import Oficina
from infrastructure.seed import seed_demo

from ..components import Badge, Card, DataTable, SectionHeader, button_style
from ..dialogs import MecanicoDialog
from ..theme import COLORS
from ..utils import abrir_arquivo, formatar_percentual, iniciais, para_decimal
from .base import BaseScreen


class ConfiguracoesScreen(BaseScreen):
    def __init__(self, master, app):
        super().__init__(master, app, "Configurações", "Oficina, equipe, backup e sistema")
        self.content.grid_rowconfigure(0, weight=1)
        self.tabs = ctk.CTkTabview(
            self.content,
            fg_color=COLORS["surface"],
            segmented_button_fg_color=COLORS["surface_alt"],
            segmented_button_selected_color=COLORS["primary"],
            segmented_button_selected_hover_color=COLORS["primary_hover"],
            segmented_button_unselected_color=COLORS["surface_alt"],
            segmented_button_unselected_hover_color=COLORS["border"],
            text_color=COLORS["text"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        self.tabs.grid(row=0, column=0, sticky="nsew")
        self.tab_oficina = self.tabs.add("Oficina")
        self.tab_equipe = self.tabs.add("Equipe")
        self.tab_backup = self.tabs.add("Backup")
        self.tab_sistema = self.tabs.add("Sistema")
        self.tabs.set("Oficina")
        self._build_oficina()
        self._build_equipe()
        self._build_backup()
        self._build_sistema()

    # ------------------------------------------------------------------ Oficina
    def _build_oficina(self) -> None:
        scroll = ctk.CTkScrollableFrame(self.tab_oficina, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        scroll.grid_columnconfigure(0, weight=1)
        card = Card(scroll)
        card.grid(row=0, column=0, sticky="ew", pady=(6, 0))
        SectionHeader(card, self.app, "Dados da oficina", "Informações usadas em orçamentos e recibos").pack(fill="x", padx=18, pady=(16, 8))

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=18, pady=(0, 8))
        form.grid_columnconfigure(1, weight=1)
        self.oficina_entries = {}
        campos = [
            ("nome", "Nome *", ""),
            ("cnpj", "CNPJ *", ""),
            ("telefone", "Telefone", ""),
            ("endereco", "Endereço", ""),
            ("taxa", "Taxa horária padrão (R$)", ""),
            ("comissao", "Comissão padrão (%)", ""),
        ]
        for linha, (chave, rotulo, placeholder) in enumerate(campos):
            ctk.CTkLabel(
                form,
                text=rotulo,
                font=self.app.fonts.small_bold,
                text_color=COLORS["text"],
                anchor="w",
            ).grid(row=linha, column=0, sticky="w", padx=(0, 14), pady=6)
            entry = ctk.CTkEntry(
                form,
                height=34,
                corner_radius=7,
                font=self.app.fonts.body,
                placeholder_text=placeholder,
                border_color=COLORS["border"],
            )
            entry.grid(row=linha, column=1, sticky="ew", pady=6)
            self.oficina_entries[chave] = entry

        ctk.CTkButton(
            card,
            text="Salvar alterações",
            command=self._salvar_oficina,
            width=150,
            height=36,
            corner_radius=8,
            font=self.app.fonts.button,
            **button_style("primary"),
        ).pack(anchor="e", padx=18, pady=(4, 16))

    def _carregar_oficina(self) -> None:
        oficina = self.app.context.configuracao_service.obter_oficina()
        valores = {
            "nome": oficina.nome,
            "cnpj": oficina.cnpj,
            "telefone": oficina.telefone_formatado,
            "endereco": oficina.endereco,
            "taxa": f"{oficina.taxa_horaria_padrao:.2f}".replace(".", ","),
            "comissao": f"{(oficina.comissao_padrao * 100):.1f}".replace(".", ","),
        }
        for chave, valor in valores.items():
            entry = self.oficina_entries[chave]
            entry.delete(0, "end")
            entry.insert(0, valor)

    def _salvar_oficina(self) -> None:
        try:
            atual = self.app.context.configuracao_service.obter_oficina()
            nova = Oficina(
                self.oficina_entries["nome"].get(),
                self.oficina_entries["cnpj"].get(),
                telefone=self.oficina_entries["telefone"].get().strip() or None,
                endereco=self.oficina_entries["endereco"].get().strip() or None,
                taxa_horaria_padrao=para_decimal(self.oficina_entries["taxa"].get()),
                comissao_padrao=para_decimal(self.oficina_entries["comissao"].get()) / Decimal("100"),
            )
            nova.id = atual.id
            self.app.context.configuracao_service.salvar_oficina(nova)
            self.app.notify("Dados da oficina atualizados.")
            self.app.refresh_screens()
        except Exception as exc:
            messagebox.showerror("Não foi possível salvar", str(exc), parent=self)

    # ------------------------------------------------------------------- Equipe
    def _build_equipe(self) -> None:
        self.tab_equipe.grid_rowconfigure(1, weight=1)
        self.tab_equipe.grid_columnconfigure(0, weight=1)
        toolbar = ctk.CTkFrame(self.tab_equipe, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(8, 10))
        toolbar.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            toolbar,
            text="Equipe técnica",
            font=self.app.fonts.h3,
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=4)
        self.mostrar_inativos_equipe = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            toolbar,
            text="Mostrar inativos",
            variable=self.mostrar_inativos_equipe,
            command=self._carregar_equipe,
            font=self.app.fonts.small,
            text_color=COLORS["muted"],
            progress_color=COLORS["primary"],
            button_color=COLORS["surface"],
        ).grid(row=0, column=1, sticky="e", padx=(4, 10))
        ctk.CTkButton(
            toolbar,
            text="+ Novo mecânico",
            command=self._novo_mecanico,
            width=130,
            height=32,
            corner_radius=8,
            font=self.app.fonts.button_small,
            **button_style("primary"),
        ).grid(row=0, column=2, sticky="e", padx=4)
        self.equipe_table = DataTable(
            self.tab_equipe,
            self.app,
            [("Mecânico", 3), ("Registro", 1), ("Especialidade", 2), ("Taxa", 1), ("Ações", 2)],
            title="",
            empty_text="Nenhum mecânico ativo.",
        )
        self.equipe_table.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 8))

    def _carregar_equipe(self) -> None:
        mecanicos = self.app.context.mecanicos.listar(
            apenas_ativos=not self.mostrar_inativos_equipe.get()
        )
        self.equipe_table.set_rows(mecanicos, self._render_mecanico)

    def _render_mecanico(self, frame, mecanico, _indice, pady) -> None:
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
        ctk.CTkLabel(nomes, text=mecanico.nome, font=self.app.fonts.small_bold, text_color=COLORS["text"], anchor="w").pack(anchor="w")
        ctk.CTkLabel(nomes, text=mecanico.email or "—", font=self.app.fonts.tiny, text_color=COLORS["muted"], anchor="w").pack(anchor="w")
        if not mecanico.ativo:
            Badge(nomes, "Inativo", COLORS["danger_bg"], COLORS["danger"], self.app).pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(frame, text=mecanico.registro, font=self.app.fonts.mono, text_color=COLORS["text"], anchor="w").grid(row=0, column=1, sticky="w", padx=6, pady=pady)
        ctk.CTkLabel(frame, text=mecanico.especialidade or "—", font=self.app.fonts.small, text_color=COLORS["muted"], anchor="w").grid(row=0, column=2, sticky="w", padx=6, pady=pady)
        ctk.CTkLabel(frame, text=formatar_percentual(mecanico.taxa_comissao), font=self.app.fonts.small_bold, text_color=COLORS["text"], anchor="w").grid(row=0, column=3, sticky="w", padx=6, pady=pady)
        acoes = ctk.CTkFrame(frame, fg_color="transparent")
        acoes.grid(row=0, column=4, sticky="e", padx=(6, 12), pady=pady)
        ctk.CTkButton(
            acoes,
            text="Editar",
            command=lambda m=mecanico: self._editar_mecanico(m),
            width=62,
            height=28,
            corner_radius=7,
            font=self.app.fonts.button_small,
            **button_style("secondary"),
        ).pack(side="left", padx=2)
        if mecanico.ativo:
            ctk.CTkButton(
                acoes,
                text="Inativar",
                command=lambda m=mecanico: self._inativar_mecanico(m),
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
                command=lambda m=mecanico: self._reativar_mecanico(m),
                width=72,
                height=28,
                corner_radius=7,
                font=self.app.fonts.button_small,
                **button_style("success"),
            ).pack(side="left", padx=2)

    def _novo_mecanico(self) -> None:
        dialogo = MecanicoDialog(self, self.app)
        self.wait_window(dialogo)
        if dialogo.result:
            self.app.notify("Mecânico cadastrado.")
            self.app.refresh_screens()

    def _editar_mecanico(self, mecanico) -> None:
        dialogo = MecanicoDialog(self, self.app, mecanico)
        self.wait_window(dialogo)
        if dialogo.result:
            self.app.notify("Mecânico atualizado.")
            self.app.refresh_screens()

    def _inativar_mecanico(self, mecanico) -> None:
        if not messagebox.askyesno(
            "Inativar mecânico",
            f"Inativar {mecanico.nome}? As OS já registradas serão preservadas.",
            parent=self,
        ):
            return
        try:
            self.app.context.mecanicos.inativar(mecanico.id)
            self.app.notify("Mecânico inativado.")
            self.app.refresh_screens()
        except Exception as exc:
            messagebox.showerror("Não foi possível inativar", str(exc), parent=self)

    def _reativar_mecanico(self, mecanico) -> None:
        try:
            self.app.context.mecanicos.reativar(mecanico.id)
            self.app.notify("Mecânico reativado.")
            self.app.refresh_screens()
        except Exception as exc:
            messagebox.showerror("Não foi possível reativar", str(exc), parent=self)

    # ------------------------------------------------------------------- Backup
    def _build_backup(self) -> None:
        scroll = ctk.CTkScrollableFrame(self.tab_backup, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        scroll.grid_columnconfigure(0, weight=1)
        card = Card(scroll)
        card.grid(row=0, column=0, sticky="ew", pady=(6, 0))
        SectionHeader(card, self.app, "Backup e restauração", "Cópias de segurança do banco SQLite").pack(fill="x", padx=18, pady=(16, 8))
        ctk.CTkLabel(
            card,
            text=(
                "O backup usa VACUUM INTO, produzindo uma cópia consistente mesmo com o sistema aberto. "
                "A restauração valida a integridade do arquivo antes de substituir o banco atual."
            ),
            font=self.app.fonts.small,
            text_color=COLORS["muted"],
            anchor="w",
            justify="left",
            wraplength=760,
        ).pack(fill="x", padx=18, pady=(0, 12))
        botoes = ctk.CTkFrame(card, fg_color="transparent")
        botoes.pack(fill="x", padx=18, pady=(0, 16))
        ctk.CTkButton(
            botoes,
            text="Fazer backup agora",
            command=self._fazer_backup,
            width=150,
            height=34,
            corner_radius=8,
            font=self.app.fonts.button,
            **button_style("primary"),
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            botoes,
            text="Restaurar backup",
            command=self._restaurar_backup,
            width=140,
            height=34,
            corner_radius=8,
            font=self.app.fonts.button,
            **button_style("secondary"),
        ).pack(side="left", padx=8)
        ctk.CTkButton(
            botoes,
            text="Abrir pasta",
            command=self._abrir_pasta_backups,
            width=110,
            height=34,
            corner_radius=8,
            font=self.app.fonts.button,
            **button_style("secondary"),
        ).pack(side="left", padx=8)

        perigo = Card(scroll)
        perigo.grid(row=1, column=0, sticky="ew", pady=(14, 0))
        SectionHeader(perigo, self.app, "Dados demonstrativos", "Use com cuidado: a operação apaga os dados atuais").pack(fill="x", padx=18, pady=(16, 8))
        ctk.CTkButton(
            perigo,
            text="Recriar base demonstrativa",
            command=self._resetar_demo,
            width=190,
            height=34,
            corner_radius=8,
            font=self.app.fonts.button,
            **button_style("danger"),
        ).pack(anchor="w", padx=18, pady=(0, 16))

    def _fazer_backup(self) -> None:
        try:
            caminho = self.app.context.configuracao_service.fazer_backup()
            self.app.notify(f"Backup criado: {caminho}")
            messagebox.showinfo("Backup criado", f"Arquivo gerado em:\n{caminho}", parent=self)
        except Exception as exc:
            messagebox.showerror("Não foi possível fazer backup", str(exc), parent=self)

    def _restaurar_backup(self) -> None:
        caminho = filedialog.askopenfilename(
            parent=self,
            title="Selecionar backup",
            filetypes=[("Banco SQLite", "*.db"), ("Todos os arquivos", "*.*")],
        )
        if not caminho:
            return
        if not messagebox.askyesno(
            "Restaurar backup",
            "Substituir o banco atual pelo backup selecionado?",
            parent=self,
        ):
            return
        try:
            self.app.context.configuracao_service.restaurar_backup(caminho)
            self.app.notify("Backup restaurado com sucesso.")
            self.app.refresh_screens()
        except Exception as exc:
            messagebox.showerror("Não foi possível restaurar", str(exc), parent=self)

    def _abrir_pasta_backups(self) -> None:
        pasta = Path("backups")
        pasta.mkdir(parents=True, exist_ok=True)
        try:
            abrir_arquivo(pasta)
        except Exception as exc:
            messagebox.showerror("Não foi possível abrir a pasta", str(exc), parent=self)

    def _resetar_demo(self) -> None:
        if not messagebox.askyesno(
            "Recriar base demonstrativa",
            "Todos os dados atuais serão apagados e a seed da Etapa 2 será recarregada. Continuar?",
            parent=self,
        ):
            return
        try:
            seed_demo(self.app.context.db, forcar=True)
            self.app.notify("Base demonstrativa recriada.")
            self.app.refresh_screens()
        except Exception as exc:
            messagebox.showerror("Não foi possível recriar", str(exc), parent=self)

    # ------------------------------------------------------------------ Sistema
    def _build_sistema(self) -> None:
        scroll = ctk.CTkScrollableFrame(self.tab_sistema, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        scroll.grid_columnconfigure(0, weight=1)
        card = Card(scroll)
        card.grid(row=0, column=0, sticky="ew", pady=(6, 0))
        SectionHeader(card, self.app, "Informações do sistema", "Ambiente de execução e banco de dados").pack(fill="x", padx=18, pady=(16, 8))
        self.sistema_labels = {}
        for chave, rotulo in (
            ("versao", "OficinaPro"),
            ("python", "Python"),
            ("sqlite", "SQLite"),
            ("schema", "Versão do schema"),
            ("banco", "Banco de dados"),
            ("pasta", "Pasta do projeto"),
        ):
            linha = ctk.CTkFrame(card, fg_color="transparent")
            linha.pack(fill="x", padx=18, pady=3)
            linha.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(linha, text=rotulo, font=self.app.fonts.small, text_color=COLORS["muted"], anchor="w", width=130).grid(row=0, column=0, sticky="w")
            valor = ctk.CTkLabel(linha, text="—", font=self.app.fonts.small, text_color=COLORS["text"], anchor="w")
            valor.grid(row=0, column=1, sticky="w")
            self.sistema_labels[chave] = valor
        ctk.CTkLabel(card, text="", height=10).pack()

    def _carregar_sistema(self) -> None:
        try:
            schema = self.app.context.db.buscar_um("PRAGMA user_version")[0]
        except Exception:
            schema = "—"
        valores = {
            "versao": "1.0.0 • Etapa Final",
            "python": sys.version.split()[0],
            "sqlite": sqlite3.sqlite_version,
            "schema": str(schema),
            "banco": str(self.app.context.db_path.resolve()),
            "pasta": str(Path.cwd()),
        }
        for chave, valor in valores.items():
            self.sistema_labels[chave].configure(text=valor)

    def refresh(self, **kwargs) -> None:
        self._carregar_oficina()
        self._carregar_equipe()
        self._carregar_sistema()
