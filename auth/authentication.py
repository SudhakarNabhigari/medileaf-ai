"""SQLite authentication (PBKDF2-HMAC-SHA256) and prediction history persistence for MEDILEAF.AI.

Zero hardcoded credentials or pre-populated fake accounts.
Limitation: Local SQLite storage is designed for single-node academic/local Streamlit deployments;
production multi-tenant environments should use external OAuth2/OIDC and HTTPS transport.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.config import DATABASE_PATH

PBKDF2_ITERATIONS = 200_000


def _get_connection(db_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = DATABASE_PATH) -> None:
    """Initialize users, user_preferences, and prediction_history tables."""
    with _get_connection(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                theme TEXT NOT NULL DEFAULT 'Light',
                notifications_enabled INTEGER NOT NULL DEFAULT 1,
                save_history_enabled INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS prediction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                image_thumbnail_b64 TEXT,
                predicted_species TEXT NOT NULL,
                confidence REAL,
                energy_score REAL,
                status TEXT NOT NULL,
                reason TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
        )
        conn.commit()


def _hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    salt_hex = salt or secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        PBKDF2_ITERATIONS,
    )
    return dk.hex(), salt_hex


def register_user(
    username: str,
    email: str,
    password: str,
    db_path: Path = DATABASE_PATH,
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Register a new user with strong validation and salted PBKDF2 hashing."""
    init_db(db_path)
    clean_user = username.strip()
    clean_email = email.strip().lower()

    if len(clean_user) < 3:
        return False, "Username must be at least 3 characters.", None
    if "@" not in clean_email or "." not in clean_email.split("@")[-1]:
        return False, "Please enter a valid email address.", None
    if len(password) < 8:
        return False, "Password must be at least 8 characters.", None

    pw_hash, salt = _hash_password(password)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    try:
        with _get_connection(db_path) as conn:
            cur = conn.execute(
                "INSERT INTO users (username, email, password_hash, salt, created_at) VALUES (?, ?, ?, ?, ?)",
                (clean_user, clean_email, pw_hash, salt, now_iso),
            )
            user_id = cur.lastrowid
            conn.execute("INSERT INTO user_preferences (user_id) VALUES (?)", (user_id,))
            conn.commit()
            return (
                True,
                "Account registered successfully.",
                {"id": user_id, "username": clean_user, "email": clean_email, "created_at": now_iso},
            )
    except sqlite3.IntegrityError:
        return False, "Username or email is already registered.", None


def authenticate_user(
    identifier: str,
    password: str,
    db_path: Path = DATABASE_PATH,
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Authenticate by username or email."""
    init_db(db_path)
    clean_id = identifier.strip()
    if not clean_id or not password:
        return False, "Please enter both email/username and password.", None

    with _get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE lower(email) = lower(?) OR lower(username) = lower(?)",
            (clean_id, clean_id),
        ).fetchone()

    if row is None:
        return False, "Invalid credentials. Please check your username/email and password.", None

    candidate_hash, _ = _hash_password(password, salt=row["salt"])
    if not hmac.compare_digest(candidate_hash, row["password_hash"]):
        return False, "Invalid credentials. Please check your username/email and password.", None

    return (
        True,
        "Signed in successfully.",
        {
            "id": int(row["id"]),
            "username": row["username"],
            "email": row["email"],
            "created_at": row["created_at"],
        },
    )


def change_password(
    user_id: int,
    current_password: str,
    new_password: str,
    db_path: Path = DATABASE_PATH,
) -> Tuple[bool, str]:
    init_db(db_path)
    if len(new_password) < 8:
        return False, "New password must be at least 8 characters."

    with _get_connection(db_path) as conn:
        row = conn.execute("SELECT password_hash, salt FROM users WHERE id = ?", (user_id,)).fetchone()
        if row is None:
            return False, "User account not found."
        curr_hash, _ = _hash_password(current_password, salt=row["salt"])
        if not hmac.compare_digest(curr_hash, row["password_hash"]):
            return False, "Current password is incorrect."
        new_hash, new_salt = _hash_password(new_password)
        conn.execute(
            "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
            (new_hash, new_salt, user_id),
        )
        conn.commit()
    return True, "Password updated successfully."


def get_user_preferences(user_id: int, db_path: Path = DATABASE_PATH) -> Dict[str, Any]:
    init_db(db_path)
    with _get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,)).fetchone()
        if row is None:
            conn.execute("INSERT INTO user_preferences (user_id) VALUES (?)", (user_id,))
            conn.commit()
            return {"theme": "Light", "notifications_enabled": True, "save_history_enabled": True}
        return {
            "theme": row["theme"],
            "notifications_enabled": bool(row["notifications_enabled"]),
            "save_history_enabled": bool(row["save_history_enabled"]),
        }


def update_user_preferences(
    user_id: int,
    theme: str,
    notifications_enabled: bool,
    save_history_enabled: bool,
    db_path: Path = DATABASE_PATH,
) -> None:
    init_db(db_path)
    with _get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO user_preferences (user_id, theme, notifications_enabled, save_history_enabled)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                theme = excluded.theme,
                notifications_enabled = excluded.notifications_enabled,
                save_history_enabled = excluded.save_history_enabled
            """,
            (user_id, theme, int(notifications_enabled), int(save_history_enabled)),
        )
        conn.commit()


def save_prediction_record(
    user_id: int,
    filename: str,
    predicted_species: str,
    confidence: Optional[float],
    energy_score: Optional[float],
    status: str,
    reason: str,
    image_thumbnail_b64: Optional[str] = None,
    db_path: Path = DATABASE_PATH,
) -> None:
    init_db(db_path)
    now_str = datetime.now().strftime("%b %d, %Y %I:%M %p")
    with _get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO prediction_history
                (user_id, filename, image_thumbnail_b64, predicted_species, confidence, energy_score, status, reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                filename,
                image_thumbnail_b64,
                predicted_species,
                confidence,
                energy_score,
                status,
                reason,
                now_str,
            ),
        )
        conn.commit()


def get_prediction_history(user_id: int, limit: int = 50, db_path: Path = DATABASE_PATH) -> List[Dict[str, Any]]:
    init_db(db_path)
    with _get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM prediction_history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def clear_prediction_history(user_id: int, db_path: Path = DATABASE_PATH) -> None:
    init_db(db_path)
    with _get_connection(db_path) as conn:
        conn.execute("DELETE FROM prediction_history WHERE user_id = ?", (user_id,))
        conn.commit()
