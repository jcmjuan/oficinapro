"""Janela principal e navegação do OficinaPro."""

from __future__ import annotations

from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

from .components import button_style
from .context import AppContext
from .dialogs import ClienteDialog, DocumentoDialog, NovaOSDialog
from .screens.clientes import ClientesScreen
from .screens.configuracoes import ConfiguracoesScreen
from .screens.dashboard import DashboardScreen
from .screens.editor_os import EditorOSScreen
from .screens.ordens import OrdensScreen
from .screens.relatorios import RelatoriosScreen
from .screens.veiculos import VeiculosScreen
from .theme import COLORS, Fonts
from .utils import abrir_arquivo, abrir_url


class Sidebar(ctk.CTkFrame):
    def __init__(self, app: "OficinaProApp"):
        super().__init__(app, width=236, fg_color=COLORS["sidebar"], corner_radius=0)
        self.app = app
        self.pack_propagate(False)
        self.grid_propagate(False)
        self.buttons: dict[str, ctk.CTkButton] = {}

        marca = ctk.CTkFrame(self, fg_color="transparent")
        marca.pack(fill="x", padx=16, pady=(22, 26))
        logo = ctk.CTkLabel(
            marca,
            text="OP",
            width=42,
            height=42,
            corner_radius=11,
            fg_color=COLORS["primary"],
            text_color="#FFFFFF",
            font=app.fonts.brand_small,
        )
        logo.pack(side="left")
        textos = ctk.CTkFrame(marca, fg_color="transparent")
        textos.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(
            textos,
            text="OficinaPro",
            font=app.fonts.brand,
            text_color="#FFFFFF",
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            textos,
            text="DevSolo Studio",
            font=app.fonts.tiny,
            text_color=COLORS["sidebar_muted"],
            anchor="w",
        ).pack(anchor="w")

        self._grupo("PRINCIPAL")
        self._item("dashboard", "Dashboard", "▦")
        self._item("ordens", "Ordens de Serviço", "▤")
        self._grupo("CADASTROS")
        self._item("clientes", "Clientes", "◉")
        self._item("veiculos", "Veículos", "▣")
        self._grupo("GESTÃO")
        self._item("relatorios", "Relatórios", "◔")
        self._item("configuracoes", "Configurações", "⚙")

        rodape = ctk.CTkFrame(self, fg_color="transparent")
        rodape.pack(side="bottom", fill="x", padx=16, pady=18)
        ctk.CTkFrame(rodape, height=1, fg_color=COLORS["sidebar_hover"]).pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            rodape,
            text="OficinaPro v1.0",
            font=app.fonts.small_bold,
            text_color=COLORS["sidebar_text"],
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            rodape,
            text="Banco local • SQLite",
            font=app.fonts.tiny,
            text_color=COLORS["sidebar_muted"],
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            rodape,
            text=Path(app.context.db_path).name,
            font=app.fonts.tiny,
            text_color=COLORS["sidebar_muted"],
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

    def _grupo(self, texto: str) -> None:
        ctk.CTkLabel(
            self,
            text=texto,
            font=self.app.fonts.tiny,
            text_color=COLORS["sidebar_muted"],
            anchor="w",
        ).pack(fill="x", padx=22, pady=(10, 4))

    def _item(self, chave: str, texto: str, simbolo: str) -> None:
        botao = ctk.CTkButton(
            self,
            text=f"{simbolo}   {texto}",
            command=lambda: self.app.show_screen(chave),
            height=40,
            corner_radius=8,
            anchor="w",
            font=self.app.fonts.nav,
            fg_color="transparent",
            hover_color=COLORS["sidebar_hover"],
            text_color=COLORS["sidebar_text"],
        )
        botao.pack(fill="x", padx=12, pady=1)
        botao.bind("<Enter>", lambda _event, destino=chave: self.app.prefetch_screen(destino))
        self.buttons[chave] = botao

    def set_active(self, chave: str) -> None:
        if chave == "editor_os":
            chave = "ordens"
        for nome, botao in self.buttons.items():
            ativo = nome == chave
            botao.configure(
                fg_color=COLORS["primary"] if ativo else "transparent",
                hover_color=COLORS["primary_hover"] if ativo else COLORS["sidebar_hover"],
                text_color="#FFFFFF" if ativo else COLORS["sidebar_text"],
                font=self.app.fonts.nav_bold if ativo else self.app.fonts.nav,
            )


