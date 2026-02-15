from typing import Any
from backend.core.db import get_conn
from backend.core.security import hash_password

def get_user_by_username(username: str) -> dict[str, Any] | None:
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT id, username, password_hash, role, is_active, created_at FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def list_users() -> list[dict[str, Any]]:
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT id, username, role, is_active, created_at FROM users ORDER BY id ASC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def create_user(username: str, password: str, role: str = "viewer") -> dict[str, Any]:
    if role not in {"admin", "viewer"}:
        raise ValueError("role must be admin or viewer")

    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hash_password(password), role),
        )
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()

def ensure_default_admin(username: str, password: str, role: str = "admin") -> None:
    if get_user_by_username(username):
        return
    create_user(username=username, password=password, role=role)

def set_active(username: str, active: bool) -> None:
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE users SET is_active = ? WHERE username = ?",
            (1 if active else 0, username),
        )
        conn.commit()
    finally:
        conn.close()

def set_role(username: str, role: str) -> None:
    if role not in {"admin", "viewer"}:
        raise ValueError("invalid role")

    conn = get_conn()
    try:
        conn.execute(
            "UPDATE users SET role = ? WHERE username = ?",
            (role, username),
        )
        conn.commit()
    finally:
        conn.close()

def set_password(username: str, new_password: str) -> None:
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE username = ?",
            (hash_password(new_password), username),
        )
        conn.commit()
    finally:
        conn.close()

def delete_user(username: str) -> None:
    conn = get_conn()
    try:
        conn.execute(
            "DELETE FROM users WHERE username = ?",
            (username,),
        )
        conn.commit()
    finally:
        conn.close()
