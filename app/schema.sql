CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL CHECK (length(trim(nome)) BETWEEN 1 AND 120),
    categoria TEXT NOT NULL CHECK (length(trim(categoria)) BETWEEN 1 AND 80),
    preco_centavos INTEGER NOT NULL CHECK (preco_centavos >= 0),
    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1)),
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_produtos_categoria_ativo
ON produtos (categoria, ativo);

CREATE INDEX IF NOT EXISTS idx_produtos_nome
ON produtos (nome COLLATE NOCASE);

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL CHECK (length(trim(nome)) BETWEEN 2 AND 120),
    email TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (length(trim(email)) BETWEEN 3 AND 254),
    senha_hash TEXT NOT NULL,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
);

CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    bairro TEXT NOT NULL CHECK (length(trim(bairro)) BETWEEN 1 AND 120),
    rua TEXT NOT NULL CHECK (length(trim(rua)) BETWEEN 1 AND 180),
    numero TEXT NOT NULL CHECK (length(trim(numero)) BETWEEN 1 AND 30),
    total_centavos INTEGER NOT NULL CHECK (total_centavos >= 0),
    status TEXT NOT NULL CHECK (status IN ('aguardando_pagamento')),
    idempotency_key TEXT NOT NULL UNIQUE CHECK (length(idempotency_key) BETWEEN 8 AND 128),
    usuario_id INTEGER,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS pedido_itens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    nome_produto TEXT NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade BETWEEN 1 AND 99),
    preco_unitario_centavos INTEGER NOT NULL CHECK (preco_unitario_centavos >= 0),
    subtotal_centavos INTEGER NOT NULL CHECK (subtotal_centavos >= 0),
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_pedido_itens_pedido
ON pedido_itens (pedido_id);
