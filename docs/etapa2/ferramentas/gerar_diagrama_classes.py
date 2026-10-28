#!/usr/bin/env python3
"""Gera o diagrama de classes do OficinaPro em SVG.

O layout é fixo para manter o diagrama legível em PDF. A fonte Mermaid
(classes-detalhado.mmd) continua disponível para edição rápida; este script
produz a versão de impressão com grade controlada.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "diagramas" / "classes-detalhado.svg"

WIDTH = 1400
HEIGHT = 1220
FONT = "Helvetica, Arial, sans-serif"
INK = "#1E293B"
MUTED = "#475569"
EDGE = "#475569"


@dataclass
class ClassBox:
    name: str
    x: float
    y: float
    w: float
    color: str
    title_color: str
    stereotype: str = ""
    attrs: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)

    @property
    def title_h(self) -> float:
        return 42 if self.stereotype else 34

    @property
    def h(self) -> float:
        base = self.title_h + 18 + len(self.attrs) * 16 + 14
        if self.methods:
            base += 12 + len(self.methods) * 16
        return base

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def bottom(self) -> float:
        return self.y + self.h


def text(x: float, y: float, value: str, size: float = 12, fill: str = INK,
         anchor: str = "start", weight: str = "400", style: str = "normal") -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
        f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" '
        f'font-style="{style}">{escape(value)}</text>'
    )


def box_svg(b: ClassBox) -> str:
    h = b.h
    r = 7
    parts: list[str] = []
    # Corpo
    parts.append(
        f'<rect x="{b.x}" y="{b.y}" width="{b.w}" height="{h}" rx="{r}" '
        f'fill="#FFFFFF" stroke="{b.color}" stroke-width="1.6"/>'
    )
    # Cabeçalho com cantos superiores arredondados
    th = b.title_h
    parts.append(
        f'<path d="M {b.x + r} {b.y} H {b.x + b.w - r} Q {b.x + b.w} {b.y} '
        f'{b.x + b.w} {b.y + r} V {b.y + th} H {b.x} V {b.y + r} '
        f'Q {b.x} {b.y} {b.x + r} {b.y} Z" fill="{b.title_color}" '
        f'stroke="{b.color}" stroke-width="1.6"/>'
    )
    # Nome e estereótipo
    if b.stereotype:
        parts.append(text(b.cx, b.y + 19, b.name, 15, INK, "middle", "700"))
        parts.append(text(b.cx, b.y + 34, b.stereotype, 10, MUTED, "middle", "400", "italic"))
    else:
        parts.append(text(b.cx, b.y + 23, b.name, 15, INK, "middle", "700"))

    # Atributos
    y = b.y + th + 16
    for attr in b.attrs:
        parts.append(text(b.x + 10, y, attr, 12, INK))
        y += 16

    if b.methods:
        # Separador
        sep = b.y + th + 18 + len(b.attrs) * 16 + 4
        parts.append(
            f'<line x1="{b.x}" y1="{sep:.1f}" x2="{b.x + b.w}" y2="{sep:.1f}" '
            f'stroke="{b.color}" stroke-width="1"/>'
        )

        # Métodos
        y = sep + 18
        for method in b.methods:
            parts.append(text(b.x + 10, y, method, 12, INK))
            y += 16
    return "\n".join(parts)


def polyline(points: list[tuple[float, float]], kind: str, dashed: bool = False) -> str:
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    attrs = [
        f'points="{pts}"',
        'fill="none"',
        f'stroke="{EDGE}"',
        'stroke-width="1.4"',
        'stroke-linejoin="round"',
        'stroke-linecap="round"',
    ]
    if kind == "inheritance":
        attrs.append('marker-end="url(#triangle)"')
    elif kind == "composition":
        attrs.append('marker-start="url(#diamond)"')
    elif kind == "association":
        attrs.append('marker-end="url(#openArrow)"')
    elif kind == "dependency":
        attrs.append('marker-end="url(#openArrow)"')
        dashed = True
    if dashed:
        attrs.append('stroke-dasharray="6 5"')
    return f'<polyline {" ".join(attrs)}/>'


def label(cx: float, cy: float, value: str) -> str:
    width = max(34, len(value) * 5.7 + 10)
    x = cx - width / 2
    y = cy - 11
    return (
        f'<g><rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="16" '
        f'rx="3" fill="#FFFFFF" fill-opacity="0.94"/>'
        f'{text(cx, cy + 1, value, 9.5, MUTED, "middle")}</g>'
    )


def svg_defs() -> str:
    return f"""
  <defs>
    <marker id="triangle" viewBox="0 0 12 12" refX="11" refY="6"
            markerWidth="13" markerHeight="13" orient="auto-start-reverse">
      <path d="M1,1 L11,6 L1,11 Z" fill="#FFFFFF" stroke="{EDGE}" stroke-width="1.4"/>
    </marker>
    <marker id="openArrow" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="9" markerHeight="9" orient="auto-start-reverse">
      <path d="M1,1 L9,5 L1,9" fill="none" stroke="{EDGE}" stroke-width="1.4"/>
    </marker>
    <marker id="diamond" viewBox="0 0 14 10" refX="1" refY="5"
            markerWidth="14" markerHeight="10" orient="auto-start-reverse">
      <path d="M1,5 L7,1 L13,5 L7,9 Z" fill="{EDGE}" stroke="{EDGE}" stroke-width="1"/>
    </marker>
  </defs>
