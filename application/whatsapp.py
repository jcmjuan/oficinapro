"""Geração de mensagens e links do WhatsApp."""

from __future__ import annotations

import re
from urllib.parse import quote

from domain.ordem_servico import OrdemServico
from domain.oficina import Oficina
from domain.validators import formatar_brl


def normalizar_telefone_whatsapp(telefone: str) -> str:
    digitos = re.sub(r"\D", "", telefone or "")
    if not digitos:
        raise ValueError("Telefone não informado.")
    if digitos.startswith("55") and len(digitos) in (12, 13):
        return digitos
    if len(digitos) in (10, 11):
        return "55" + digitos
    return digitos


def montar_mensagem_orcamento(ordem: OrdemServico, oficina: Oficina) -> str:
    primeiro_nome = ordem.cliente.nome.split()[0]
    validade = "7 dias"
    return (
        f"Olá, {primeiro_nome}! Tudo bem?\n\n"
        f"Segue o resumo do orçamento da OS {ordem.numero} para o "
        f"{ordem.veiculo.marca} {ordem.veiculo.modelo} ({ordem.veiculo.placa}).\n\n"
        f"Itens: {ordem.quantidade_itens}\n"
        f"Total: {formatar_brl(ordem.total)}\n"
        f"Validade: {validade}\n\n"
        f"Qualquer dúvida, estamos à disposição.\n"
        f"{oficina.nome}\n"
        f"{oficina.telefone_formatado}"
    )


def montar_link_whatsapp(telefone: str, mensagem: str) -> str:
    numero = normalizar_telefone_whatsapp(telefone)
    return f"https://wa.me/{numero}?text={quote(mensagem, safe='')}"


def link_orcamento(ordem: OrdemServico, oficina: Oficina) -> str:
    return montar_link_whatsapp(
        ordem.cliente.telefone, montar_mensagem_orcamento(ordem, oficina)
    )
