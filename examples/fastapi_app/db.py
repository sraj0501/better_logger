from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent / "app.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
            """
        )
        conn.commit()


def create_customer(name: str, email: str) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            cursor = conn.execute(
                "INSERT INTO customers (name, email) VALUES (?, ?)",
                (name, email),
            )
            conn.commit()
            customer_id = int(cursor.lastrowid)
    except sqlite3.IntegrityError as exc:
        raise ValueError("duplicate email") from exc

    return {"id": customer_id, "name": name, "email": email}


def list_customers() -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, name, email FROM customers ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]
