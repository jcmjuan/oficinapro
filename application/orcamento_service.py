"""Serviço de orçamento: PDF e WhatsApp."""

from __future__ import annotations

from pathlib import Path

from infrastructure.pdf.orcamento_pdf import PdfGenerator
from infrastructure.repositories.oficina_repository import OficinaRepository
from infrastructure.repositories.ordem_servico_repository import OrdemServicoRepository

from .whatsapp import link_orcamento, montar_link_whatsapp, montar_mensagem_orcamento


class OrcamentoService:
    def __init__(
        self,
        os_repo: OrdemServicoRepository,
        oficina_repo: OficinaRepository,
        pdf: PdfGenerator | None = None,
    ) -> None:
        self.ordens = os_repo
        self.oficina_repo = oficina_repo
        self.pdf = pdf or PdfGenerator()

    def gerar_pdf(self, numero: str, destino: str | Path | None = None) -> Path:
        ordem = self.ordens.obter(numero)
        oficina = self.oficina_repo.obter()
        if destino is None:
            destino = Path("orcamentos") / f"OS-{ordem.numero}.pdf"
        return self.pdf.gerar_orcamento(ordem, oficina, destino)

    def mensagem_whatsapp(self, numero: str) -> str:
        ordem = self.ordens.obter(numero)
        oficina = self.oficina_repo.obter()
        return montar_mensagem_orcamento(ordem, oficina)

    def link_whatsapp(self, numero: str) -> str:
        ordem = self.ordens.obter(numero)
        oficina = self.oficina_repo.obter()
        return link_orcamento(ordem, oficina)

    def link_whatsapp_para(self, numero: str, telefone: str) -> str:
        ordem = self.ordens.obter(numero)
        oficina = self.oficina_repo.obter()
        return montar_link_whatsapp(telefone, montar_mensagem_orcamento(ordem, oficina))
