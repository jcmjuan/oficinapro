"""Geração de orçamentos em PDF via HTML + Chrome headless.

O gerador monta o HTML com o layout do orçamento e usa o Chrome/Chromium já
disponível no sistema para produzir o PDF. A classe é isolada para permitir
trocar o motor sem alterar a camada de aplicação.
"""

from __future__ import annotations

import html
import os
import shutil
import subprocess
import tempfile
from decimal import Decimal
from pathlib import Path
from string import Template

from domain.exceptions import PdfError
from domain.ordem_servico import OrdemServico
from domain.oficina import Oficina
from domain.validators import formatar_brl

_RAIZ = Path(__file__).resolve().parents[2]
_LOGO = _RAIZ / "assets" / "logo-horizontal.png"

_TEMPLATE = Template(
    """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Orçamento ${numero} — ${oficina_nome}</title>
<style>
  @page { size: A4; margin: 14mm 14mm 16mm; }
  * { box-sizing: border-box; }
  body {
    margin: 0; color: #14213d; background: #ffffff;
    font-family: "DejaVu Sans", Arial, sans-serif;
    -webkit-print-color-adjust: exact; print-color-adjust: exact;
  }
  .top {
    display: flex; justify-content: space-between; align-items: flex-start;
    gap: 24px; padding-bottom: 18px; border-bottom: 3px solid #fca311;
  }
  .brand { display: flex; gap: 14px; align-items: center; }
  .brand img { width: 150px; height: auto; }
  .brand-mark {
    width: 52px; height: 52px; border-radius: 12px; background: #14213d;
    color: #ffffff; display: flex; align-items: center; justify-content: center;
    font-weight: 800; letter-spacing: 1px;
  }
  h1 { margin: 0; font-size: 21px; letter-spacing: -0.3px; }
  .muted { color: #5c677d; font-size: 10.5px; line-height: 1.5; margin: 3px 0 0; }
  .doc { text-align: right; min-width: 150px; }
  .doc span {
    display: inline-block; background: #fca311; color: #14213d; font-weight: 800;
    font-size: 10px; letter-spacing: 1.4px; padding: 5px 9px; border-radius: 4px;
  }
  .doc strong { display: block; font-size: 18px; margin-top: 8px; }
  .doc p { margin: 2px 0 0; color: #5c677d; font-size: 10.5px; }
  .status {
    margin: 16px 0; padding: 11px 14px; border-radius: 8px; background: #f4f6fa;
    display: flex; justify-content: space-between; align-items: center; gap: 12px;
    font-size: 11px;
  }
  .badge {
    display: inline-block; padding: 4px 9px; border-radius: 20px;
    background: #14213d; color: #fff; font-weight: 700; font-size: 9.5px;
    letter-spacing: .6px;
  }
  .grid { display: grid; grid-template-columns: 1.25fr 1.25fr 1fr; gap: 10px; }
  .card { border: 1px solid #e3e8ef; border-radius: 8px; padding: 11px 12px; }
  .card h2, .notes h2 {
    margin: 0 0 7px; color: #5c677d; font-size: 9px; letter-spacing: 1px;
    text-transform: uppercase;
  }
  .card p { margin: 2px 0; font-size: 10.5px; line-height: 1.45; }
  .card .strong { font-weight: 700; font-size: 11.5px; }
  table { width: 100%; border-collapse: collapse; margin-top: 18px; }
  thead th {
    background: #14213d; color: #fff; font-size: 9.5px; text-align: left;
    padding: 8px 9px; letter-spacing: .4px;
  }
  thead th:last-child, tbody td:last-child { text-align: right; }
  tbody td {
    border-bottom: 1px solid #e8edf3; padding: 8px 9px; font-size: 10.5px;
    vertical-align: top;
  }
  tbody tr:nth-child(even) td { background: #fafbfc; }
  .tipo { font-size: 8.5px; color: #5c677d; text-transform: uppercase; letter-spacing: .4px; }
  .bottom { display: grid; grid-template-columns: 1fr 250px; gap: 18px; margin-top: 16px; }
  .notes { font-size: 10.5px; line-height: 1.5; color: #33415c; }
  .notes h2 { margin-top: 12px; }
  .notes h2:first-child { margin-top: 0; }
  .totals { border: 1px solid #e3e8ef; border-radius: 8px; overflow: hidden; height: fit-content; }
  .totals div { display: flex; justify-content: space-between; padding: 7px 11px; font-size: 10.5px; }
  .totals div:nth-child(odd) { background: #f7f9fc; }
  .totals .grand {
    background: #14213d !important; color: #fff; font-size: 13px; font-weight: 800;
    padding: 10px 11px;
  }
  .timeline { margin-top: 18px; border-top: 1px solid #e3e8ef; padding-top: 12px; }
  .timeline h2 { margin: 0 0 7px; font-size: 9px; letter-spacing: 1px; color: #5c677d; }
  .timeline ul { margin: 0; padding-left: 16px; color: #33415c; font-size: 10px; line-height: 1.6; }
  .signatures { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin-top: 42px; }
  .signatures div { border-top: 1px solid #8d99ae; padding-top: 6px; text-align: center; font-size: 9.5px; color: #5c677d; }
  footer {
    margin-top: 22px; padding-top: 8px; border-top: 1px solid #e3e8ef;
    color: #8d99ae; font-size: 8.5px; display: flex; justify-content: space-between;
  }
</style>
</head>
<body>
  <header class="top">
    <div class="brand">
      ${logo}
      <div>
        <h1>${oficina_nome}</h1>
        <p class="muted">${oficina_endereco}<br>${oficina_contato}</p>
      </div>
    </div>
    <div class="doc">
      <span>ORÇAMENTO</span>
      <strong>OS ${numero}</strong>
      <p>Abertura: ${data_abertura}</p>
      <p>Validade: 7 dias</p>
    </div>
  </header>

  <section class="status">
    <div><strong>Status:</strong> <span class="badge">${status}</span></div>
    <div><strong>Itens:</strong> ${quantidade_itens} &nbsp;•&nbsp; <strong>Responsável:</strong> ${mecanico}</div>
  </section>

  <section class="grid">
    <div class="card">
      <h2>Cliente</h2>
      <p class="strong">${cliente_nome}</p>
      <p>${cliente_documento}</p>
      <p>${cliente_telefone}</p>
      <p>${cliente_email}</p>
    </div>
    <div class="card">
      <h2>Veículo</h2>
      <p class="strong">${veiculo_marca} ${veiculo_modelo}</p>
      <p>Placa: ${veiculo_placa}</p>
      <p>Ano: ${veiculo_ano} • KM: ${veiculo_km}</p>
      <p>${veiculo_cor}${veiculo_combustivel}</p>
    </div>
    <div class="card">
      <h2>Responsável técnico</h2>
      <p class="strong">${mecanico}</p>
      <p>Registro: ${mecanico_registro}</p>
      <p>${mecanico_especialidade}</p>
    </div>
  </section>

  <table>
    <thead>
      <tr><th style="width:9%">Tipo</th><th>Descrição</th><th style="width:13%">Qtd./Horas</th><th style="width:16%">Unitário</th><th style="width:15%">Subtotal</th></tr>
    </thead>
    <tbody>
      ${linhas_itens}
    </tbody>
  </table>

  <section class="bottom">
    <div class="notes">
      <h2>Observações</h2>
      <p>${observacoes}</p>
      <h2>Condições</h2>
      <p>Orçamento válido por 7 dias. A execução do serviço está condicionada à aprovação do cliente. Peças e insumos podem sofrer reajuste do fornecedor antes da compra.</p>
    </div>
    <div class="totals">
      <div><span>Peças</span><strong>${subtotal_pecas}</strong></div>
      <div><span>Mão de obra</span><strong>${subtotal_mao_obra}</strong></div>
      <div><span>Subtotal</span><strong>${subtotal}</strong></div>
      <div><span>Desconto</span><strong>${desconto}</strong></div>
      <div class="grand"><span>Total</span><span>${total}</span></div>
    </div>
  </section>

  <section class="timeline">
    <h2>Histórico de status</h2>
    <ul>${historico}</ul>
  </section>

  <section class="signatures">
    <div>${oficina_nome} — responsável técnico</div>
    <div>${cliente_nome} — cliente</div>
  </section>

  <footer>
    <span>Documento gerado pelo OficinaPro</span>
    <span>${rodape_data}</span>
  </footer>
</body>
</html>"""
)


