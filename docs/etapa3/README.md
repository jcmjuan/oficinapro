# Etapa 3 — Implementação do Núcleo

Esta pasta contém o relatório técnico da Etapa 3 do OficinaPro.

## Arquivos

| Arquivo | Descrição |
|---|---|
| `Etapa3_Implementacao.md` | Fonte Markdown do relatório |
| `Etapa3_Implementacao.html` | Renderização HTML completa |
| `Etapa3_Implementacao.pdf` | PDF de submissão (18 páginas) |
| `capturas/` | Evidências visuais: painel CLI, testes e orçamento em PDF |
| `ferramentas/gerar_pdf.mjs` | Gerador do PDF a partir do Markdown |

## Visualizar

```bash
xdg-open Etapa3_Implementacao.pdf
```

Ou abra `Etapa3_Implementacao.html` no navegador.

## Regenerar o PDF

O gerador usa `marked` e `puppeteer-core` para renderizar o Markdown e o Chrome
headless para imprimir o PDF. Em um ambiente limpo:

```bash
mkdir -p /tmp/opencode/docgen
cd /tmp/opencode/docgen
npm init -y
npm install marked puppeteer-core
cd -
node docs/etapa3/ferramentas/gerar_pdf.mjs
```

O script grava:

- `docs/etapa3/Etapa3_Implementacao.html`
- `docs/etapa3/Etapa3_Implementacao.pdf`

Requisitos: Node.js, Google Chrome/Chromium e `pdfunite` (poppler-utils).

## Regenerar as capturas

```bash
# Orçamento em PDF
python3 main.py --pdf 2026-0042
pdftoppm -f 1 -singlefile -png -r 120 \
  orcamentos/OS-2026-0042.pdf docs/etapa3/capturas/orcamento

# Painel CLI
python3 main.py --db /tmp/opencode/oficinapro_demo.db

# Testes
python3 -m unittest discover -s tests -v
```

As capturas `painel-cli.png` e `testes.png` foram geradas a partir da saída real
do terminal em uma página HTML com o mesmo tema escuro.

## Checklist de entrega

- [x] Domínio implementado
- [x] Persistência SQLite
- [x] Serviços de aplicação
- [x] Relatórios e comissões
- [x] Orçamento em PDF
- [x] Integração com WhatsApp
- [x] Backup e restauração
- [x] 29 testes automatizados
- [x] Relatório e PDF da Etapa 3
- [x] Interface CustomTkinter implementada (Etapa Final)
- [x] Validação visual em ambiente com Tkinter (Etapa Final)
- [x] Slides e apresentação (19/11/2026)
