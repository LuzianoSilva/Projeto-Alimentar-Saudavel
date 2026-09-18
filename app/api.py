import math

from flask import Blueprint, current_app, jsonify, request, session

from .db import get_db
from .services import OrderValidationError, create_order

api = Blueprint("api", __name__, url_prefix="/api")
DEFAULT_LIMIT = 12
MAX_LIMIT = 50


def _positive_int(name, default, maximum=None):
    raw = request.args.get(name, str(default))
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise OrderValidationError(f"O parâmetro {name} deve ser um número inteiro.")
    if value < 1 or (maximum is not None and value > maximum):
        suffix = f" entre 1 e {maximum}" if maximum else " maior que zero"
        raise OrderValidationError(f"O parâmetro {name} deve ser{suffix}.")
    return value


@api.errorhandler(OrderValidationError)
def validation_error(error):
    return jsonify({"erro": str(error), "campos": error.fields}), 400


@api.errorhandler(413)
def too_large(_error):
    return jsonify({"erro": "A solicitação excede o tamanho permitido."}), 413


@api.get("/produtos")
def list_products():
    page = _positive_int("page", 1)
    limit = _positive_int("limit", DEFAULT_LIMIT, MAX_LIMIT)
    query = request.args.get("q", "").strip()
    category = request.args.get("categoria", "").strip()
    if len(query) > 100 or len(category) > 80:
        raise OrderValidationError("Os filtros informados são muito longos.")

    clauses = ["ativo = 1"]
    parameters = []
    if query:
        clauses.append("nome LIKE ? ESCAPE '\\' COLLATE NOCASE")
        escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        parameters.append(f"%{escaped}%")
    if category:
        clauses.append("categoria = ? COLLATE NOCASE")
        parameters.append(category)
    where = " AND ".join(clauses)
    db = get_db()
    total = db.execute(f"SELECT COUNT(*) FROM produtos WHERE {where}", parameters).fetchone()[0]
    total_pages = max(1, math.ceil(total / limit))
    offset = (page - 1) * limit
    rows = db.execute(
        f"""
        SELECT id, nome, categoria, preco_centavos
        FROM produtos WHERE {where}
        ORDER BY nome COLLATE NOCASE, id
        LIMIT ? OFFSET ?
        """,
        (*parameters, limit, offset),
    ).fetchall()
    return jsonify({
        "produtos": [dict(row) for row in rows],
        "paginacao": {"pagina": page, "por_pagina": limit, "total_resultados": total, "total_paginas": total_pages},
    })


@api.get("/produtos/selecionados")
def selected_products():
    raw_ids = request.args.get("ids", "")
    if not raw_ids:
        return jsonify({"produtos": []})
    pieces = raw_ids.split(",")
    if len(pieces) > 100:
        raise OrderValidationError("Consulte no máximo 100 produtos por vez.")
    try:
        ids = sorted({int(piece) for piece in pieces if piece})
    except ValueError:
        raise OrderValidationError("A lista de produtos contém um ID inválido.")
    if not ids or any(product_id < 1 for product_id in ids):
        raise OrderValidationError("A lista de produtos contém um ID inválido.")
    placeholders = ",".join("?" for _ in ids)
    rows = get_db().execute(
        f"SELECT id, nome, categoria, preco_centavos FROM produtos WHERE ativo = 1 AND id IN ({placeholders})",
        ids,
    ).fetchall()
    return jsonify({"produtos": [dict(row) for row in rows]})


@api.get("/categorias")
def list_categories():
    rows = get_db().execute(
        "SELECT DISTINCT categoria FROM produtos WHERE ativo = 1 ORDER BY categoria COLLATE NOCASE"
    ).fetchall()
    return jsonify({"categorias": [row["categoria"] for row in rows]})


@api.post("/pedidos")
def post_order():
    payload = request.get_json(silent=True)
    key = request.headers.get("Idempotency-Key", "")
    try:
        order, created = create_order(payload, key, current_app.config.get("ORDER_ITEM_HOOK"), session.get("user_id"))
    except OrderValidationError as error:
        return validation_error(error)
    except Exception:
        current_app.logger.exception("Falha ao criar pedido")
        return jsonify({"erro": "Não foi possível registrar o pedido. Tente novamente."}), 500
    return jsonify({"pedido": order, "repetido": not created}), 201 if created else 200