def _linhas_itens(ordem: OrdemServico) -> str:
    linhas = []
    for item in ordem.itens:
        if item.tipo() == "PECA":
            tipo = "Peça"
            quantidade = f"{item.quantidade:.2f}".rstrip("0").rstrip(".")
        else:
            tipo = "Mão de obra"
            quantidade = f"{getattr(item, 'horas', Decimal('0')):.2f}".rstrip("0").rstrip(".") + " h"
        linhas.append(
            "<tr>"
            f"<td><span class='tipo'>{html.escape(tipo)}</span></td>"
            f"<td>{html.escape(item.descricao)}</td>"
            f"<td>{html.escape(quantidade)}</td>"
            f"<td>{formatar_brl(item.valor_unitario)}</td>"
            f"<td>{formatar_brl(item.calcular_subtotal())}</td>"
            "</tr>"
        )
    return "\n".join(linhas)


def _historico_html(ordem: OrdemServico) -> str:
    return "".join(
        f"<li>{html.escape(registro.descricao())}"
        + (f" — {html.escape(registro.motivo)}" if registro.motivo else "")
        + "</li>"
        for registro in ordem.historico
    )


def _logo_html() -> str:
    if _LOGO.exists():
        return f'<img src="{_LOGO.as_uri()}" alt="Logo da oficina">'
    return '<div class="brand-mark">OP</div>'


