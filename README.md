# OficinaPro

Sistema de gestão para oficina mecânica desenvolvido como projeto acadêmico.
A **Etapa 2** entregou a modelagem, os wireframes e o protótipo navegável. A
**Etapa 3** entregou o núcleo executável: domínio, persistência SQLite, regras
de negócio, relatórios, geração de orçamento em PDF, integração com WhatsApp e
testes automatizados. A **Etapa Final** adiciona a interface CustomTkinter,
integrada aos mesmos serviços, e a documentação de encerramento.

> Situação atual: **Etapa Final implementada**. A interface gráfica é o modo
> padrão de execução; o painel CLI continua disponível como alternativa e como
> fallback em ambientes sem Tkinter/CustomTkinter.

## Destaques

- Interface desktop em **CustomTkinter** com a linguagem visual da Etapa 2.
- Domínio orientado a objetos com `Decimal` para valores monetários.
- Herança e polimorfismo em `ItemOS` (`Peca` e `MaoDeObra`).
- Ciclo de vida da OS com transições validadas e histórico append-only.
- Persistência SQLite com chaves estrangeiras, índices e migração versionada.
- Relatórios de faturamento, mão de obra, peças e comissões.
- Orçamento/recibo em PDF com identidade visual do projeto.
- Link de WhatsApp via `wa.me`.
- Backup e restauração com verificação de integridade.
- 28 testes automatizados com `unittest` (biblioteca padrão).

## Requisitos

- **Python 3.12+** (o ambiente de desenvolvimento usa Python 3.14).
- **Chrome ou Chromium** para gerar PDFs (o núcleo não exige ReportLab).
- Para a interface: **Tkinter** e `customtkinter` (veja `requirements-ui.txt`).
- Nenhuma dependência externa é necessária para o núcleo, os testes e os
  comandos CLI.

## Como executar

### Interface gráfica

```bash
# 1. Entre na raiz do projeto
cd oficinapro

# 2. Crie um ambiente virtual (recomendado)
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Instale a dependência da interface
pip install -r requirements-ui.txt

# 4. Abra a interface
python3 main.py
```

`python3 main.py` cria/abre `oficinapro.db`, carrega a seed demonstrativa quando
o banco está vazio e abre o dashboard. Para forçar um modo:

```bash
python3 main.py --ui            # exige Tkinter/CustomTkinter
python3 main.py --cli           # painel CLI
python3 main.py --db outro.db   # banco alternativo
```

Se Tkinter ou CustomTkinter não estiverem disponíveis, o comando padrão exibe
uma mensagem e cai automaticamente no painel CLI. O modo `--ui` falha de forma
explícita para facilitar o diagnóstico.

### Telas da interface

| Tela | Recursos principais |
|---|---|
| **Dashboard** | Faturamento, mão de obra, peças, comissões, status das OS e últimas ordens |
| **Clientes** | Busca, cadastro, edição, inativação/reativação e acesso aos veículos |
| **Veículos** | Busca por placa/modelo/cliente, cadastro, edição e histórico de OS |
| **Ordens de Serviço** | Filtros por status/cliente/veículo, abertura, PDF e WhatsApp |
| **Editor da OS** | Itens, desconto, observações, histórico e transições de status |
| **Orçamento/Recibo** | Visualização, geração de PDF, cópia da mensagem e WhatsApp |
| **Relatórios** | Período configurável, comissões, composição do faturamento e CSV |
| **Configurações** | Dados da oficina, equipe, backup/restauração e informações do sistema |

### Comandos CLI

```bash
python3 main.py --cli           # painel demonstrativo
python3 main.py --reset         # recria a base demonstrativa
python3 main.py --report        # relatório de comissões do mês
python3 main.py --pdf 2026-0042 # gera o PDF de uma OS
python3 main.py --whatsapp 2026-0042
python3 main.py --backup
python3 main.py --backup backups/entrega.db
```

O PDF é gravado em `orcamentos/OS-<numero>.pdf`. O banco padrão é
`oficinapro.db`; use `--db caminho/arquivo.db` para apontar para outro arquivo.

## Testes

```bash
python3 -m unittest discover -s tests -v
```

