import re
import sqlite3

from flask import Blueprint, jsonify, request, session
from flask_wtf.csrf import generate_csrf
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db
from .extensions import limiter
from .services import serialize_order

auth = Blueprint("auth", __name__, url_prefix="/api")
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
MIN_PASSWORD_LENGTH = 10
MAX_PASSWORD_LENGTH = 128


def normalize_email(value):
    return value.strip().casefold() if isinstance(value, str) else ""


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return get_db().execute(
        "SELECT id, nome, email, criado_em FROM usuarios WHERE id = ? AND ativo = 1",
        (user_id,),
    ).fetchone()


def unauthorized():
    return jsonify({"erro": "É necessário entrar para acessar esta área."}), 401


@auth.get("/auth/csrf")
def csrf_token():
    return jsonify({"csrf_token": generate_csrf()})


@auth.post("/auth/cadastro")
def register():
    payload = request.get_json(silent=True) or {}
    name = payload.get("nome", "").strip() if isinstance(payload.get("nome"), str) else ""
    email = normalize_email(payload.get("email"))
    password = payload.get("senha") if isinstance(payload.get("senha"), str) else ""
    confirmation = payload.get("confirmacao") if isinstance(payload.get("confirmacao"), str) else ""
    errors = {}
    if not 2 <= len(name) <= 120:
        errors["nome"] = "Informe um nome com 2 a 120 caracteres."
    if not email or len(email) > 254 or not EMAIL_PATTERN.fullmatch(email):
        errors["email"] = "Informe um e-mail válido."
    if not MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH:
        errors["senha"] = f"A senha deve possuir entre {MIN_PASSWORD_LENGTH} e {MAX_PASSWORD_LENGTH} caracteres."
    if confirmation != password:
        errors["confirmacao"] = "As senhas não coincidem."
    if errors:
        return jsonify({"erro": "Revise os campos indicados.", "campos": errors}), 400
    try:
        cursor = get_db().execute(
            "INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password)),
        )
        get_db().commit()
    except sqlite3.IntegrityError:
        get_db().rollback()
        return jsonify({"erro": "Já existe uma conta cadastrada com este e-mail.", "campos": {"email": "Já existe uma conta cadastrada com este e-mail."}}), 409
    return jsonify({"usuario": {"id": cursor.lastrowid, "nome": name, "email": email}}), 201


@auth.post("/auth/login")
@limiter.limit("10 per minute; 50 per hour")
def login():
    payload = request.get_json(silent=True) or {}
    email = normalize_email(payload.get("email"))
    password = payload.get("senha") if isinstance(payload.get("senha"), str) else ""
    user = get_db().execute(
        "SELECT id, nome, email, senha_hash FROM usuarios WHERE email = ? AND ativo = 1",
        (email,),
    ).fetchone()
    if not user or not check_password_hash(user["senha_hash"], password):
        return jsonify({"erro": "E-mail ou senha incorretos."}), 401
    session.clear()
    session["user_id"] = user["id"]
    return jsonify({"usuario": {"id": user["id"], "nome": user["nome"], "email": user["email"]}})


@auth.post("/auth/logout")
def logout():
    session.clear()
    return jsonify({"mensagem": "Você saiu da sua conta."})


@auth.get("/auth/sessao")
def session_status():
    user = current_user()
    return jsonify({"autenticado": bool(user), "usuario": dict(user) if user else None})


@auth.get("/conta")
def account():
    user = current_user()
    if not user:
        return unauthorized()
    return jsonify({"usuario": dict(user)})


@auth.get("/conta/pedidos")
def my_orders():
    user = current_user()
    if not user:
        return unauthorized()
    rows = get_db().execute(
        """
        SELECT id, criado_em, total_centavos, status
        FROM pedidos WHERE usuario_id = ? ORDER BY id DESC
        """,
        (user["id"],),
    ).fetchall()
    return jsonify({"pedidos": [dict(row) for row in rows]})


@auth.get("/pedidos/<int:order_id>")
def order_detail(order_id):
    user = current_user()
    if not user:
        return unauthorized()
    owned = get_db().execute(
        "SELECT id FROM pedidos WHERE id = ? AND usuario_id = ?",
        (order_id, user["id"]),
    ).fetchone()
    if not owned:
        return jsonify({"erro": "Pedido não encontrado."}), 404
    return jsonify({"pedido": serialize_order(order_id)})
