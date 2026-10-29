"""Componentes reutilizáveis da interface."""

from __future__ import annotations

from typing import Callable, Iterable, Sequence

import customtkinter as ctk

from domain.status_os import StatusOS

from .theme import COLORS, status_style


def clear_children(widget) -> None:
    for child in widget.winfo_children():
        child.destroy()


def button_style(kind: str) -> dict:
    if kind == "primary":
        return {
            "fg_color": COLORS["primary"],
            "hover_color": COLORS["primary_hover"],
            "text_color": "#FFFFFF",
        }
    if kind == "secondary":
        return {
            "fg_color": COLORS["surface"],
            "hover_color": COLORS["surface_alt"],
            "text_color": COLORS["text"],
            "border_width": 1,
            "border_color": COLORS["border"],
        }
    if kind == "ghost":
        return {
            "fg_color": "transparent",
            "hover_color": COLORS["surface_alt"],
            "text_color": COLORS["muted"],
        }
    if kind == "danger":
        return {
            "fg_color": COLORS["danger_bg"],
            "hover_color": "#FECACA",
            "text_color": COLORS["danger"],
        }
    if kind == "success":
        return {
            "fg_color": COLORS["success"],
            "hover_color": "#15803D",
            "text_color": "#FFFFFF",
        }
    return {}


class Card(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", COLORS["surface"])
        kwargs.setdefault("corner_radius", 14)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", COLORS["border"])
        super().__init__(master, **kwargs)


class PageHeader(ctk.CTkFrame):
    def __init__(self, master, app, title: str, subtitle: str = ""):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=app.fonts.h1,
            text_color=COLORS["text"],
            anchor="w",
        )
        self.title_label.grid(row=0, column=0, sticky="w")
        self.subtitle_label = ctk.CTkLabel(
            self,
            text=subtitle,
            font=app.fonts.small,
            text_color=COLORS["muted"],
            anchor="w",
        )
        self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(2, 0))
        self.actions = ctk.CTkFrame(self, fg_color="transparent", width=1, height=1)
        self.actions.grid(row=0, column=1, rowspan=2, sticky="e")

    def set_title(self, title: str, subtitle: str | None = None) -> None:
        self.title_label.configure(text=title)
        if subtitle is not None:
            self.subtitle_label.configure(text=subtitle)

    def add_button(
        self,
        text: str,
        command: Callable,
        *,
        kind: str = "primary",
        width: int = 120,
        symbol: str = "",
    ) -> ctk.CTkButton:
        label = f"{symbol}  {text}" if symbol else text
        button = ctk.CTkButton(
            self.actions,
            text=label,
            command=command,
            width=width,
            height=36,
            corner_radius=9,
            font=self.app.fonts.button,
            **button_style(kind),
        )
        button.pack(side="left", padx=(8, 0))
        return button

    def add_widget(self, widget) -> None:
        widget.pack(side="left", padx=(8, 0))


class StatCard(Card):
    def __init__(
        self,
        master,
        app,
        title: str,
        value: str = "—",
        foot: str = "",
        *,
        accent: str = COLORS["primary"],
        symbol: str = "●",
    ):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 0))
        top.grid_columnconfigure(0, weight=1)
        self.title_label = ctk.CTkLabel(
            top,
            text=title.upper(),
            font=app.fonts.tiny,
            text_color=COLORS["muted"],
            anchor="w",
        )
        self.title_label.grid(row=0, column=0, sticky="w")
        self.icon = ctk.CTkLabel(
            top,
            text=symbol,
            width=34,
            height=34,
            corner_radius=9,
            fg_color=COLORS["surface_alt"],
            text_color=accent,
            font=app.fonts.body_bold,
        )
        self.icon.grid(row=0, column=1, sticky="e")
        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=app.fonts.stat_small,
            text_color=COLORS["text"],
            anchor="w",
        )
        self.value_label.grid(row=1, column=0, sticky="w", padx=16, pady=(4, 0))
        self.foot_label = ctk.CTkLabel(
            self,
            text=foot,
            font=app.fonts.small,
            text_color=COLORS["muted"],
            anchor="w",
        )
        self.foot_label.grid(row=2, column=0, sticky="w", padx=16, pady=(2, 14))

    def set_values(self, value: str, foot: str | None = None) -> None:
        self.value_label.configure(text=value)
        if foot is not None:
            self.foot_label.configure(text=foot)


class Badge(ctk.CTkLabel):
    def __init__(self, master, text: str, bg: str, fg: str, app):
        super().__init__(
            master,
            text=text,
            fg_color=bg,
            text_color=fg,
            corner_radius=999,
            font=app.fonts.tiny,
            height=24,
        )


def status_badge(master, status: StatusOS | str, app) -> Badge:
    rotulo = status.rotulo if isinstance(status, StatusOS) else StatusOS.from_value(status).rotulo
    bg, fg = status_style(status)
    return Badge(master, rotulo, bg, fg, app)


class SectionHeader(ctk.CTkFrame):
    def __init__(
        self,
        master,
        app,
        title: str,
        subtitle: str = "",
        *,
        action_text: str = "",
        action_command: Callable | None = None,
        action_kind: str = "ghost",
    ):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            self,
            text=title,
            font=app.fonts.h3,
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        if subtitle:
            ctk.CTkLabel(
                self,
                text=subtitle,
                font=app.fonts.small,
                text_color=COLORS["muted"],
                anchor="w",
            ).grid(row=1, column=0, sticky="w", pady=(1, 0))
        if action_text and action_command:
            ctk.CTkButton(
                self,
                text=action_text,
                command=action_command,
                width=110,
                height=30,
                corner_radius=8,
                font=app.fonts.button_small,
                **button_style(action_kind),
            ).grid(row=0, column=1, rowspan=2, sticky="e")


