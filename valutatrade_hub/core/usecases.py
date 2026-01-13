import secrets
from datetime import datetime
from typing import Any, Dict, Optional

from .models import Portfolio, User
from .utils import DataManager, ExchangeRateService, validate_amount


class UserManager:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.current_user: Optional[User] = None

    def register_user(self, username: str, password: str) -> User:
        """Регистрация пользователя."""
        if not username or not username.strip():
            raise ValueError("Имя пользователя не может быть пустым")

        if len(password) < 4:
            raise ValueError("Пароль должен быть не менее 4 символов")

        users_data = self.data_manager.load_json("users.json", [])
        if any(user["username"] == username for user in users_data):
            raise ValueError(f"Пользователь '{username}' уже существует")

        user_id = self.data_manager.get_next_user_id()
        salt = secrets.token_hex(8)
        hashed_password = self._hash_password(password, salt)
        registration_date = datetime.now()

        user = User(user_id, username, hashed_password, salt, registration_date)

        users_data.append(user.to_dict())
        self.data_manager.save_json("users.json", users_data)

        self._create_user_portfolio(user_id)

        return user

    def login(self, username: str, password: str) -> User:
        """Аутентификация пользователя."""
        users_data = self.data_manager.load_json("users.json", [])

        for user_data in users_data:
            if user_data["username"] == username:
                user = User.from_dict(user_data)
                if user.verify_password(password):
                    self.current_user = user
                    return user
                else:
                    raise ValueError("Неверный пароль")

        raise ValueError(f"Пользователь '{username}' не найден")

    def logout(self):
        """Выход из системы."""
        self.current_user = None

    def _create_user_portfolio(self, user_id: int):
        """Создание пустого портфеля."""
        portfolios_data = self.data_manager.load_json("portfolios.json", [])

        if not any(portfolio["user_id"] == user_id for portfolio in portfolios_data):
            portfolio = Portfolio(user_id)
            portfolios_data.append(portfolio.to_dict())
            self.data_manager.save_json("portfolios.json", portfolios_data)

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        import hashlib
        return hashlib.sha256((password + salt).encode()).hexdigest()


class PortfolioManager:
    def __init__(self, data_manager: DataManager, rate_service: ExchangeRateService):
        self.data_manager = data_manager
        self.rate_service = rate_service

    def get_user_portfolio(self, user_id: int) -> Portfolio:
        """Получение портфеля."""
        portfolios_data = self.data_manager.load_json("portfolios.json", [])

        for portfolio_data in portfolios_data:
            if portfolio_data["user_id"] == user_id:
                return Portfolio.from_dict(portfolio_data)

        portfolio = Portfolio(user_id)
        self._save_portfolio(portfolio)
        return portfolio

    def buy_currency(self, user_id: int, currency_code: str, amount: float) -> Dict[str, Any]:
        """Покупка валюты."""
        if not validate_amount(amount):
            raise ValueError("Сумма должна быть положительной")

        portfolio = self.get_user_portfolio(user_id)
        currency_code = currency_code.upper()

        if currency_code not in portfolio.wallets:
            portfolio.add_currency(currency_code)

        wallet = portfolio.get_wallet(currency_code)
        old_balance = wallet.balance
        wallet.deposit(amount)

        self._save_portfolio(portfolio)

        rate = None
        estimated_cost = None

        rate = self.rate_service.get_rate(currency_code, "USD")

        return {
            "currency": currency_code,
            "amount": amount,
            "rate": rate,
            "estimated_cost": estimated_cost,
            "old_balance": old_balance,
            "new_balance": wallet.balance
        }

    def sell_currency(self, user_id: int, currency_code: str, amount: float) -> Dict[str, Any]:
        """Продажа валюты."""
        if not validate_amount(amount):
            raise ValueError("Сумма должна быть положительной")

        portfolio = self.get_user_portfolio(user_id)
        currency_code = currency_code.upper()

        wallet = portfolio.get_wallet(currency_code)
        if not wallet:
            raise ValueError(f"У вас нет кошелька для валюты '{currency_code}'")

        old_balance = wallet.balance

        wallet.withdraw(amount)

        self._save_portfolio(portfolio)

        rate = None
        estimated_revenue = None

        rate = self.rate_service.get_rate(currency_code, "USD")
        if rate:
            estimated_revenue = amount * rate

        return {
            "currency": currency_code,
            "amount": amount,
            "rate": rate,
            "estimated_revenue": estimated_revenue,
            "old_balance": old_balance,
            "new_balance": wallet.balance
        }

    def _save_portfolio(self, portfolio: Portfolio):
        """Сохранение портфеля в JSON."""
        portfolios_data = self.data_manager.load_json("portfolios.json", [])

        found = False
        for i, portfolio_data in enumerate(portfolios_data):
            if portfolio_data["user_id"] == portfolio.user_id:
                portfolios_data[i] = portfolio.to_dict()
                found = True
                break

        if not found:
            portfolios_data.append(portfolio.to_dict())

        self.data_manager.save_json("portfolios.json", portfolios_data)