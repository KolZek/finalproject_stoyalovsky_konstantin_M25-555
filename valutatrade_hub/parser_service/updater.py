import logging
from typing import Dict

from ..core.exceptions import ApiRequestError
from .api_clients import CoinGeckoClient, ExchangeRateApiClient
from .config import ParserConfig
from .storage import RatesStorage


class RatesUpdater:
    """Обновлние курсов валют."""

    def __init__(self):
        self.config = ParserConfig()
        self.storage = RatesStorage(self.config)
        self.logger = logging.getLogger('parser')

        self.clients = {
            "coingecko": CoinGeckoClient(self.config),
            "exchangerate": ExchangeRateApiClient(self.config)
        }

    def run_update(self, source: str = None) -> Dict[str, float]:
        """Запуск обновления."""
        self.logger.info("Запуск обновления курсов")

        all_rates = {}
        sources_to_update = [source] if source else list(self.clients.keys())

        for client_name in sources_to_update:
            if client_name not in self.clients:
                self.logger.warning(f"Неизвестный источник: {client_name}")
                continue

            try:
                client = self.clients[client_name]
                rates = client.fetch_rates()
                all_rates.update(rates)

                for pair, rate in rates.items():
                    from_currency, to_currency = pair.split('_')
                    self.storage.save_historical_record(
                        from_currency, to_currency, rate, client_name.upper(),
                        {"request_ms": 0, "status_code": 200}
                    )

                self.logger.info(f"Успешно обновлено из {client_name}: {len(rates)} курсов")

            except ApiRequestError as e:
                self.logger.error(f"Ошибка обновления из {client_name}: {e}")
                continue

        if all_rates:
            self.storage.save_current_rates(all_rates, "ParserService")
            self.logger.info(f"Обновление завершено. Всего курсов: {len(all_rates)}")
        else:
            self.logger.warning("Курсы не были обновлены")

        return all_rates