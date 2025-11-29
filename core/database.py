# database.py

import sqlite3
from typing import List, Optional
from core.models import Transaction
import os
from datetime import datetime

DB_NAME = os.path.join(os.path.dirname(__file__), "moneytracker.db")


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Transactions table (original)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            t_type TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            user_id INTEGER
        );
    """)

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    """)

    conn.commit()
    conn.close()


# --------------------------------------------------
# USER HELPERS (used by auth system)
# --------------------------------------------------
def create_user_row(username: str, password_hash: str, salt: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, password_hash, salt, created_at)
        VALUES (?, ?, ?, ?)
    """, (username, password_hash, salt, datetime.now().isoformat()))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_user_row_by_username(username: str) -> Optional[sqlite3.Row]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?;", (username,))
    row = cursor.fetchone()
    conn.close()
    return row


# --------------------------------------------------
# ADD TRANSACTION
# --------------------------------------------------
def add_transaction(transaction: Transaction, user_id: int) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transactions (t_type, amount, currency, category, date, user_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        transaction.t_type,
        transaction.amount,
        transaction.currency,
        transaction.category,
        transaction.date.strftime("%Y-%m-%d"),
        user_id
    ))

    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


# --------------------------------------------------
# FETCH transactions for logged-in user
# --------------------------------------------------
def get_transactions_for_user(user_id: int) -> List[sqlite3.Row]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM transactions
        WHERE user_id = ?
        ORDER BY id;
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


# --------------------------------------------------
# UPDATE TRANSACTION
# --------------------------------------------------
def update_transaction_for_user(row_id: int, transaction: Transaction, user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE transactions
        SET t_type = ?, amount = ?, currency = ?, category = ?, date = ?
        WHERE id = ? AND user_id = ?;
    """, (
        transaction.t_type,
        transaction.amount,
        transaction.currency,
        transaction.category,
        transaction.date.strftime("%Y-%m-%d"),
        row_id,
        user_id
    ))

    conn.commit()
    updated = cursor.rowcount == 1
    conn.close()
    return updated


# --------------------------------------------------
# DELETE TRANSACTION
# --------------------------------------------------
def delete_transaction_for_user(row_id: int, user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM transactions
        WHERE id = ? AND user_id = ?;
    """, (row_id, user_id))
    conn.commit()

    deleted = cursor.rowcount == 1
    conn.close()
    return deleted


# --------------------------------------------------
# SETTINGS TABLE
# --------------------------------------------------
def init_settings():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO settings (key, value)
        VALUES ('base_currency', 'USD');
    """)

    conn.commit()
    conn.close()


def get_setting(key: str) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?;", (key,))
    row = cursor.fetchone()
    conn.close()
    return row["value"] if row else None


def set_setting(key: str, value: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO settings (key, value)
        VALUES (?, ?);
    """, (key, value))
    conn.commit()
    conn.close()
