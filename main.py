"""Ponto de entrada do OficinaPro.

Uso rápido:
    python main.py                 # abre a interface gráfica (fallback: painel CLI)
    python main.py --cli           # força o painel CLI
    python main.py --ui            # força a interface CustomTkinter
    python main.py --report        # relatório de comissões do mês
    python main.py --pdf 2026-0042 # gera o orçamento em PDF
    python main.py --whatsapp 2026-0042
    python main.py --backup
    python main.py --reset         # recria a base demonstrativa
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from application.configuracao_service import ConfiguracaoService
from application.orcamento_service import OrcamentoService
from application.relatorio_service import RelatorioService
from domain.status_os import StatusOS
from domain.validators import formatar_brl
from infrastructure.database import Database
from infrastructure.repositories.cliente_repository import ClienteRepository
from infrastructure.repositories.configuracao_repository import ConfiguracaoRepository
from infrastructure.repositories.mecanico_repository import MecanicoRepository
from infrastructure.repositories.oficina_repository import OficinaRepository
from infrastructure.repositories.ordem_servico_repository import OrdemServicoRepository
from infrastructure.repositories.veiculo_repository import VeiculoRepository
from infrastructure.seed import seed_demo


def _construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oficinapro",
        description="OficinaPro — gestão de oficina mecânica (Etapa Final)",
    )
    parser.add_argument(
        "--db",
        default="oficinapro.db",
        help="Caminho do banco SQLite (padrão: oficinapro.db).",
    )
    modo = parser.add_mutually_exclusive_group()
    modo.add_argument(
        "--ui",
        action="store_true",
        help="Abre a interface gráfica CustomTkinter.",
    )
    modo.add_argument(
        "--cli",
        action="store_true",
        help="Executa o painel e os comandos no terminal.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Apaga os dados e recria a base demonstrativa.",
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Carrega a base demonstrativa se o banco estiver vazio.",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Exibe o relatório de comissões do mês atual.",
    )
    parser.add_argument(
        "--pdf",
        metavar="OS",
        help="Gera o PDF do orçamento da OS informada.",
    )
    parser.add_argument(
        "--whatsapp",
        metavar="OS",
        help="Exibe o link do WhatsApp para a OS informada.",
    )
    parser.add_argument(
        "--backup",
        nargs="?",
        const="",
        metavar="ARQUIVO",
        help="Gera um backup do banco (opcionalmente em um caminho).",
    )
    return parser


def _painel(db: Database) -> None:
    clientes = ClienteRepository(db)
    mecanicos = MecanicoRepository(db)
    veiculos = VeiculoRepository(db)
    ordens = OrdemServicoRepository(db)
    oficinas = OficinaRepository(db)
    relatorio = RelatorioService(ordens)
    oficina = oficinas.obter()
    resumo = relatorio.resumo_formatado()
    contagem = ordens.contar_por_status()

    print("=" * 72)
    print(f"  {oficina.nome} — OficinaPro")
    print("=" * 72)
    print(
        f"Clientes: {clientes.contar():>2}  •  Mecânicos: {mecanicos.contar():>2}  •  "
        f"Veículos: {veiculos.contar():>2}  •  OS: {ordens.contar():>2}"
    )
    print(
        "Status: "
        + "  ".join(
            f"{status.rotulo}: {contagem.get(status.value, 0)}"
            for status in StatusOS
        )
    )
    print("-" * 72)
    print(
        f"Período: {resumo['inicio']:%d/%m/%Y} a {resumo['fim']:%d/%m/%Y}  •  "
        f"OS finalizadas: {resumo['quantidade_os']}"
    )
    print(f"Faturamento: {resumo['faturamento_fmt']}  •  Ticket médio: {resumo['ticket_medio_fmt']}")
    print(
        f"Mão de obra: {resumo['mao_obra_fmt']}  •  Peças: {resumo['pecas_fmt']}  •  "
        f"Comissões: {resumo['comissoes_fmt']}"
    )
    print("-" * 72)
    print("Últimas ordens de serviço")
    for ordem in ordens.ultimas(6):
        print(
            f"  {ordem.numero}  {ordem.cliente.nome:<22.22}  "
            f"{ordem.veiculo.placa:<10}  {ordem.status.rotulo:<12}  "
            f"{formatar_brl(ordem.total):>13}"
        )
    print("=" * 72)


def _relatorio(db: Database) -> None:
    ordens = OrdemServicoRepository(db)
    relatorio = RelatorioService(ordens)
    dados = relatorio.resumo()
    print(f"Relatório de comissões — {dados['inicio']:%d/%m/%Y} a {dados['fim']:%d/%m/%Y}")
    print(f"OS finalizadas: {dados['quantidade_os']}")
    print(f"Faturamento: {formatar_brl(dados['faturamento'])}")
    print(f"Mão de obra: {formatar_brl(dados['mao_obra'])}")
    print(f"Peças: {formatar_brl(dados['pecas'])}")
    print(f"Comissões: {formatar_brl(dados['comissoes'])}")
    print("-" * 72)
    print(f"{'Mecânico':<20} {'OS':>4} {'Mão de obra':>14} {'Taxa':>7} {'Comissão':>12}")
    for item in dados["mecanicos"]:
        print(
            f"{item['nome']:<20} {item['quantidade_os']:>4} "
            f"{formatar_brl(item['mao_obra']):>14} "
            f"{item['taxa'] * 100:>6.1f}% {formatar_brl(item['comissao']):>12}"
        )


def _executar(args: argparse.Namespace) -> int:
    db = Database(args.db)
    try:
        if args.reset:
            seed_demo(db, forcar=True)
            print(f"Base demonstrativa recriada em {args.db}.")
            return 0
        seed_demo(db)
        if args.seed:
            print(f"Base pronta em {args.db}.")
            return 0

        oficinas = OficinaRepository(db)
        ordens = OrdemServicoRepository(db)
        if args.pdf:
            servico = OrcamentoService(ordens, oficinas)
            destino = Path("orcamentos") / f"OS-{args.pdf}.pdf"
            caminho = servico.gerar_pdf(args.pdf, destino)
            print(f"PDF gerado: {caminho.resolve()}")
            return 0
        if args.whatsapp:
            servico = OrcamentoService(ordens, oficinas)
            print(servico.link_whatsapp(args.whatsapp))
            return 0
        if args.backup is not None:
            config = ConfiguracaoService(
                ConfiguracaoRepository(db), oficinas, db
            )
            destino = args.backup or None
            caminho = config.fazer_backup(destino)
            print(f"Backup criado: {caminho.resolve()}")
            return 0
        if args.report:
            _relatorio(db)
            return 0

        if args.cli:
            _painel(db)
            return 0

        # O fluxo padrão é a interface gráfica. Em ambientes sem Tkinter ou
        # CustomTkinter, o painel CLI mantém o sistema utilizável.
        db.fechar()
        try:
            from ui.app import run as run_ui

            run_ui(args.db)
            return 0
        except ImportError as exc:
            if args.ui:
                print(
                    "Interface gráfica indisponível: instale as dependências com "
                    "`pip install -r requirements-ui.txt`.\n"
                    f"Detalhe: {exc}",
                    file=sys.stderr,
                )
                return 1
            print(
                "Interface gráfica indisponível (CustomTkinter/Tkinter). "
                "Exibindo o painel CLI.\n"
                "Para instalar a interface: pip install -r requirements-ui.txt",
                file=sys.stderr,
            )
        except Exception as exc:
            if args.ui:
                print(f"Não foi possível abrir a interface: {exc}", file=sys.stderr)
                return 1
            print(
                f"Não foi possível abrir a interface ({exc}). "
                "Exibindo o painel CLI.",
                file=sys.stderr,
            )
        db = Database(args.db)
        _painel(db)
        return 0
    finally:
        try:
            db.fechar()
        except Exception:
            pass


def main(argv: list[str] | None = None) -> int:
    parser = _construir_parser()
    args = parser.parse_args(argv)
    return _executar(args)


if __name__ == "__main__":
    sys.exit(main())