Resultado esperado: **28 testes OK**. Os testes cobrem domínio, validações,
transições de status, persistência, backup/restauração, serviços, relatórios,
WhatsApp e geração de PDF (quando o Chrome está disponível).

## Dados demonstrativos

A seed reproduz os totais da Etapa 2:

| Indicador | Valor |
|---|---:|
| Faturamento | R$ 18.450,00 |
| Mão de obra | R$ 6.320,00 |
| Peças | R$ 12.130,00 |
| Comissões | R$ 743,00 |
| OS finalizadas | 18 |
| OS totais | 22 |

Comissões por mecânico:

| Mecânico | OS | Mão de obra | Taxa | Comissão |
|---|---:|---:|---:|---:|
| Marcos Silva | 8 | R$ 3.000,00 | 12% | R$ 360,00 |
| Rafael Costa | 6 | R$ 2.300,00 | 10% | R$ 230,00 |
| Diego Almeida | 4 | R$ 1.020,00 | 15% | R$ 153,00 |

Além das 18 OS finalizadas, a base contém:

- `2026-0042` — orçamento em aberto, R$ 1.240,00, 7 itens;
- `2026-0041` — em execução, R$ 860,00;
- `2026-0039` — aprovada, R$ 2.300,00;
- `2026-0038` — cancelada, R$ 420,00.

## Estrutura do projeto

```text
oficinapro/
├── main.py                         # entrada padrão: UI; --cli para terminal
├── pyproject.toml
├── requirements.txt
├── requirements-ui.txt
├── domain/                         # regras de negócio puras
│   ├── pessoa.py                   # classe abstrata
│   ├── cliente.py
│   ├── mecanico.py
│   ├── veiculo.py
│   ├── item_os.py                  # classe abstrata de item
│   ├── peca.py
│   ├── mao_de_obra.py
│   ├── ordem_servico.py            # agregado raiz
│   ├── oficina.py
│   ├── status_os.py
│   ├── status_historico.py
│   ├── validators.py
│   └── exceptions.py
├── application/                    # casos de uso
│   ├── ordem_servico_service.py
│   ├── orcamento_service.py
│   ├── relatorio_service.py
│   ├── configuracao_service.py
│   └── whatsapp.py
├── infrastructure/                 # SQLite, repositórios, PDF e backup
│   ├── database.py
│   ├── migrations.py
│   ├── seed.py
│   ├── backup.py
│   ├── repositories/
│   │   ├── cliente_repository.py
│   │   ├── mecanico_repository.py
│   │   ├── veiculo_repository.py
│   │   ├── ordem_servico_repository.py
│   │   ├── oficina_repository.py
│   │   └── configuracao_repository.py
│   └── pdf/
│       └── orcamento_pdf.py
├── ui/                             # interface CustomTkinter
│   ├── app.py                      # janela principal, sidebar e navegação
│   ├── theme.py                    # cores, fontes e badges de status
│   ├── components.py               # cards, tabelas, cabeçalhos e indicadores
│   ├── dialogs.py                  # formulários e orçamento/recibo
│   ├── context.py                  # banco, repositórios e serviços
│   ├── utils.py                    # formatação e integrações do SO
│   └── screens/
│       ├── dashboard.py
│       ├── clientes.py
│       ├── veiculos.py
│       ├── ordens.py
│       ├── editor_os.py
│       ├── relatorios.py
│       └── configuracoes.py
├── tests/
│   ├── test_domain.py
│   ├── test_repositories.py
│   └── test_services.py
├── assets/                         # logos
├── docs/
│   ├── etapa2/                     # modelagem, wireframes e protótipo
│   ├── etapa3/                     # relatório de implementação
│   └── final/                      # relatório e slides da Etapa Final
└── orcamentos/                     # PDFs gerados (criado sob demanda)
```

## Arquitetura

O projeto segue uma separação em camadas:

1. **Domínio** — entidades, validações, cálculos e transições de status. Não
   conhece SQLite, PDF, WhatsApp nem interface gráfica.
2. **Aplicação** — orquestra casos de uso e repositórios.
3. **Infraestrutura** — implementação SQLite, mapeamento de linhas, seed,
   backup, geração de PDF e links de WhatsApp.
