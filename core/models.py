# models.py

from dataclasses import dataclass
from datetime import datetime


class ValidationError(Exception):
    """Custom exception for invalid transaction data."""
    pass


@dataclass
class Transaction:
    t_type: str
    amount: float
    currency: str
    category: str
    date: datetime

    @staticmethod
    def validate_type(t_type: str):
        valid_types = ["Income", "Expense"]
        if t_type not in valid_types:
            raise ValidationError(f"Invalid transaction type: {t_type}")

    @staticmethod
    def validate_amount(amount: float):
        if amount <= 0:
            raise ValidationError("Amount must be greater than zero.")


    @staticmethod
    def validate_category(category: str):
        if not category.strip():
            raise ValidationError("Category cannot be empty.")

    @staticmethod
    def validate_date(date_input):
        if not isinstance(date_input, (str, datetime)):
            raise ValidationError("Invalid date format.")

        try:
            if isinstance(date_input, str):
                return datetime.strptime(date_input, "%Y-%m-%d")
            return date_input
        except ValueError:
            raise ValidationError("Date must be in YYYY-MM-DD format.")

    @classmethod
    def create(cls, t_type: str, amount: float, currency: str, category: str, date_input):
        """Factory method that validates fields before creating an object."""

        cls.validate_type(t_type)
        cls.validate_amount(amount)
        cls.validate_category(category)
        date_parsed = cls.validate_date(date_input)

        return cls(
            t_type=t_type,
            amount=amount,
            currency=currency,
            category=category,
            date=date_parsed
        )
