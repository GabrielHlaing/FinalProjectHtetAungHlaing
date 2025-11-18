# app.py
"""
Simple backend testing script for models.py and database.py.
This is NOT part of the Streamlit UI.
"""

from models import Transaction, ValidationError
import database


def test_insert():
    print("=== INSERT TEST ===")

    try:
        t = Transaction.create(
            t_type="Income",
            amount=150,
            currency="USD",
            category="Salary",
            date_input="2025-02-01"
        )

        row_id = database.add_transaction(t)
        print(f"Inserted with ID: {row_id}")

    except ValidationError as e:
        print("Validation error:", e)


def test_fetch_all():
    print("\n=== FETCH ALL TEST ===")

    rows = database.get_all_transactions()

    if not rows:
        print("No transactions found.")
    else:
        for row in rows:
            print(dict(row))


def test_update():
    print("\n=== UPDATE TEST ===")

    rows = database.get_all_transactions()
    if not rows:
        print("Cannot update — no rows.")
        return

    first_row = rows[0]
    row_id = first_row["id"]

    try:
        updated_transaction = Transaction.create(
            t_type="Expense",
            amount=50,
            currency="USD",
            category="Groceries",
            date_input="2025-02-02"
        )

        success = database.update_transaction(row_id, updated_transaction)
        print("Update successful?" , success)

    except ValidationError as e:
        print("Validation error:", e)


def test_delete():
    print("\n=== DELETE TEST ===")

    rows = database.get_all_transactions()
    if not rows:
        print("Cannot delete — no rows.")
        return

    row_id = rows[-1]["id"]  # delete last row for safety

    success = database.delete_transaction(row_id)
    print("Deleted?", success)


def test_settings():
    print("\n=== SETTINGS TEST ===")

    print("Current base currency:", database.get_setting("base_currency"))

    database.set_setting("base_currency", "MMK")
    print("Updated base currency:", database.get_setting("base_currency"))

    # Reset if needed
    database.set_setting("base_currency", "USD")


if __name__ == "__main__":
    print("Initializing DB...")
    database.init_db()
    database.init_settings()

    test_insert()
    test_fetch_all()
    test_update()
    test_fetch_all()
    test_delete()
    test_fetch_all()
    test_settings()

    print("\nAll tests completed.")
