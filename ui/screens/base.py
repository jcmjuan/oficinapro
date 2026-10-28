"""Base comum das telas."""

from __future__ import annotations

import customtkinter as ctk

from ..components import PageHeader
from ..theme import COLORS


class BaseScreen(ctk.CTkFrame):
    def __init__(self, master, app, title: str, subtitle: str = ""):
        super().__init__(master, fg_color=COLORS["bg"], corner_radius=0)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.header = PageHeader(self, app, title, subtitle)
        self.header.grid(row=0, column=0, sticky="ew", padx=28, pady=(22, 12))
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew", padx=28, pady=(0, 22))
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def on_show(self, **kwargs) -> None:
        self.refresh(**kwargs)

    def refresh(self, **kwargs) -> None:  # pragma: no cover - sobrescrito
        pass