class OficinaProApp(ctk.CTk):
    def __init__(self, db_path: str | Path = "oficinapro.db"):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        super().__init__()
        self.withdraw()
        self.title("OficinaPro v1.0 — Gestão de Oficina")
        self.geometry("1440x900")
        self.minsize(1180, 720)
        self.configure(fg_color=COLORS["bg"])
        self.fonts = Fonts()
        self.context = AppContext(db_path)
        self.screens: dict[str, object] = {}
        self._tela_atual: str | None = None
        self._notify_job = None
        self._build_layout()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        # A janela só aparece depois que a moldura (sidebar + barra de status)
        # está pronta; o conteúdo entra em seguida, já com o layout estável.
        self.update_idletasks()
        self.deiconify()
        self.after(10, lambda: self.show_screen("dashboard"))

    def _build_layout(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.sidebar = Sidebar(self)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.main = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, minsize=28)

        self.screen_host = ctk.CTkFrame(self.main, fg_color="transparent", corner_radius=0)
        self.screen_host.grid(row=0, column=0, sticky="nsew")
        self.screen_host.grid_columnconfigure(0, weight=1)
        self.screen_host.grid_rowconfigure(0, weight=1)

        barra = ctk.CTkFrame(self.main, height=28, fg_color=COLORS["surface"], corner_radius=0)
        barra.grid(row=1, column=0, sticky="ew")
        barra.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            barra,
            text=f"Banco: {Path(self.context.db_path).name}",
            font=self.fonts.tiny,
            text_color=COLORS["muted"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=12)
        self.status_label = ctk.CTkLabel(
            barra,
            text="Pronto",
            font=self.fonts.tiny,
            text_color=COLORS["muted"],
            anchor="e",
        )
        self.status_label.grid(row=0, column=1, sticky="e", padx=12)

    SCREENS = {
        "dashboard": DashboardScreen,
        "clientes": ClientesScreen,
        "veiculos": VeiculosScreen,
        "ordens": OrdensScreen,
        "editor_os": EditorOSScreen,
        "relatorios": RelatoriosScreen,
        "configuracoes": ConfiguracoesScreen,
    }

    def _criar_tela(self, nome: str):
        classe = self.SCREENS.get(nome)
        if classe is None:
            return None
        tela = classe(self.screen_host, self)
        self.screens[nome] = tela
        return tela

    def prefetch_screen(self, nome: str) -> None:
        """Cria a estrutura da tela antes do clique, sem carregar dados.

        Chamado no <Enter> dos itens da sidebar: quando o usuário clica, a
        tela já existe e só precisa receber os dados.
        """
        if nome in self.screens:
            return
        try:
            self._criar_tela(nome)
        except Exception:
            pass

    def show_screen(self, nome: str, **kwargs) -> None:
        tela = self.screens.get(nome)
        if tela is None:
            tela = self._criar_tela(nome)
        if tela is None:
            return
        if not tela.winfo_manager():
            tela.grid(row=0, column=0, sticky="nsew")
        tela.tkraise()
        tela.on_show(**kwargs)
        self._tela_atual = nome
        self.sidebar.set_active(nome)

    def refresh_screens(self, exclude: str | None = None) -> None:
        """Atualiza apenas a tela visível; as demais recarregam ao serem abertas.

        Reconstruir todas as telas a cada gravação custa caro. Como
        ``on_show()`` sempre recarrega os dados ao exibir, as telas ocultas
        podem esperar a próxima navegação.
        """
        tela = self.screens.get(self._tela_atual) if self._tela_atual else None
        if tela is None or self._tela_atual == exclude:
            return
        try:
            tela.refresh()
        except Exception:
            # Uma tela não deve derrubar as demais durante a atualização.
            pass

    def notify(self, mensagem: str, kind: str = "success") -> None:
        cores = {
            "success": COLORS["success"],
            "error": COLORS["danger"],
            "info": COLORS["muted"],
        }
        self.status_label.configure(text=mensagem, text_color=cores.get(kind, COLORS["muted"]))
        if self._notify_job is not None:
            try:
                self.after_cancel(self._notify_job)
            except Exception:
                pass
        self._notify_job = self.after(
            6000,
            lambda: self.status_label.configure(text="Pronto", text_color=COLORS["muted"]),
        )

    def novo_cliente(self) -> None:
        dialogo = ClienteDialog(self, self)
        self.wait_window(dialogo)
        if dialogo.result:
            self.notify("Cliente cadastrado com sucesso.")
            self.show_screen("clientes")
            self.refresh_screens(exclude="clientes")

    def nova_os(self, cliente_id: int | None = None, veiculo_id: int | None = None) -> None:
        dialogo = NovaOSDialog(self, self, cliente_id=cliente_id, veiculo_id=veiculo_id)
        self.wait_window(dialogo)
        if dialogo.result:
            self.notify(f"OS {dialogo.result} criada.")
            self.show_screen("editor_os", numero=dialogo.result)
            self.refresh_screens(exclude="editor_os")

    def abrir_os(self, numero: str) -> None:
        self.show_screen("editor_os", numero=numero)

    def abrir_documento(self, ordem) -> None:
        DocumentoDialog(self, self, ordem)

    def gerar_pdf(self, numero: str) -> None:
        try:
            caminho = self.context.orcamento_service.gerar_pdf(numero)
            self.notify(f"PDF gerado: {caminho}")
            if messagebox.askyesno(
                "PDF gerado",
                f"Orçamento gerado em:\n{caminho}\n\nDeseja abrir o arquivo?",
                parent=self,
            ):
                abrir_arquivo(caminho)
        except Exception as exc:
            messagebox.showerror("Não foi possível gerar o PDF", str(exc), parent=self)

    def abrir_whatsapp(self, numero: str) -> None:
        try:
            link = self.context.orcamento_service.link_whatsapp(numero)
            abrir_url(link)
            self.notify("WhatsApp aberto no navegador.")
        except Exception as exc:
            messagebox.showerror("Não foi possível abrir o WhatsApp", str(exc), parent=self)

    def _on_close(self) -> None:
        try:
            self.context.fechar()
        except Exception:
            pass
        self.destroy()


def run(db_path: str | Path = "oficinapro.db") -> None:
    app = OficinaProApp(db_path)
    app.mainloop()
