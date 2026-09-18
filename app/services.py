from dataclasses import dataclass

from .db import get_db

ORDER_STATUS = "aguardando_pagamento"
MAX_ITEM_QUANTITY = 99


class OrderValidationError(ValueError):
    def __init__(self, message, fields=None):
        super().__init__(message)
        self.fields = fields or {}


@dataclass(frozen=True)
class ValidatedItem:
    product_id: int
    name: str
    quantity: int
    unit_price_cents: int

    @property
    def subtotal_cents(self):
        return self.quantity * self.unit_price_cents


def _validate_address(payload):
    field_limits = {"bairro": 120, "rua": 180, "numero": 30}
    values = {}
    errors = {}
    for field, maximum in field_limits.items():
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            errors[field] = "Este campo é obrigatório."
        elif len(value.strip()) > maximum:
            errors[field] = f"Use no máximo {maximum} caracteres."
        else:
            values[field] = value.strip()
    if errors:
        raise OrderValidationError("Revise os dados de entrega.", errors)
    return values


def _validate_items(raw_items):
    if not isinstance(raw_items, list) or not raw_items:
        raise OrderValidationError("O carrinho deve conter pelo menos um item.")
    if len(raw_items) > 100:
        raise OrderValidationError("O pedido excede o limite de 100 itens diferentes.")

    quantities = {}
    for index, raw in enumerate(raw_items):
        if not isinstance(raw, dict):
            raise OrderValidationError(f"Item {index + 1} inválido.")
        product_id = raw.get("produto_id")
        quantity = raw.get("quantidade")
        if isinstance(product_id, bool) or not isinstance(product_id, int) or product_id < 1:
            raise OrderValidationError(f"Produto do item {index + 1} inválido.")
        if isinstance(quantity, bool) or not isinstance(quantity, int) or not 1 <= quantity <= MAX_ITEM_QUANTITY:
            raise OrderValidationError(
                f"A quantidade do item {index + 1} deve ser um inteiro entre 1 e {MAX_ITEM_QUANTITY}."
            )
        quantities[product_id] = quantities.get(product_id, 0) + quantity
        if quantities[product_id] > MAX_ITEM_QUANTITY:
            raise OrderValidationError(f"A quantidade total do produto {product_id} excede {MAX_ITEM_QUANTITY}.")

    db = get_db()
    placeholders = ",".join("?" for _ in quantities)
    products = db.execute(
        f"SELECT id, nome, preco_centavos FROM produtos WHERE ativo = 1 AND id IN ({placeholders})",
        tuple(quantities),
    ).fetchall()
    by_id = {row["id"]: row for row in products}
    missing = sorted(set(quantities) - set(by_id))
    if missing:
        raise OrderValidationError(f"Produto indisponível ou inexistente: {missing[0]}.")
    return [
        ValidatedItem(product_id, by_id[product_id]["nome"], quantity, by_id[product_id]["preco_centavos"])
        for product_id, quantity in quantities.items()
    ]


def serialize_order(order_id):
    db = get_db()
    order = db.execute(
        "SELECT id, criado_em, bairro, rua, numero, total_centavos, status, usuario_id FROM pedidos WHERE id = ?",
        (order_id,),
    ).fetchone()
    items = db.execute(
        """
        SELECT produto_id, nome_produto, quantidade, preco_unitario_centavos, subtotal_centavos
        FROM pedido_itens WHERE pedido_id = ? ORDER BY id
        """,
        (order_id,),
    ).fetchall()
    return {
        "id": order["id"],
        "criado_em": order["criado_em"],
        "status": order["status"],
        "usuario_id": order["usuario_id"],
        "entrega": {"bairro": order["bairro"], "rua": order["rua"], "numero": order["numero"]},
        "total_centavos": order["total_centavos"],
        "itens": [dict(item) for item in items],
    }


def create_order(payload, idempotency_key, item_hook=None, user_id=None):
    if not isinstance(payload, dict):
        raise OrderValidationError("Envie um objeto JSON válido.")
    if not isinstance(idempotency_key, str) or not 8 <= len(idempotency_key) <= 128:
        raise OrderValidationError("Informe uma chave de idempotência válida.")

    db = get_db()
    existing = db.execute("SELECT id FROM pedidos WHERE idempotency_key = ?", (idempotency_key,)).fetchone()
    if existing:
        return serialize_order(existing["id"]), False

    address = _validate_address(payload)
    items = _validate_items(payload.get("itens"))
    total = sum(item.subtotal_cents for item in items)

    try:
        db.execute("BEGIN IMMEDIATE")
        cursor = db.execute(
            """
            INSERT INTO pedidos (bairro, rua, numero, total_centavos, status, idempotency_key, usuario_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (address["bairro"], address["rua"], address["numero"], total, ORDER_STATUS, idempotency_key, user_id),
        )
        order_id = cursor.lastrowid
        for position, item in enumerate(items):
            if item_hook:
                item_hook(position, item)
            db.execute(
                """
                INSERT INTO pedido_itens
                (pedido_id, produto_id, nome_produto, quantidade, preco_unitario_centavos, subtotal_centavos)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (order_id, item.product_id, item.name, item.quantity, item.unit_price_cents, item.subtotal_cents),
            )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return serialize_order(order_id), True
