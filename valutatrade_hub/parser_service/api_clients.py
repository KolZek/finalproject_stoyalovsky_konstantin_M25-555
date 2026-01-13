import logging
from abc import ABC, abstractmethod
from typing import Dict

import requests

from ..core.exceptions import ApiRequestError
from .config import ParserConfig


class BaseApiClient(ABC):
    """API клиенты."""

    def __init__(self, config: ParserConfig):
        self.config = config
        self.logger = logging.getLogger("parser")

    @abstractmethod
    def fetch_rates(self) -> Dict[str, float]:
        pass

    def _make_request(self, url: str) -> dict:
        """HTTP запрос с обработкой ошибок."""
        try:
            response = requests.get(url, timeout=self.config.REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка запроса: {e}")
            raise ApiRequestError(f"Сетевая ошибка: {e}")
        except ValueError as e:
            self.logger.error(f"Ошибка парсинга JSON: {e}")
            raise ApiRequestError(f"Неверный формат ответа: {e}")


class CoinGeckoClient(BaseApiClient):
    """Клиент для CoinGecko API."""

    def fetch_rates(self) -> Dict[str, float]:
        """Получаем курсы криптовалют."""
        self.logger.info("Получение курсов криптовалют с CoinGecko")

        crypto_ids = [
            self.config.CRYPTO_ID_MAP[code] for code in self.config.CRYPTO_CURRENCIES
        ]
        ids_param = ",".join(crypto_ids)

        url = f"{self.config.COINGECKO_URL}?ids={ids_param}&vs_currencies=usd"

        try:
            data = self._make_request(url)
            rates = {}

            for crypto_code in self.config.CRYPTO_CURRENCIES:
                crypto_id = self.config.CRYPTO_ID_MAP[crypto_code]
                if crypto_id in data and "usd" in data[crypto_id]:
                    rate_key = f"{crypto_code}_{self.config.BASE_CURRENCY}"
                    rates[rate_key] = data[crypto_id]["usd"]

            self.logger.info(f"Получено курсов криптовалют: {len(rates)}")
            return rates

        except ApiRequestError:
            self.logger.error("Не удалось получить курсы криптовалют")
            raise


class ExchangeRateApiClient(BaseApiClient):
    """Клиент для ExchangeRate-API."""

    def fetch_rates(self) -> Dict[str, float]:
        """Получаем курсы фиатных валют."""
        self.logger.info("Получение курсов фиатных валют с ExchangeRate-API")

        if not self.config.EXCHANGERATE_API_KEY:
            self.logger.warning("Ключ ExchangeRate-API не настроен")
            return {}

        url = f"{self.config.EXCHANGERATE_API_URL}/{self.config.EXCHANGERATE_API_KEY}/latest/{self.config.BASE_CURRENCY}"  # noqa: E501

        try:
            data = self._make_request(url)

            if data.get("result") != "success":
                raise ApiRequestError(
                    f"Ошибка API: {data.get('error-type', 'Неизвестная ошибка')}"
                )

            rates = {}
            conversion_rates = data.get("conversion_rates", {})

            for currency in self.config.FIAT_CURRENCIES:
                if currency in conversion_rates:
                    rate_key = f"{currency}_{self.config.BASE_CURRENCY}"
                    rates[rate_key] = conversion_rates[currency]

            self.logger.info(f"Получено курсов фиатных валют: {len(rates)}")
            return rates

        except ApiRequestError:
            self.logger.error("Не удалось получить курсы фиатных валют")
            raise
