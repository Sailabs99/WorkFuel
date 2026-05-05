"""
API-клиент для взаимодействия с бэкендом.
На этапе MVP использует мок-функции из mock_data.
"""

from mock_data.mock_data import mock_login, mock_fetch_menu, mock_fetch_profile
from shared_models.schemas import AuthResponse, WeeklyMenu, EmployeeProfile


class ApiClient:
    def login(self, username: str, password: str) -> AuthResponse:
        # Здесь позже будет POST /auth/login, а пока мок
        return mock_login(username, password)

    def fetch_weekly_menu(self, token: str) -> WeeklyMenu:
        # Здесь позже будет GET /menu с заголовком Authorization
        return mock_fetch_menu(token)

    def fetch_profile(self, token: str) -> EmployeeProfile:
        return mock_fetch_profile(token)