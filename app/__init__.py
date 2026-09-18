import os
import secrets
from pathlib import Path

from flask import Flask, send_from_directory
from flask_wtf.csrf import CSRFError

from . import db
from .api import api
from .auth import auth
from .extensions import csrf, limiter


def create_app(test_config=None):
    project_root = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        instance_path=str(project_root / "instance"),
        static_folder=str(project_root / "site"),
        static_url_path="",
    )
    app.config.from_mapping(
        DATABASE=str(project_root / "instance" / "alimentar.sqlite3"),
        LOAD_SEED_PRODUCTS=True,
        JSON_SORT_KEYS=False,
        MAX_CONTENT_LENGTH=64 * 1024,
        SECRET_KEY=os.environ.get("ALIMENTAR_SECRET_KEY") or secrets.token_hex(32),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("ALIMENTAR_HTTPS", "0") == "1",
        WTF_CSRF_TIME_LIMIT=3600,
        WTF_CSRF_ENABLED=True,
        RATELIMIT_STORAGE_URI=os.environ.get("ALIMENTAR_RATELIMIT_STORAGE", "memory://"),
    )
    if test_config:
        app.config.update(test_config)
    if app.config.get("TESTING") and "WTF_CSRF_ENABLED" not in (test_config or {}):
        app.config["WTF_CSRF_ENABLED"] = False

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    app.register_blueprint(api)
    app.register_blueprint(auth)

    @app.get("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.errorhandler(CSRFError)
    def handle_csrf_error(_error):
        return {"erro": "A sessão do formulário expirou. Atualize a página e tente novamente."}, 400

    @app.errorhandler(429)
    def handle_rate_limit(_error):
        return {"erro": "Muitas tentativas. Aguarde um pouco antes de tentar novamente."}, 429

    with app.app_context():
        db.ensure_database()

    return app
