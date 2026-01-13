class TradingBaseError(Exception):
    """Базовое исключение."""

    pass


class InsufficientFundsError(TradingBaseError):
    """Недостаточно средств на счете."""

    def __init__(self, currency_code: str, available: float, required: float):
        self.currency_code = currency_code
        self.available = available
        self.required = required
        super().__init__(
            f"Недостаточно средств: доступно {available} {currency_code}, "
            f"требуется {required} {currency_code}"
        )


class CurrencyNotFoundError(TradingBaseError):
    """Неизвестная валюта."""

    def __init__(self, currency_code: str):
        self.currency_code = currency_code
        super().__init__(f"Неизвестная валюта: '{currency_code}'")


class ApiRequestError(TradingBaseError):
    """Ошибка при обращении к API."""

    def __init__(self, reason: str = "Неизвестная ошибка"):
        self.reason = reason
        super().__init__(f"Ошибка обращения к API: {reason}")
