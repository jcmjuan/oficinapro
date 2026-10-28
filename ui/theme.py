"""Tema visual do OficinaPro (CustomTkinter)."""

from __future__ import annotations

from domain.status_os import StatusOS

COLORS = {
    "bg": "#F1F5F9",
    "surface": "#FFFFFF",
    "surface_alt": "#F8FAFC",
    "sidebar": "#0F172A",
    "sidebar_hover": "#1E293B",
    "sidebar_text": "#E2E8F0",
    "sidebar_muted": "#94A3B8",
    "primary": "#F97316",
    "primary_hover": "#EA580C",
    "primary_soft": "#FFF7ED",
    "text": "#1E293B",
    "muted": "#64748B",
    "border": "#E2E8F0",
    "success": "#16A34A",
    "success_bg": "#DCFCE7",
    "warning": "#D97706",
    "warning_bg": "#FEF3C7",
    "danger": "#DC2626",
    "danger_bg": "#FEE2E2",
    "info": "#2563EB",
    "info_bg": "#DBEAFE",
    "slate": "#475569",
    "slate_light": "#CBD5E1",
    "purple": "#7C3AED",
    "purple_bg": "#EDE9FE",
}

STATUS_STYLES: dict[str, tuple[str, str]] = {
    StatusOS.ORCAMENTO.value: (COLORS["warning_bg"], "#B45309"),
    StatusOS.APROVADA.value: (COLORS["success_bg"], "#15803D"),
    StatusOS.EM_EXECUCAO.value: (COLORS["info_bg"], "#1D4ED8"),
    StatusOS.FINALIZADA.value: ("#E2E8F0", "#334155"),
    StatusOS.CANCELADA.value: (COLORS["danger_bg"], "#B91C1C"),
}


def status_style(status: StatusOS | str) -> tuple[str, str]:
    valor = status.value if isinstance(status, StatusOS) else str(status)
    return STATUS_STYLES.get(valor, ("#E2E8F0", COLORS["text"]))


class Fonts:
    """Fontes criadas depois que a janela Tk existe."""

    def __init__(self) -> None:
        import customtkinter as ctk

        family = "Segoe UI"
        mono = "DejaVu Sans Mono"
        self.brand = ctk.CTkFont(family=family, size=20, weight="bold")
        self.brand_small = ctk.CTkFont(family=family, size=10, weight="bold")
        self.h1 = ctk.CTkFont(family=family, size=25, weight="bold")
        self.h2 = ctk.CTkFont(family=family, size=18, weight="bold")
        self.h3 = ctk.CTkFont(family=family, size=14, weight="bold")
        self.body = ctk.CTkFont(family=family, size=13)
        self.body_bold = ctk.CTkFont(family=family, size=13, weight="bold")
        self.small = ctk.CTkFont(family=family, size=11)
        self.small_bold = ctk.CTkFont(family=family, size=11, weight="bold")
        self.tiny = ctk.CTkFont(family=family, size=10)
        self.nav = ctk.CTkFont(family=family, size=13)
        self.nav_bold = ctk.CTkFont(family=family, size=13, weight="bold")
        self.stat = ctk.CTkFont(family=family, size=28, weight="bold")
        self.stat_small = ctk.CTkFont(family=family, size=22, weight="bold")
        self.button = ctk.CTkFont(family=family, size=12, weight="bold")
        self.button_small = ctk.CTkFont(family=family, size=11, weight="bold")
        self.mono = ctk.CTkFont(family=mono, size=11)
