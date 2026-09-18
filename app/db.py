import sqlite3
from pathlib import Path

import click
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db():
    connection = get_db()
    schema_path = Path(__file__).with_name("schema.sql")
    connection.executescript(schema_path.read_text(encoding="utf-8"))
    connection.commit()


def seed_products():
    connection = get_db()
    if connection.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]:
        return 0
    if not current_app.config.get("LOAD_SEED_PRODUCTS", True):
        return 0
    seed_path = Path(__file__).with_name("seed_products.sql")
    connection.executescript(seed_path.read_text(encoding="utf-8"))
    connection.commit()
    return connection.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]


def ensure_database():
    init_db()
    columns = {row["name"] for row in get_db().execute("PRAGMA table_info(pedidos)").fetchall()}
    if "usuario_id" not in columns:
        get_db().execute("ALTER TABLE pedidos ADD COLUMN usuario_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL")
    get_db().execute("CREATE INDEX IF NOT EXISTS idx_pedidos_usuario ON pedidos (usuario_id, criado_em DESC)")
    get_db().commit()
    seed_products()


@click.command("init-db")
def init_db_command():
    ensure_database()
    count = get_db().execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
    click.echo(f"Banco inicializado com {count} produtos.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
