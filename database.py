# database.py

import sqlite3
from typing import List
from models import Transaction
import os

DB_NAME = os.path.join(os.path.dirname(__file__), "moneytracker.db")


# --------------------------------------------------
# 1. DATABASE INITIALIZATION
# --------------------------------------------------
def get_connection():
    """Return a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the transactions table if it does not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            t_type TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        );
    ''')

    conn.commit()
    conn.close()


# --------------------------------------------------
# 2. ADD TRANSACTION
# --------------------------------------------------
def add_transaction(transaction: Transaction) -> int:
    """
    Insert a transaction into the database.
    Returns the ID of the inserted row.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transactions (t_type, amount, currency, category, date)
        VALUES (?, ?, ?, ?, ?);
    """, (
        transaction.t_type,
        transaction.amount,
        transaction.currency,
        transaction.category,
        transaction.date.strftime("%Y-%m-%d")
    ))

    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


# --------------------------------------------------
# 3. FETCH ALL TRANSACTIONS
# --------------------------------------------------
def get_all_transactions() -> List[sqlite3.Row]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM transactions ORDER BY id;")
    rows = cursor.fetchall()

    conn.close()
    return rows


# --------------------------------------------------
# 4. EDIT TRANSACTION
# --------------------------------------------------
def update_transaction(row_id: int, transaction: Transaction) -> bool:
    """
    Update an existing transaction.
    Returns True if one row was updated, False otherwise.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE transactions
        SET t_type = ?, amount = ?, currency = ?, category = ?, date = ?
        WHERE id = ?;
    """, (
        transaction.t_type,
        transaction.amount,
        transaction.currency,
        transaction.category,
        transaction.date.strftime("%Y-%m-%d"),
        row_id
    ))

    conn.commit()
    updated = cursor.rowcount == 1
    conn.close()
    return updated


# --------------------------------------------------
# 5. DELETE TRANSACTION
# --------------------------------------------------
def delete_transaction(row_id: int) -> bool:
    """Delete a transaction by its ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM transactions WHERE id = ?;", (row_id,))
    conn.commit()

    deleted = cursor.rowcount == 1
    conn.close()
    return deleted


# --------------------------------------------------
# 6. FETCH BY FILTERS (optional expansion)
# --------------------------------------------------
def get_transactions_by_type(t_type: str) -> List[sqlite3.Row]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM transactions WHERE t_type = ?;", (t_type,))
    rows = cursor.fetchall()

    conn.close()
    return rows


def get_transactions_by_date_range(start: str, end: str) -> List[sqlite3.Row]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM transactions
        WHERE date BETWEEN ? AND ?
        ORDER BY date ASC;
    """, (start, end))

    rows = cursor.fetchall()
    conn.close()
    return rows

# --------------------------------------------------
# Create a settings table for storing base currency.
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

    # Insert default base currency if none exists
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
