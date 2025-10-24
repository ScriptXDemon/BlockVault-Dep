from __future__ import annotations
from flask import Flask, current_app, g
import logging
from .sqlite_db import get_sqlite_db, SQLiteDB
from .memory_db import get_memory_db, MemoryDB
from typing import Optional

DB_KEY = "_sqlite_db"


def init_db(app: Flask) -> None:
    @app.before_request
    def _before_request():  # type: ignore
        if DB_KEY not in g:
            db_path = app.config.get("DB_PATH", "blockvault.db")
            try:
                # Use SQLite database
                g._sqlite_db = get_sqlite_db(db_path)  # type: ignore[attr-defined]
                logging.getLogger(__name__).info(f"Using SQLite database: {db_path}")
            except Exception as e:
                logging.getLogger(__name__).warning(
                    "Falling back to in-memory DB because SQLite connection failed: %s", e
                )
                g._sqlite_db = get_memory_db()  # type: ignore[attr-defined]

    @app.teardown_appcontext
    def close_connection(exception: Optional[BaseException]):  # type: ignore
        # SQLite connections are handled automatically by the context manager
        pass


def get_db():
    if getattr(g, "_sqlite_db", None) is None:
        init_db(current_app)
    return g._sqlite_db  # type: ignore[attr-defined]
