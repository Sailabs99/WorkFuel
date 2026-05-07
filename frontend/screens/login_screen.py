"""
Экран авторизации сотрудника.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from utils.snackbar_helper import show_snackbar

from services.data_manager import DataManager
from utils.threading_helper import run_in_thread

from kivy.lang import Builder
import os

# Загружаем kv-стили
Builder.load_file(os.path.join(os.path.dirname(__file__), "login_screen.kv"))


class LoginScreen(MDScreen):
    def __init__(self, data_manager: DataManager, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = data_manager
        self.bind(on_pre_enter=self.auto_login_if_cached)

    def auto_login_if_cached(self, *args):
        token = self.data_manager.load_cached_token()
        if token:
            # Проверяем токен, загружая профиль
            def on_success(profile):
                self.manager.current = 'day_menu'

            def on_error(error):
                self.data_manager.logout()
                # остаёмся на экране входа

            @run_in_thread(on_success, on_error)
            def _check():
                return self.data_manager.load_cached_profile()
            _check()

    def login(self):
        username = self.ids.employee_id.text.strip()
        password = self.ids.password.text.strip()


        if not username or not password:
            show_snackbar('Введите логин и пароль')
            return

        print("LOGIN METHOD CALLED")

        def on_success(profile):
            if profile is None:
                self.data_manager.logout()
                show_snackbar('Сессия устарела, войдите заново')
            else:
                self.manager.current = 'day_menu'

        def on_error(error_msg):
            print("ОШИБКА ВХОДА:", error_msg)
            show_snackbar(f'Ошибка: {error_msg}')

        @run_in_thread(on_success, on_error)
        def _auth():
            return self.data_manager.authenticate(username, password)
        _auth()