from app import create_app
from app.db import get_db


def test_clean_database_receives_public_catalog(tmp_path):
    database = tmp_path / "clean.sqlite3"
    app = create_app({"TESTING": True, "DATABASE": str(database)})

    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM produtos").fetchone()[0] == 30
        assert get_db().execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0
        assert get_db().execute("SELECT COUNT(*) FROM pedidos").fetchone()[0] == 0

    client = app.test_client()
    first_page = client.get("/api/produtos?page=1&limit=12").get_json()
    search = client.get("/api/produtos?q=banana").get_json()
    selected = client.get("/api/produtos/selecionados?ids=1").get_json()
    assert first_page["paginacao"] == {
        "pagina": 1,
        "por_pagina": 12,
        "total_resultados": 30,
        "total_paginas": 3,
    }
    assert len(first_page["produtos"]) == 12
    assert [product["nome"] for product in search["produtos"]] == ["Banana"]
    assert selected["produtos"][0]["nome"] == "Maçã"

    checkout = client.post(
        "/api/pedidos",
        json={
            "bairro": "Bairro de Teste",
            "rua": "Rua de Teste",
            "numero": "1",
            "itens": [{"produto_id": 1, "quantidade": 2}],
        },
        headers={"Idempotency-Key": "clean-install-checkout"},
    )
    assert checkout.status_code == 201
    assert checkout.get_json()["pedido"]["total_centavos"] == 700
