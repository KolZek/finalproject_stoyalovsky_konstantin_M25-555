from typing import Any


class SettingsLoader:
    """Загрузка конфигурации проекта."""

    _instance = None
    _settings = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsLoader, cls).__new__(cls)
            cls._instance._load_settings()
        return cls._instance

    def _load_settings(self):
        """Зашрузка настроек приложения."""
        self._settings = {
            "data_dir": "data",
            "rates_ttl_seconds": 300,
            "default_base_currency": "USD",
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Значение настройки по ключу."""
        return self._settings.get(key, default)

    def reload(self):
        """Перезагрузка настройки."""
        self._settings = None
        self._load_settings()


settings = SettingsLoader()