"""


def build() -> str:
    boxes = {
        "Oficina": ClassBox(
            "Oficina", 545, 20, 310, "#3B82F6", "#DBEAFE",
            attrs=[
                "- nome : str",
                "- cnpj : str",
                "- telefone : str",
                "- endereco : str",
                "- taxaHorariaPadrao : float",
                "- comissaoPadrao : float",
            ],
            methods=[
                "+ adicionarCliente(c) void",
                "+ adicionarMecanico(m) void",
                "+ emitirOrdemServico(c, v) OrdemServico",
                "+ relatorioComissoes(inicio, fim) list",
            ],
        ),
        "Pessoa": ClassBox(
            "Pessoa", 20, 250, 310, "#A855F7", "#F3E8FF",
            stereotype="<<abstract>>",
            attrs=["- nome : str", "- telefone : str", "- email : str"],
            methods=["+ resumo()* str", "- __validarContato() bool"],
        ),
        "ItemOS": ClassBox(
            "ItemOS", 1070, 250, 310, "#22C55E", "#DCFCE7",
            stereotype="<<abstract>>",
            attrs=["- descricao : str", "- quantidade : float", "- valorUnitario : float"],
            methods=["+ calcularSubtotal()* float", "+ descrever()* str"],
        ),
        "Cliente": ClassBox(
            "Cliente", 20, 500, 310, "#14B8A6", "#CCFBF1",
            attrs=["- cpfCnpj : str", "- endereco : str", "- veiculos : list<Veiculo>"],
            methods=[
                "+ adicionarVeiculo(v) void",
                "+ listarVeiculos() list<Veiculo>",
                "+ resumo() str",
            ],
        ),
        "Mecanico": ClassBox(
            "Mecanico", 370, 500, 310, "#F97316", "#FFEDD5",
            attrs=["- registro : str", "- especialidade : str", "- taxaComissao : float"],
            methods=["+ calcularComissao(valor) float", "+ resumo() str"],
        ),
        "Veiculo": ClassBox(
            "Veiculo", 720, 500, 310, "#06B6D4", "#CFFAFE",
            attrs=[
                "- placa : str",
                "- marca : str",
                "- modelo : str",
                "- ano : int",
                "- km : int",
                "- cliente : Cliente",
            ],
            methods=[
                "+ atualizarKm(km) void",
                "+ historico() list<OrdemServico>",
                "+ descricao() str",
            ],
        ),
        "Peca": ClassBox(
            "Peca", 1070, 500, 310, "#8B5CF6", "#EDE9FE",
            attrs=["- codigo : str", "- fornecedor : str"],
            methods=["+ calcularSubtotal() float", "+ descrever() str"],
        ),
        "OrdemServico": ClassBox(
            "OrdemServico", 370, 780, 660, "#EAB308", "#FEF9C3",
            attrs=[
                "- numero : str",
                "- status : StatusOS",
                "- cliente : Cliente",
                "- veiculo : Veiculo",
                "- responsavel : Mecanico",
                "- __itens : list<ItemOS>",
                "- desconto : float",
                "- dataAbertura : datetime",
                "- dataFinalizacao : datetime",
                "- observacoes : str",
            ],
            methods=[
                "+ adicionarItem(item) void",
                "+ removerItem(item) void",
                "+ calcularSubtotal() float",
                "+ calcularTotal() float",
                "+ aprovar() void",
                "+ iniciar() void",
                "+ finalizar() void",
                "+ cancelar() void",
                "+ podeTransicionar(novo) bool",
                "- __recalcular_total() void",
                "- __validar_transicao(novo) void",
            ],
        ),
        "StatusOS": ClassBox(
            "StatusOS", 20, 780, 310, "#22C55E", "#DCFCE7",
            stereotype="<<enumeration>>",
            attrs=["ORCAMENTO", "APROVADA", "EM_EXECUCAO", "FINALIZADA", "CANCELADA"],
            methods=[],
        ),
        "MaoDeObra": ClassBox(
            "MaoDeObra", 1070, 780, 310, "#EF4444", "#FEE2E2",
            attrs=["- horas : float", "- taxaHoraria : float", "- executor : Mecanico"],
            methods=["+ calcularSubtotal() float", "+ descrever() str"],
        ),
    }

    p = boxes["Pessoa"]
    c = boxes["Cliente"]
    m = boxes["Mecanico"]
    v = boxes["Veiculo"]
    i = boxes["ItemOS"]
    pe = boxes["Peca"]
    mo = boxes["MaoDeObra"]
    os_ = boxes["OrdemServico"]
    st = boxes["StatusOS"]

    edges = [
        # Herança
        polyline([(p.cx, p.bottom), (p.cx, c.y)], "inheritance"),
        polyline([(p.x + p.w, p.y + p.h / 2), (350, p.y + p.h / 2),
                  (350, m.y + m.h / 2), (m.x, m.y + m.h / 2)], "inheritance"),
        polyline([(i.cx, i.bottom), (i.cx, pe.y)], "inheritance"),
        polyline([(i.x + i.w, i.y + i.h / 2), (1395, i.y + i.h / 2),
                  (1395, mo.y + mo.h / 2), (mo.x + mo.w, mo.y + mo.h / 2)], "inheritance"),
        # Associações
        polyline([(c.x + c.w, c.y + c.h / 2), (365, c.y + c.h / 2), (365, 470),
                  (700, 470), (700, v.y + v.h / 2), (v.x, v.y + v.h / 2)], "association"),
        polyline([(c.cx, c.bottom), (c.cx, 730), (400, 730), (400, os_.y)], "association"),
        polyline([(m.cx, m.bottom), (m.cx, os_.y)], "association"),
        polyline([(v.cx, v.bottom), (v.cx, os_.y)], "association"),
        polyline([(600, m.bottom), (600, 740), (1040, 740),
                  (1040, mo.y + mo.h / 2), (mo.x, mo.y + mo.h / 2)], "association"),
        # Composição
        polyline([(os_.x + os_.w, 850), (1050, 850), (1050, i.y + i.h / 2),
                  (i.x, i.y + i.h / 2)], "composition"),
        # Dependência
        polyline([(os_.x, 850), (st.x + st.w, 850)], "dependency"),
    ]

    labels = [
        label(532, 460, "1  possui  0..*"),
        label(300, 722, "1  solicita  0..*"),
        label(m.cx + 12, 700, "1  responsável  0..*"),
        label(v.cx + 12, 710, "1  recebe  0..*"),
        label(820, 758, "1  executa  0..*"),
        label(1055, 450, "1  contém  1..*"),
        label(350, 840, "usa"),
    ]

    note = (
        f'<g>{text(880, 76, "A Oficina agrega clientes,", 11, MUTED, "start", "400", "italic")}'
        f'{text(880, 92, "mecânicos e ordens de serviço.", 11, MUTED, "start", "400", "italic")}</g>'
    )

    body = [svg_defs(), f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#FFFFFF"/>']
    body.extend(edges)
    body.extend(box_svg(b) for b in boxes.values())
    body.extend(labels)
    body.append(note)

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" '
        f'aria-label="Diagrama de classes do OficinaPro">\n'
        + "\n".join(body)
        + "\n</svg>\n"
    )


def build_compact() -> str:
    """Versão enxuta para a seção principal do documento."""
    width, height = 1050, 1020
    boxes = {
        "Oficina": ClassBox(
            "Oficina", 365, 20, 320, "#3B82F6", "#DBEAFE",
            attrs=["- nome : str", "- taxaHorariaPadrao : float"],
            methods=["+ emitirOrdemServico() OrdemServico", "+ relatorioComissoes() list"],
        ),
        "Pessoa": ClassBox(
            "Pessoa", 20, 220, 320, "#A855F7", "#F3E8FF",
            stereotype="<<abstract>>",
            attrs=["- nome : str", "- telefone : str"],
            methods=["+ resumo()* str"],
        ),
        "ItemOS": ClassBox(
            "ItemOS", 710, 220, 320, "#22C55E", "#DCFCE7",
            stereotype="<<abstract>>",
            attrs=["- descricao : str", "- valorUnitario : float"],
            methods=["+ calcularSubtotal()* float"],
        ),
        "Cliente": ClassBox(
            "Cliente", 20, 430, 320, "#14B8A6", "#CCFBF1",
            attrs=["- cpfCnpj : str", "- veiculos : list<Veiculo>"],
            methods=["+ adicionarVeiculo(v) void"],
        ),
        "Mecanico": ClassBox(
            "Mecanico", 365, 430, 320, "#F97316", "#FFEDD5",
            attrs=["- registro : str", "- taxaComissao : float"],
            methods=["+ calcularComissao(valor) float"],
        ),
        "Veiculo": ClassBox(
            "Veiculo", 710, 430, 320, "#06B6D4", "#CFFAFE",
            attrs=["- placa : str", "- modelo : str"],
            methods=["+ historico() list"],
        ),
        "StatusOS": ClassBox(
            "StatusOS", 20, 680, 320, "#22C55E", "#DCFCE7",
            stereotype="<<enumeration>>",
            attrs=["ORCAMENTO", "APROVADA", "EM_EXECUCAO", "FINALIZADA", "CANCELADA"],
        ),
        "OrdemServico": ClassBox(
            "OrdemServico", 365, 680, 320, "#EAB308", "#FEF9C3",
            attrs=["- numero : str", "- status : StatusOS", "- __itens : list<ItemOS>", "- desconto : float"],
            methods=[
                "+ calcularTotal() float",
                "+ aprovar() void",
                "+ finalizar() void",
                "- __recalcular_total() void",
            ],
        ),
        "Peca": ClassBox(
            "Peca", 710, 680, 320, "#8B5CF6", "#EDE9FE",
            attrs=["- codigo : str"],
            methods=["+ calcularSubtotal() float"],
        ),
        "MaoDeObra": ClassBox(
            "MaoDeObra", 710, 880, 320, "#EF4444", "#FEE2E2",
            attrs=["- horas : float", "- executor : Mecanico"],
            methods=["+ calcularSubtotal() float"],
        ),
    }

    p, c, m, v = boxes["Pessoa"], boxes["Cliente"], boxes["Mecanico"], boxes["Veiculo"]
    i, pe, mo = boxes["ItemOS"], boxes["Peca"], boxes["MaoDeObra"]
    os_, st = boxes["OrdemServico"], boxes["StatusOS"]

    edges = [
        # Herança
        polyline([(p.cx, p.bottom), (p.cx, c.y)], "inheritance"),
        polyline([(p.x + p.w, p.y + p.h / 2), (350, p.y + p.h / 2),
                  (350, m.y + m.h / 2), (m.x, m.y + m.h / 2)], "inheritance"),
        polyline([(i.x + i.w, i.y + i.h / 2), (1040, i.y + i.h / 2),
                  (1040, pe.y + pe.h / 2), (pe.x + pe.w, pe.y + pe.h / 2)], "inheritance"),
        polyline([(i.x + i.w, i.y + i.h / 2), (1045, i.y + i.h / 2),
                  (1045, mo.y + mo.h / 2), (mo.x + mo.w, mo.y + mo.h / 2)], "inheritance"),
        # Associações
        polyline([(c.x + c.w, c.y + c.h / 2), (355, c.y + c.h / 2), (355, 400),
                  (700, 400), (700, v.y + v.h / 2), (v.x, v.y + v.h / 2)], "association"),
        polyline([(c.cx, c.bottom), (c.cx, 620), (400, 620), (400, os_.y)], "association"),
        polyline([(m.cx, m.bottom), (m.cx, os_.y)], "association"),
        polyline([(v.cx, v.bottom), (v.cx, 620), (685, 620), (685, os_.y)], "association"),
        # Composição
        polyline([(os_.x + os_.w, 750), (700, 750), (700, 330),
                  (i.x, 330)], "composition"),
        # Dependência
        polyline([(os_.x, 750), (st.x + st.w, 750)], "dependency"),
    ]

    labels = [
        label(527, 390, "1  possui  0..*"),
        label(300, 612, "1  solicita  0..*"),
        label(m.cx + 12, 610, "1  responsável  0..*"),
        label(v.cx + 12, 610, "1  recebe  0..*"),
        label(705, 600, "1  contém  1..*"),
        label(350, 740, "usa"),
    ]

    note = (
        f'<g>{text(700, 76, "A Oficina agrega clientes,", 11, MUTED, "start", "400", "italic")}'
        f'{text(700, 92, "mecânicos e ordens de serviço.", 11, MUTED, "start", "400", "italic")}</g>'
    )

    body = [svg_defs(), f'<rect width="{width}" height="{height}" fill="#FFFFFF"/>']
    body.extend(edges)
    body.extend(box_svg(b) for b in boxes.values())
    body.extend(labels)
    body.append(note)

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="Visão compacta do diagrama de classes do OficinaPro">\n'
        + "\n".join(body)
        + "\n</svg>\n"
    )


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(f"SVG gerado: {OUT}")
    compact_out = OUT.with_name("classes-compacto.svg")
    compact_out.write_text(build_compact(), encoding="utf-8")
    print(f"SVG gerado: {compact_out}")
