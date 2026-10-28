"""Esquema SQLite do OficinaPro (versão 1)."""

from __future__ import annotations

import sqlite3

SCHEMA_VERSION = 1

DDL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS oficina (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    nome                TEXT NOT NULL,
    cnpj                TEXT NOT NULL UNIQUE,
    telefone            TEXT,
    endereco            TEXT,
    taxa_horaria_padrao TEXT NOT NULL DEFAULT '120.00',
    comissao_padrao     TEXT NOT NULL DEFAULT '0.10',
    criado_em           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em       TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cliente (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nome            TEXT NOT NULL,
    cpf_cnpj       TEXT NOT NULL UNIQUE,
    telefone        TEXT NOT NULL,
    email           TEXT,
    endereco        TEXT,
    data_nascimento TEXT,
    observacoes     TEXT,
    ativo           INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1)),
    criado_em       TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mecanico (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    nome           TEXT NOT NULL,
    telefone       TEXT NOT NULL,
    email          TEXT,
    registro       TEXT NOT NULL UNIQUE,
    taxa_comissao  TEXT NOT NULL DEFAULT '0.10',
    especialidade  TEXT,
    ativo          INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1)),
    criado_em      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS veiculo (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    placa         TEXT NOT NULL UNIQUE,
    marca         TEXT NOT NULL,
    modelo        TEXT NOT NULL,
    ano           INTEGER NOT NULL,
    km            INTEGER NOT NULL DEFAULT 0 CHECK (km >= 0),
    cor           TEXT,
    combustivel   TEXT,
    cliente_id    INTEGER NOT NULL,
    observacoes   TEXT,
    criado_em     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES cliente(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS ordem_servico (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    numero              TEXT NOT NULL UNIQUE,
    cliente_id          INTEGER NOT NULL,
    veiculo_id          INTEGER NOT NULL,
    mecanico_id         INTEGER NOT NULL,
    status              TEXT NOT NULL DEFAULT 'ORCAMENTO'
                        CHECK (status IN ('ORCAMENTO', 'APROVADA', 'EM_EXECUCAO', 'FINALIZADA', 'CANCELADA')),
    desconto            TEXT NOT NULL DEFAULT '0.00',
    data_abertura       TEXT NOT NULL,
    data_aprovacao      TEXT,
    data_inicio         TEXT,
    data_finalizacao    TEXT,
    data_cancelamento   TEXT,
    motivo_cancelamento TEXT,
    observacoes         TEXT,
    criado_por          TEXT,
    criado_em           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em       TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES cliente(id) ON DELETE RESTRICT,
    FOREIGN KEY (veiculo_id) REFERENCES veiculo(id) ON DELETE RESTRICT,
    FOREIGN KEY (mecanico_id) REFERENCES mecanico(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS item_os (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    ordem_servico_id INTEGER NOT NULL,
    tipo             TEXT NOT NULL CHECK (tipo IN ('PECA', 'MAO_DE_OBRA')),
    descricao        TEXT NOT NULL,
    quantidade       TEXT NOT NULL DEFAULT '1.00',
    valor_unitario   TEXT NOT NULL DEFAULT '0.00',
    codigo_peca      TEXT,
    fornecedor       TEXT,
    horas            TEXT,
    taxa_horaria     TEXT,
    mecanico_id      INTEGER,
    criado_em        TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ordem_servico_id) REFERENCES ordem_servico(id) ON DELETE CASCADE,
    FOREIGN KEY (mecanico_id) REFERENCES mecanico(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS status_historico (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    ordem_servico_id INTEGER NOT NULL,
    status_anterior  TEXT,
    status_novo      TEXT NOT NULL,
    data_hora        TEXT NOT NULL,
    usuario          TEXT,
    motivo           TEXT,
    FOREIGN KEY (ordem_servico_id) REFERENCES ordem_servico(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comissao_pagamento (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    mecanico_id      INTEGER NOT NULL,
    periodo_inicio   TEXT NOT NULL,
    periodo_fim      TEXT NOT NULL,
    valor_base       TEXT NOT NULL,
    percentual       TEXT NOT NULL,
    valor_comissao   TEXT NOT NULL,
    pago_em          TEXT,
    observacoes      TEXT,
    criado_em        TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mecanico_id) REFERENCES mecanico(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS configuracao (
    chave         TEXT PRIMARY KEY,
    valor         TEXT,
    atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cliente_nome ON cliente(nome);
CREATE INDEX IF NOT EXISTS idx_veiculo_cliente ON veiculo(cliente_id);
CREATE INDEX IF NOT EXISTS idx_os_cliente ON ordem_servico(cliente_id);
CREATE INDEX IF NOT EXISTS idx_os_veiculo ON ordem_servico(veiculo_id);
CREATE INDEX IF NOT EXISTS idx_os_mecanico ON ordem_servico(mecanico_id);
CREATE INDEX IF NOT EXISTS idx_os_status ON ordem_servico(status);
CREATE INDEX IF NOT EXISTS idx_os_abertura ON ordem_servico(data_abertura);
CREATE INDEX IF NOT EXISTS idx_os_finalizacao ON ordem_servico(data_finalizacao);
CREATE INDEX IF NOT EXISTS idx_item_os_os ON item_os(ordem_servico_id);
CREATE INDEX IF NOT EXISTS idx_historico_os ON status_historico(ordem_servico_id);
"""


def migrate(conn: sqlite3.Connection) -> None:
    """Cria ou atualiza o esquema de forma idempotente."""
    versao = conn.execute("PRAGMA user_version").fetchone()[0]
    if versao > SCHEMA_VERSION:
        raise RuntimeError(
            f"Banco criado com versão {versao}, superior à versão suportada "
            f"{SCHEMA_VERSION}."
        )
    conn.executescript(DDL)
    conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    conn.commit()