class DataTable(Card):
    """Tabela simples com cabeçalho fixo e corpo rolável."""

    def __init__(
        self,
        master,
        app,
        columns: Sequence[tuple[str, int]],
        *,
        empty_text: str = "Nenhum registro encontrado.",
        row_pady: int = 10,
        title: str = "",
        subtitle: str = "",
    ):
        super().__init__(master)
        self.app = app
        self.columns = list(columns)
        self.empty_text = empty_text
        self.row_pady = row_pady
        self.grid_columnconfigure(0, weight=1)

        row_offset = 0
        if title:
            titulo = ctk.CTkFrame(self, fg_color="transparent")
            titulo.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 8))
            titulo.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                titulo,
                text=title,
                font=app.fonts.h3,
                text_color=COLORS["text"],
                anchor="w",
            ).grid(row=0, column=0, sticky="w")
            if subtitle:
                ctk.CTkLabel(
                    titulo,
                    text=subtitle,
                    font=app.fonts.small,
                    text_color=COLORS["muted"],
                    anchor="w",
                ).grid(row=1, column=0, sticky="w", pady=(1, 0))
            row_offset = 1

        self.grid_rowconfigure(row_offset + 1, weight=1)

        self.header = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface_alt"],
            corner_radius=0,
            height=38,
        )
        self.header.grid(row=row_offset, column=0, sticky="ew")
        for index, (title_col, weight) in enumerate(self.columns):
            self.header.grid_columnconfigure(index, weight=weight)
            ctk.CTkLabel(
                self.header,
                text=title_col.upper(),
                font=app.fonts.tiny,
                text_color=COLORS["muted"],
                anchor="w",
            ).grid(row=0, column=index, sticky="w", padx=(12, 6), pady=9)

        self.body = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=COLORS["slate_light"],
            scrollbar_button_hover_color=COLORS["muted"],
        )
        self.body.grid(row=row_offset + 1, column=0, sticky="nsew")

    def set_rows(self, rows: Iterable, row_builder: Callable) -> None:
        clear_children(self.body)
        rows = list(rows)
        if not rows:
            ctk.CTkLabel(
                self.body,
                text=self.empty_text,
                font=self.app.fonts.body,
                text_color=COLORS["muted"],
            ).pack(pady=36)
            return
        for index, row in enumerate(rows):
            frame = ctk.CTkFrame(
                self.body,
                fg_color=COLORS["surface"] if index % 2 == 0 else "#FCFDFE",
                corner_radius=0,
            )
            frame.pack(fill="x", pady=(0, 1))
            for col, (_, weight) in enumerate(self.columns):
                frame.grid_columnconfigure(col, weight=weight)
            row_builder(frame, row, index, self.row_pady)


class EmptyState(Card):
    def __init__(
        self,
        master,
        app,
        title: str,
        message: str,
        *,
        action_text: str = "",
        command: Callable | None = None,
        symbol: str = "○",
    ):
        super().__init__(master)
        ctk.CTkLabel(
            self,
            text=symbol,
            font=app.fonts.h1,
            text_color=COLORS["slate_light"],
        ).pack(pady=(24, 4))
        ctk.CTkLabel(
            self,
            text=title,
            font=app.fonts.h3,
            text_color=COLORS["text"],
        ).pack()
        ctk.CTkLabel(
            self,
            text=message,
            font=app.fonts.small,
            text_color=COLORS["muted"],
            wraplength=420,
        ).pack(pady=(4, 12))
        if action_text and command:
            ctk.CTkButton(
                self,
                text=action_text,
                command=command,
                width=140,
                height=34,
                corner_radius=8,
                font=app.fonts.button,
                **button_style("primary"),
            ).pack(pady=(0, 22))


class SummaryRow(ctk.CTkFrame):
    def __init__(self, master, app, label: str, value: str = "—", *, strong: bool = False):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.label = ctk.CTkLabel(
            self,
            text=label,
            font=app.fonts.small_bold if strong else app.fonts.small,
            text_color=COLORS["text"] if strong else COLORS["muted"],
            anchor="w",
        )
        self.label.grid(row=0, column=0, sticky="w")
        self.value = ctk.CTkLabel(
            self,
            text=value,
            font=app.fonts.body_bold if strong else app.fonts.body,
            text_color=COLORS["text"],
            anchor="e",
        )
        self.value.grid(row=0, column=1, sticky="e")

    def set_value(self, value: str) -> None:
        self.value.configure(text=value)


class ProgressLine(ctk.CTkFrame):
    def __init__(self, master, app, label: str, value: int, total: int, color: str):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            self,
            text=label,
            font=app.fonts.small,
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        self.value_label = ctk.CTkLabel(
            self,
            text=str(value),
            font=app.fonts.small_bold,
            text_color=COLORS["muted"],
            anchor="e",
        )
        self.value_label.grid(row=0, column=1, sticky="e")
        self.bar = ctk.CTkProgressBar(
            self,
            height=7,
            corner_radius=999,
            progress_color=color,
            fg_color=COLORS["border"],
        )
        self.bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(3, 0))
        self.set_values(value, total)

    def set_values(self, value: int, total: int) -> None:
        self.value_label.configure(text=str(value))
        self.bar.set(0 if total <= 0 else max(0.0, min(1.0, value / total)))


def divider(master) -> ctk.CTkFrame:
    return ctk.CTkFrame(master, height=1, fg_color=COLORS["border"], corner_radius=0)
