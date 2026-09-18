from werkzeug.security import check_password_hash

from app import create_app
from app.db import get_db


def register(client, email="cliente@example.com", password="senha-segura-123", name="Cliente Teste"):
    return client.post("/api/auth/cadastro", json={
        "nome": name,
        "email": email,
        "senha": password,
        "confirmacao": password,
    })


def login(client, email="cliente@example.com", password="senha-segura-123"):
    return client.post("/api/auth/login", json={"email": email, "senha": password})


def create_order(client, key, product_id=1, quantity=1, spoofed_user_id=None):
    payload = {
        "bairro": "Centro",
        "rua": "Rua das Flores",
        "numero": "10",
        "itens": [{"produto_id": product_id, "quantidade": quantity}],
    }
    if spoofed_user_id is not None:
        payload["usuario_id"] = spoofed_user_id
    return client.post("/api/pedidos", json=payload, headers={"Idempotency-Key": key})


def test_valid_registration_normalizes_email_and_hashes_password(client, db):
    response = register(client, email="  Cliente@Example.COM  ")
    row = db.execute("SELECT email, senha_hash FROM usuarios").fetchone()
    assert response.status_code == 201
    assert row["email"] == "cliente@example.com"
    assert row["senha_hash"] != "senha-segura-123"
    assert "senha-segura-123" not in row["senha_hash"]
    assert check_password_hash(row["senha_hash"], "senha-segura-123")


def test_registration_validation(client):
    invalid_email = register(client, email="email-invalido")
    short_password = register(client, email="outro@example.com", password="curta")
    mismatch = client.post("/api/auth/cadastro", json={"nome":"Cliente", "email":"novo@example.com", "senha":"senha-segura-123", "confirmacao":"diferente-123"})
    missing = client.post("/api/auth/cadastro", json={})
    assert invalid_email.status_code == 400
    assert "email" in invalid_email.get_json()["campos"]
    assert short_password.status_code == 400
    assert "senha" in short_password.get_json()["campos"]
    assert mismatch.status_code == 400
    assert "confirmacao" in mismatch.get_json()["campos"]
    assert missing.status_code == 400


def test_duplicate_email_is_blocked_by_database(client, db):
    assert register(client, email="Cliente@Example.com").status_code == 201
    duplicate = register(client, email="cliente@example.COM")
    assert duplicate.status_code == 409
    assert duplicate.get_json()["erro"] == "Já existe uma conta cadastrada com este e-mail."
    assert db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 1


def test_login_session_logout_and_protected_access(client):
    register(client)
    assert login(client).status_code == 200
    assert client.get("/api/auth/sessao").get_json()["autenticado"] is True
    assert client.get("/api/conta").status_code == 200
    assert client.post("/api/auth/logout").status_code == 200
    assert client.get("/api/auth/sessao").get_json()["autenticado"] is False
    assert client.get("/api/conta").status_code == 401


def test_login_uses_generic_error(client):
    register(client)
    wrong_password = login(client, password="senha-incorreta")
    missing_user = login(client, email="inexistente@example.com")
    assert wrong_password.status_code == 401
    assert missing_user.status_code == 401
    assert wrong_password.get_json()["erro"] == missing_user.get_json()["erro"] == "E-mail ou senha incorretos."


def test_authenticated_and_guest_orders_get_correct_owner(app, db):
    client = app.test_client()
    register(client)
    login(client)
    user_id = client.get("/api/conta").get_json()["usuario"]["id"]
    authenticated = create_order(client, "authenticated-order", spoofed_user_id=99999)
    client.post("/api/auth/logout")
    guest = create_order(client, "guest-order")
    assert authenticated.get_json()["pedido"]["usuario_id"] == user_id
    assert guest.get_json()["pedido"]["usuario_id"] is None
    rows = db.execute("SELECT usuario_id FROM pedidos ORDER BY id").fetchall()
    assert [row["usuario_id"] for row in rows] == [user_id, None]


def test_users_cannot_access_each_others_orders(app):
    client_a = app.test_client()
    client_b = app.test_client()
    register(client_a, email="a@example.com", name="Usuário A")
    login(client_a, email="a@example.com")
    order_a = create_order(client_a, "order-user-a").get_json()["pedido"]["id"]
    register(client_b, email="b@example.com", name="Usuário B")
    login(client_b, email="b@example.com")
    order_b = create_order(client_b, "order-user-b", product_id=2).get_json()["pedido"]["id"]

    list_a = client_a.get("/api/conta/pedidos").get_json()["pedidos"]
    list_b = client_b.get("/api/conta/pedidos").get_json()["pedidos"]
    assert [order["id"] for order in list_a] == [order_a]
    assert [order["id"] for order in list_b] == [order_b]
    assert client_a.get(f"/api/pedidos/{order_a}").status_code == 200
    assert client_b.get(f"/api/pedidos/{order_b}").status_code == 200
    assert client_a.get(f"/api/pedidos/{order_b}").status_code == 404
    assert client_b.get(f"/api/pedidos/{order_a}").status_code == 404


def test_csrf_is_required_for_state_changes(tmp_path):
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "DATABASE": str(tmp_path / "csrf.sqlite3"),
        "LOAD_SEED_PRODUCTS": False,
        "WTF_CSRF_ENABLED": True,
    })
    client = app.test_client()
    payload = {"nome":"Cliente CSRF", "email":"csrf@example.com", "senha":"senha-segura-123", "confirmacao":"senha-segura-123"}
    assert client.post("/api/auth/cadastro", json=payload).status_code == 400
    token = client.get("/api/auth/csrf").get_json()["csrf_token"]
    assert client.post("/api/auth/cadastro", json=payload, headers={"X-CSRFToken": token}).status_code == 201
