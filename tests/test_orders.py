import sqlite3

import pytest

from app.db import get_db


HEADERS = {"Idempotency-Key": "test-key-123456"}


def post(client, payload, key="test-key-123456"):
    return client.post("/api/pedidos", json=payload, headers={"Idempotency-Key": key})


def test_create_order_and_multiple_items(client, make_order):
    response = post(client, make_order([{"produto_id": 1, "quantidade": 2}, {"produto_id": 2, "quantidade": 3}]))
    order = response.get_json()["pedido"]
    assert response.status_code == 201
    assert order["total_centavos"] == 1360
    assert len(order["itens"]) == 2
    assert order["status"] == "aguardando_pagamento"


@pytest.mark.parametrize("quantity", [0, -1, 1.5, "2", None, 100])
def test_rejects_invalid_quantities(client, make_order, quantity):
    response = post(client, make_order([{"produto_id": 1, "quantidade": quantity}]), key=f"invalid-{quantity}-key")
    assert response.status_code == 400


def test_rejects_empty_cart(client, make_order):
    response = post(client, make_order([]))
    assert response.status_code == 400


def test_rejects_unknown_product(client, make_order):
    response = post(client, make_order([{"produto_id": 99999, "quantidade": 1}]))
    assert response.status_code == 400
    assert "inexistente" in response.get_json()["erro"]


def test_backend_ignores_manipulated_price(client, db, make_order):
    db.execute("UPDATE produtos SET preco_centavos = 5000 WHERE id = 1")
    db.commit()
    payload = make_order([{"produto_id": 1, "quantidade": 1, "preco_centavos": 100}])
    response = post(client, payload)
    assert response.get_json()["pedido"]["total_centavos"] == 5000
    assert response.get_json()["pedido"]["itens"][0]["preco_unitario_centavos"] == 5000


def test_backend_ignores_manipulated_total(client, db, make_order):
    db.execute("UPDATE produtos SET preco_centavos = 10000 WHERE id = 1")
    db.commit()
    response = post(client, make_order(total_centavos=200))
    assert response.get_json()["pedido"]["total_centavos"] == 20000


def test_idempotency_prevents_duplicate_orders(client, db, make_order):
    first = post(client, make_order(), key="same-request-key")
    second = post(client, make_order(), key="same-request-key")
    assert first.status_code == 201
    assert second.status_code == 200
    assert first.get_json()["pedido"]["id"] == second.get_json()["pedido"]["id"]
    assert db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0] == 1


def test_order_accepts_product_beyond_30(client, db, make_order):
    db.executemany(
        "INSERT INTO produtos (nome, categoria, preco_centavos) VALUES (?, 'Teste', 125)",
        [(f"Produto {number}",) for number in range(4, 101)],
    )
    db.commit()
    product_100 = db.execute("SELECT id FROM produtos WHERE nome = 'Produto 100'").fetchone()[0]
    response = post(client, make_order([{"produto_id": product_100, "quantidade": 2}]), key="product-100-key")
    assert response.status_code == 201
    assert response.get_json()["pedido"]["itens"][0]["produto_id"] == product_100


def test_transaction_rolls_back_on_item_failure(app, client, db, make_order):
    def fail_on_second(position, _item):
        if position == 1:
            raise sqlite3.OperationalError("falha provocada")

    app.config["ORDER_ITEM_HOOK"] = fail_on_second
    response = post(client, make_order([{"produto_id": 1, "quantidade": 1}, {"produto_id": 2, "quantidade": 1}]))
    assert response.status_code == 500
    assert db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0] == 0
    assert db.execute("SELECT COUNT(*) FROM pedido_itens").fetchone()[0] == 0


def test_address_errors_are_associated_with_fields(client, make_order):
    response = post(client, make_order(bairro="", rua="", numero=""))
    data = response.get_json()
    assert response.status_code == 400
    assert set(data["campos"]) == {"bairro", "rua", "numero"}