4. **Interface** — CustomTkinter em `ui/`, consumindo exclusivamente os
   serviços e repositórios das camadas anteriores. O CLI em `main.py` permanece
   como alternativa de operação e fallback.

### Regras de negócio principais

- Valores monetários usam `Decimal` com duas casas e arredondamento
  `ROUND_HALF_UP`.
- CPF/CNPJ é armazenado somente com dígitos e exibido formatado.
- Placas aceitam o padrão antigo (`ABC-1234`) e Mercosul (`ABC-1D23`).
- O veículo precisa pertencer ao cliente da OS.
- Itens só podem ser adicionados, removidos ou descontados em `ORCAMENTO`.
- O desconto não pode ultrapassar o subtotal.
- A aprovação exige pelo menos um item e total maior que zero.
- Transições permitidas:
  `ORCAMENTO → APROVADA → EM_EXECUCAO → FINALIZADA`, com cancelamento em
  `ORCAMENTO`, `APROVADA` ou `EM_EXECUCAO`.
- `FINALIZADA` e `CANCELADA` são estados terminais.
- O histórico de status é append-only.
- A quilometragem do veículo é atualizada ao finalizar a OS e não pode
  diminuir.
- Clientes e mecânicos possuem inativação lógica (soft delete).

## Banco de dados

O esquema é criado automaticamente em `infrastructure/migrations.py` e usa
`PRAGMA user_version = 1`. Tabelas principais:

`oficina`, `cliente`, `mecanico`, `veiculo`, `ordem_servico`, `item_os`,
`status_historico`, `comissao_pagamento`, `configuracao`.

O repositório de OS salva o agregado completo, recria os itens e acrescenta
somente os novos registros de histórico, preservando o caráter append-only.

## Geração de PDF

O gerador `infrastructure/pdf/orcamento_pdf.py` monta um HTML com o layout do
orçamento e usa Chrome/Chromium headless (`--print-to-pdf`). Essa escolha
permite gerar PDFs de alta qualidade no ambiente da disciplina, que não possui
ReportLab instalado. A classe é isolada: é possível trocar o motor por
ReportLab sem alterar os serviços de aplicação.

Para apontar um Chrome específico:

```bash
export OFICINAPRO_CHROME=/caminho/para/google-chrome
```

## WhatsApp

O link é montado no formato:

```text
https://wa.me/55DDDNUMERO?text=<mensagem codificada>
```

A mensagem inclui o primeiro nome do cliente, número da OS, veículo, quantidade
de itens, total e validade do orçamento. A interface oferece “WhatsApp” na lista
de OS, no editor e na visualização do orçamento/recibo.

## Documentação

- `docs/etapa2/Etapa2_Modelagem_e_Interfaces.pdf` — modelagem, diagramas,
  dicionário de dados, wireframes e protótipo.
- `docs/etapa3/Etapa3_Implementacao.pdf` — relatório de implementação da
  Etapa 3.
- `docs/final/Relatorio_Final.pdf` — relatório de encerramento da Etapa Final.
- `docs/final/Slides_Apresentacao.pdf` — slides da apresentação.
- `docs/etapa2/README.md`, `docs/etapa3/README.md` e `docs/final/README.md` —
  instruções de visualização e regeneração.

## Validação da interface

A Etapa Final foi validada em execução real, não apenas por compilação:

- **Tk 8.6** e **CustomTkinter 5.2.2** foram usados em uma sessão gráfica local
  com janela de **1440 × 900**;
- as telas, diálogos e fluxos de cadastro, OS, aprovação, finalização, PDF,
  WhatsApp, CSV, backup e restauração foram exercitados;
- as **20 capturas reais** usadas no relatório e nos slides estão em
  `docs/final/capturas/`;
- o roteiro criou as OS `2026-0043` e `2026-0044` em banco temporário, sem
  alterar a base demonstrativa do projeto.

O ambiente de automação original não possui `tkinter`, `pip`, `ReportLab` nem
`pytest`. Por isso, os testes usam `unittest` (stdlib) e os PDFs usam Chrome
headless. Em uma instalação normal, basta ter Python com Tkinter e executar
`pip install -r requirements-ui.txt` antes de `python3 main.py`.

---

Desenvolvido por **DevSolo Studio** para o projeto OficinaPro.
