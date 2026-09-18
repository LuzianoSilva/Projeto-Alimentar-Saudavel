import sqlite3

import pytest

from app import create_app
from app.db import get_db


@pytest.fixture()
def app(tmp_path):
    database = tmp_path / "test.sqlite3"
    app = create_app({
        "TESTING": True,
        "DATABASE": str(database),
        "LOAD_SEED_PRODUCTS": False,
    })
    with app.app_context():
        db = get_db()
        db.executemany(
            "INSERT INTO produtos (nome, categoria, preco_centavos, ativo) VALUES (?, ?, ?, 1)",
            [("Maçã", "Fruta", 350), ("Banana", "Fruta", 220), ("Cenoura", "Legume", 300)],
        )
        db.commit()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    with app.app_context():
        yield get_db()


def order_payload(items=None, **extra):
    payload = {
        "bairro": "Centro",
        "rua": "Rua das Flores",
        "numero": "10",
        "itens": items if items is not None else [{"produto_id": 1, "quantidade": 2}],
    }
    payload.update(extra)
    return payload


@pytest.fixture()
def make_order():
    return order_payload