class PdfGenerator:
    def __init__(self, chrome_path: str | None = None) -> None:
        self.chrome_path = (
            chrome_path
            or os.environ.get("OFICINAPRO_CHROME")
            or shutil.which("google-chrome")
            or shutil.which("chromium")
            or shutil.which("chromium-browser")
        )

    @property
    def disponivel(self) -> bool:
        return bool(self.chrome_path and Path(self.chrome_path).exists())

    def gerar_orcamento(
        self,
        ordem: OrdemServico,
        oficina: Oficina,
        destino: str | Path,
    ) -> Path:
        if not self.disponivel:
            raise PdfError(
                "Chrome/Chromium não encontrado. Defina OFICINAPRO_CHROME ou "
                "instale o Google Chrome para gerar PDFs."
            )
        destino = Path(destino)
        destino.parent.mkdir(parents=True, exist_ok=True)
        if destino.exists():
            destino.unlink()
        html_doc = self._renderizar(ordem, oficina)
        with tempfile.TemporaryDirectory(prefix="oficinapro_pdf_") as tmp:
            html_path = Path(tmp) / "orcamento.html"
            html_path.write_text(html_doc, encoding="utf-8")
            erros = []
            for headless in ("--headless=new", "--headless"):
                comando = [
                    self.chrome_path,
                    headless,
                    "--no-sandbox",
                    "--disable-gpu",
                    "--disable-dev-shm-usage",
                    "--allow-file-access-from-files",
                    "--no-pdf-header-footer",
                    "--run-all-compositor-stages-before-draw",
                    "--virtual-time-budget=2000",
                    f"--print-to-pdf={destino.resolve()}",
                    html_path.resolve().as_uri(),
                ]
                try:
                    resultado = subprocess.run(
                        comando,
                        capture_output=True,
                        text=True,
                        timeout=90,
                    )
                except (OSError, subprocess.TimeoutExpired) as exc:
                    erros.append(str(exc))
                    continue
                if resultado.returncode == 0 and destino.exists() and destino.stat().st_size > 0:
                    return destino
                erros.append((resultado.stderr or resultado.stdout or "").strip())
        raise PdfError(
            "Não foi possível gerar o PDF. " + " | ".join(erro for erro in erros if erro)
        )

    def _renderizar(self, ordem: OrdemServico, oficina: Oficina) -> str:
        cliente = ordem.cliente
        veiculo = ordem.veiculo
        return _TEMPLATE.safe_substitute(
            numero=html.escape(ordem.numero),
            oficina_nome=html.escape(oficina.nome),
            oficina_endereco=html.escape(oficina.endereco or ""),
            oficina_contato=html.escape(
                " • ".join(
                    parte for parte in (oficina.telefone_formatado, oficina.cnpj) if parte
                )
            ),
            data_abertura=ordem.data_abertura.strftime("%d/%m/%Y"),
            status=html.escape(ordem.status.rotulo.upper()),
            quantidade_itens=str(ordem.quantidade_itens),
            mecanico=html.escape(ordem.mecanico.nome),
            mecanico_registro=html.escape(ordem.mecanico.registro),
            mecanico_especialidade=html.escape(ordem.mecanico.especialidade or ""),
            cliente_nome=html.escape(cliente.nome),
            cliente_documento=html.escape(cliente.cpf_cnpj),
            cliente_telefone=html.escape(cliente.telefone_formatado),
            cliente_email=html.escape(cliente.email or ""),
            veiculo_marca=html.escape(veiculo.marca),
            veiculo_modelo=html.escape(veiculo.modelo),
            veiculo_placa=html.escape(veiculo.placa),
            veiculo_ano=str(veiculo.ano),
            veiculo_km=f"{veiculo.km:,}".replace(",", "."),
            veiculo_cor=html.escape(veiculo.cor),
            veiculo_combustivel=(" • " + html.escape(veiculo.combustivel)) if veiculo.combustivel else "",
            linhas_itens=_linhas_itens(ordem),
            observacoes=html.escape(ordem.observacoes or "Sem observações."),
            subtotal_pecas=formatar_brl(ordem.subtotal_pecas),
            subtotal_mao_obra=formatar_brl(ordem.subtotal_mao_obra),
            subtotal=formatar_brl(ordem.subtotal),
            desconto=formatar_brl(ordem.desconto),
            total=formatar_brl(ordem.total),
            historico=_historico_html(ordem),
            logo=_logo_html(),
            rodape_data=ordem.data_abertura.strftime("%d/%m/%Y %H:%M"),
        )
