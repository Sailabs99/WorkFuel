"""
Менеджер данных.
Обеспечивает загрузку, кэширование и обновление данных.
"""

from services.api_client import ApiClient
from services import local_storage as storage
from shared_models.schemas import EmployeeProfile, WeeklyMenu


class DataManager:
    def __init__(self):
        self.api = ApiClient()

    def authenticate(self, username: str, password: str) -> EmployeeProfile:
        """
        Авторизация: отправляет запрос, сохраняет токен и профиль.
        Возвращает профиль.
        """
        auth_response = self.api.login(username, password)
        storage.save_token(auth_response.token)
        storage.save_profile(auth_response.profile)
        return auth_response.profile

    def load_cached_profile(self) -> EmployeeProfile | None:
        return storage.load_profile()

    def load_cached_token(self) -> str | None:
        return storage.load_token()

    def get_weekly_menu(self, token: str) -> WeeklyMenu:
        """Всегда загружаем свежее меню с сервера."""
        return self.refresh_menu(token)

    def refresh_menu(self, token: str) -> WeeklyMenu:
        """Принудительная загрузка меню с сервера (без сохранения в локальный кэш)."""
        return self.api.fetch_weekly_menu(token)

    def logout(self):
        storage.delete_token()
        storage.delete_profile()
        storage.delete_menu()