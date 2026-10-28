# OficinaPro v1.0 — Etapa 2

Entrega de **Modelagem e Interfaces** do projeto **OficinaPro v1.0**, da equipe **DevSolo Studio** (integrante: Juan Carlos Matos).

O pacote reúne a documentação técnica em Markdown, o PDF de submissão, os diagramas UML, oito wireframes navegáveis e um protótipo HTML que simula o fluxo principal do sistema.

## Arquivos principais

| Arquivo | Descrição |
|---|---|
| [`Etapa2_Modelagem_e_Interfaces.pdf`](Etapa2_Modelagem_e_Interfaces.pdf) | Documento final para submissão: 51 páginas (capa + 50 páginas numeradas). |
| [`Etapa2_Modelagem_e_Interfaces.md`](Etapa2_Modelagem_e_Interfaces.md) | Fonte editável em Markdown + Mermaid. |
| [`Etapa2_Modelagem_e_Interfaces.html`](Etapa2_Modelagem_e_Interfaces.html) | Versão HTML do documento, útil para leitura no navegador. |
| [`prototipo/index.html`](prototipo/index.html) | Protótipo navegável com as oito telas em um shell com sidebar. |
| [`wireframes/`](wireframes/) | As oito telas individuais em HTML/CSS/JS. |
| [`capturas/`](capturas/) | Capturas 1440 × 900 usadas no documento e nos slides. |
| [`diagramas/`](diagramas/) | Diagramas renderizados (PNG/SVG) e fontes Mermaid. |
| [`ferramentas/`](ferramentas/) | Scripts de geração do diagrama de classes e do PDF. |

## Como visualizar

### PDF

```bash
xdg-open docs/etapa2/Etapa2_Modelagem_e_Interfaces.pdf
```

Ou abra o arquivo diretamente no leitor de PDF de sua preferência.

### Protótipo navegável

```bash
xdg-open docs/etapa2/prototipo/index.html
```

O protótipo não precisa de servidor: ele usa apenas HTML, CSS e JavaScript puros. A navegação pode ser feita pela sidebar, pelo botão **Próxima tela** ou pelas setas `←` e `→` do teclado. O botão **Abrir em nova aba** mostra a tela em tamanho real (1440 × 900).

### Wireframes individuais

Abra qualquer arquivo de `docs/etapa2/wireframes/` no navegador. Por exemplo:

```bash
xdg-open docs/etapa2/wireframes/t01-dashboard.html
```

Os parâmetros de URL usados nas capturas também funcionam:

- `?list=1` — oculta o drawer de exemplo e mostra apenas a lista.
- Sem parâmetro — o drawer de exemplo aparece aberto nas telas que possuem drawer (T02 e T03).

## Como regenerar o PDF

O PDF já está gerado. Para refazê-lo após editar o Markdown:

```bash
cd "/home/juan/Área de trabalho/oficinapro"
node docs/etapa2/ferramentas/gerar_pdf.mjs
```

O script:

1. Renderiza a capa e o corpo separadamente.
2. Usa o Chrome headless via `puppeteer-core` para imprimir os dois PDFs.
3. Junta capa + corpo com `pdfunite`.
4. Grava o resultado em `docs/etapa2/Etapa2_Modelagem_e_Interfaces.pdf`.

Requisitos do ambiente usado neste projeto:

- Google Chrome em `/usr/bin/google-chrome`.
- `pdfunite` (poppler-utils).
- `marked` e `puppeteer-core` instalados em `/tmp/opencode/docgen/node_modules`.

Se as dependências não estiverem nesse caminho, instale-as em uma pasta local e ajuste os dois `require(...)` no início de `gerar_pdf.mjs`:

```bash
mkdir -p /tmp/opencode/docgen
cd /tmp/opencode/docgen
npm init -y
npm install marked puppeteer-core
```

## Como regenerar os diagramas

### Diagrama de classes detalhado (SVG)

```bash
python3 docs/etapa2/ferramentas/gerar_diagrama_classes.py
```

O script grava `docs/etapa2/diagramas/classes-detalhado.svg`. Para gerar o PNG usado no PDF, converta o SVG com Chrome, Inkscape, `sharp` ou outra ferramenta de sua preferência. As versões PNG já estão incluídas no pacote.

### Diagramas Mermaid

As fontes `.mmd` estão em `docs/etapa2/diagramas/`. Exemplo com o Mermaid CLI:

```bash
npx @mermaid-js/mermaid-cli \
  -i docs/etapa2/diagramas/estados-os.mmd \
  -o docs/etapa2/diagramas/estados-os.png \
  -p docs/etapa2/diagramas/puppeteer-config.json \
  --size 1200 -s 2
```

O arquivo `puppeteer-config.json` já contém a configuração do Chrome headless usada neste ambiente Linux.

## Como recapturar os wireframes

As capturas foram feitas em 1440 × 900 com Chrome headless. O padrão do comando é:

```bash
google-chrome --headless=new --no-sandbox --hide-scrollbars \
  --window-size=1440,900 \
  --screenshot=docs/etapa2/capturas/t01-dashboard.png \
  "file:///home/juan/%C3%81rea%20de%20trabalho/oficinapro/docs/etapa2/wireframes/t01-dashboard.html"
```

Para as listas sem drawer, acrescente `?list=1` ao final da URL. Para os drawers, abra a tela sem esse parâmetro (o drawer de exemplo já aparece aberto) e recorte a área do painel com `sharp`, `ImageMagick` ou outra ferramenta. As imagens `*-drawer-pdf.png` são recortes usados no documento (PDF e HTML); os arquivos `*-drawer.png` são as capturas completas.

## Escopo e limitações

- O protótipo é um **artefato de design e validação de fluxo**: não persiste dados, não gera PDFs reais e não se conecta ao SQLite.
- A interface final será implementada em **CustomTkinter** na Etapa 3 e na Etapa Final.
- A integração com WhatsApp usa links `wa.me` com texto pré-formatado; não há API oficial.
- O modelo didático usa `float` para valores monetários; a implementação deve usar `Decimal` para evitar erros de arredondamento.
- Os dados dos wireframes são fictícios e servem apenas para validar layout, hierarquia e estados.

## Checklist da Etapa 2

- [x] Diagrama de classes com herança, associação, composição, atributo privado e método privado.
- [x] Diagrama de estados da Ordem de Serviço.
- [x] Diagrama de arquitetura em camadas.
- [x] Modelo de dados SQLite e DDL.
- [x] Design system com paleta, tipografia, componentes e acessibilidade.
- [x] Mapa de navegação.
- [x] Oito wireframes em 1440 × 900.
- [x] Protótipo navegável.
- [x] Fluxos de interação e três diagramas de sequência.
- [x] Plano de testes, cronograma, riscos e glossário.
- [x] Prévia do programa principal com pelo menos dois objetos.
- [x] Documento em Markdown + Mermaid.
- [x] PDF final para submissão.

## Contato

**DevSolo Studio** — Juan Carlos Matos  
Projeto: OficinaPro v1.0  
Entrega: 29/10/2026
