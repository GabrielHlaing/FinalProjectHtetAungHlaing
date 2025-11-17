# models.py — placeholder for later implementation

class ValidationError(Exception):
    pass

class Transaction:
    @staticmethod
    def validate_type(t_type: str):
        pass

    @staticmethod
    def validate_amount(amount: float):
        pass

    @staticmethod
    def validate_currency(currency: str):
        pass

    @staticmethod
    def validate_category(category: str):
        pass

    @staticmethod
    def validate_date(date_input):
        pass

    @classmethod
    def create(cls, t_type, amount, currency, category, date_input):
        pass
