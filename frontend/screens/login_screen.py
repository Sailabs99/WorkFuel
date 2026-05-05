"""
Экран авторизации сотрудника.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.snackbar import Snackbar
from kivy.clock import Clock

from services.data_manager import DataManager
from utils.threading_helper import run_in_thread


class LoginScreen(MDScreen):
    def __init__(self, data_manager: DataManager, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = data_manager

        layout = MDBoxLayout(orientation='vertical', padding=30, spacing=20,
                             pos_hint={'center_x': 0.5, 'center_y': 0.5},
                             adaptive_height=True)

        layout.add_widget(MDLabel(text='Вход в систему', halign='center',
                                  font_style='H4'))

        self.username_field = MDTextField(hint_text='Логин', mode='rectangle')
        self.password_field = MDTextField(hint_text='Пароль', password=True,
                                          mode='rectangle')

        layout.add_widget(self.username_field)
        layout.add_widget(self.password_field)

        btn = MDRaisedButton(text='Войти', size_hint=(1, None), height=50)
        btn.bind(on_release=self.login)
        layout.add_widget(btn)

        self.add_widget(layout)

    def on_pre_enter(self, *args):
        """Перед показом экрана: если есть сохранённый токен, пробуем войти автоматически."""
        token = self.data_manager.load_cached_token()
        if token:
            # Автоматическая авторизация
            self._auto_login(token)

    def _auto_login(self, token):
        """Пытается загрузить профиль по токену и перейти на меню."""
        # В мок-режиме загрузка профиля может не требовать токена,
        # но мы реализуем общую логику через DataManager
        def on_success(profile):
            # Всё хорошо, переходим на DayMenuScreen
            self.manager.current = 'day_menu'

        def on_error(error_msg):
            # Токен невалиден, удаляем, остаёмся на экране входа
            self.data_manager.logout()
            # Показываем уведомление? Не нужно, просто остаёмся на этом экране.

        # Запрос профиля или меню, чтобы проверить токен
        self._async_call(self.data_manager.load_cached_profile,
                         on_success, on_error)

    def login(self, instance):
        username = self.username_field.text.strip()
        password = self.password_field.text.strip()

        if not username or not password:
            MDSnackbar(text='Введите логин и пароль').open()
            return

        def on_success(profile):
            MDSnackbar(text=f'Добро пожаловать, {profile.full_name.split()[0]}!').open()
            Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'day_menu'), 0.5)

        def on_error(error_msg):
            MDSnackbar(text=f'Ошибка: {error_msg}').open()

        self._async_call(lambda: self.data_manager.authenticate(username, password),
                         on_success, on_error)

    def _async_call(self, func, on_success, on_error):
        """Оборачивает вызов в поток с колбэками в главном потоке."""
        @run_in_thread(on_success, on_error)
        def wrapper():
            return func()
        wrapper()