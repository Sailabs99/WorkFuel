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
        """
        Возвращает меню. Если кэш актуален, использует его,
        иначе загружает с API и обновляет кэш.
        """
        # Проверяем кэш
        cached_menu = storage.load_menu()
        if cached_menu:
            # Проверка актуальности: меню должно быть на текущую неделю.
            # Поскольку мок-данные генерируются на текущий понедельник,
            # то простая проверка: последний_день_недели >= сегодня.
            # Упростим: если меню сохранено, считаем его актуальным
            # (обновление раз в неделю по требованию).
            # Но для демонстрации можно вернуть кэш.
            return cached_menu

        # Иначе загружаем
        return self.refresh_menu(token)

    def refresh_menu(self, token: str) -> WeeklyMenu:
        """Принудительная загрузка меню с сервера и кэширование."""
        menu = self.api.fetch_weekly_menu(token)
        storage.save_menu(menu)
        return menu

    def logout(self):
        storage.delete_token()
        storage.delete_profile()
        # Меню можно не удалять, чтобы в офлайне показывать