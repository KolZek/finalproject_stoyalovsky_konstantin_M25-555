from abc import ABC, abstractmethod
from typing import Dict

from .exceptions import CurrencyNotFoundError


class Currency(ABC):
    """Валюта."""

    def __init__(self, name: str, code: str):
        self._validate_code(code)
        self._validate_name(name)

        self._name = name
        self._code = code.upper()

    @property
    def name(self) -> str:
        return self._name

    @property
    def code(self) -> str:
        return self._code

    @abstractmethod
    def get_display_info(self) -> str:
        pass

    def _validate_code(self, code: str):
        """Валидация валюты."""
        if not isinstance(code, str):
            raise ValueError("Код валюты должен быть строкой")
        if not (2 <= len(code) <= 5):
            raise ValueError("Код валюты должен содержать 2-5 символов")
        if not code.isalpha():
            raise ValueError("Код валюты должен содержать только буквы")
        if not code.isupper():
            raise ValueError("Код валюты должен быть в верхнем регистре")

    def _validate_name(self, name: str):
        """Валидация названия валюты."""
        if not isinstance(name, str):
            raise ValueError("Название валюты должно быть строкой")
        if not name.strip():
            raise ValueError("Название валюты не может быть пустым")


class FiatCurrency(Currency):
    """Фиатная валюта."""

    def __init__(self, name: str, code: str, issuing_country: str):
        super().__init__(name, code)
        self._issuing_country = issuing_country

    @property
    def issuing_country(self) -> str:
        return self._issuing_country

    def get_display_info(self) -> str:
        return f"[FIAT] {self.code} — {self.name} (Страна: {self.issuing_country})"


class CryptoCurrency(Currency):
    """Крипта."""

    def __init__(self, name: str, code: str, algorithm: str, market_cap: float = 0.0):
        super().__init__(name, code)
        self._algorithm = algorithm
        self._market_cap = market_cap

    @property
    def algorithm(self) -> str:
        return self._algorithm

    @property
    def market_cap(self) -> float:
        return self._market_cap

    def get_display_info(self) -> str:
        if self.market_cap > 0:
            mcap_str = f"{self.market_cap:.2e}"
        else:
            mcap_str = "N/A"
        return f"[CRYPTO] {self.code} — {self.name} (Алгоритм: {self.algorithm}, Капитализация: {mcap_str})"  # noqa: E501


_CURRENCY_REGISTRY: Dict[str, Currency] = {}


def register_currency(currency: Currency):
    """Регистрация валюты."""
    _CURRENCY_REGISTRY[currency.code] = currency


def get_currency(code: str) -> Currency:
    """Возвращение валюты по коду."""
    code = code.upper()
    if code not in _CURRENCY_REGISTRY:
        raise CurrencyNotFoundError(code)
    return _CURRENCY_REGISTRY[code]


def get_all_currencies() -> Dict[str, Currency]:
    """Возвращение всех зарегистрированных валют."""
    return _CURRENCY_REGISTRY.copy()


def _initialize_currencies():
    """Инициализация валют."""
    fiats = [
        ("US Dollar", "USD", "США"),
        ("Euro", "EUR", "Еврозона"),
        ("Russian Ruble", "RUB", "Россия"),
        ("British Pound", "GBP", "Великобритания"),
        ("Japanese Yen", "JPY", "Япония"),
    ]

    cryptos = [
        ("Bitcoin", "BTC", "SHA-256", 1.12e12),
        ("Ethereum", "ETH", "Ethash", 4.5e11),
        ("Litecoin", "LTC", "Scrypt", 5.8e9),
        ("Cardano", "ADA", "Ouroboros", 1.2e10),
    ]

    for name, code, country in fiats:
        register_currency(FiatCurrency(name, code, country))

    for name, code, algo, mcap in cryptos:
        register_currency(CryptoCurrency(name, code, algo, mcap))


_initialize_currencies()
