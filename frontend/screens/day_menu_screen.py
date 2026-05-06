"""
Экран с меню на выбранный день.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from datetime import date
from kivy.lang import Builder
import os

from services.data_manager import DataManager
from ui.components.top_week_bar import TopWeekBar
from ui.components.day_panel import DayPanel
from utils.threading_helper import run_in_thread

from services.local_storage import get_avatar_path

# Загружаем kv-стили
Builder.load_file(os.path.join(os.path.dirname(__file__), "day_menu_screen.kv"))


class DayMenuScreen(MDScreen):
    def __init__(self, data_manager: DataManager, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = data_manager
        self.current_day_index = date.today().weekday()
        self.weekly_menu = None
        self.bind(on_pre_enter=self.on_pre_enter)

    def on_pre_enter(self, *args):
        self.load_or_refresh_menu()
        self.update_avatar()

    def update_avatar(self):
        avatar_path = get_avatar_path()
        if avatar_path:
            self.ids.profile_avatar.source = avatar_path
        else:
            self.ids.profile_avatar.source = "default_avatar.png"
        # Принудительно обновить изображение
        self.ids.profile_avatar.reload()

    def load_or_refresh_menu(self):
        token = self.data_manager.load_cached_token()
        if not token:
            self.manager.current = 'login'
            return

        def on_success(menu):
            self.weekly_menu = menu
            self.build_ui_for_day(self.current_day_index)

        def on_error(error):
            MDDialog(title="Ошибка", text=f"Не удалось загрузить меню: {error}",
                     auto_dismiss=True).open()

        @run_in_thread(on_success, on_error)
        def _load():
            return self.data_manager.get_weekly_menu(token)

        _load()

    def build_ui_for_day(self, day_index: int):
        self.current_day_index = day_index
        content = self.ids.content_layout  # используем id из kv
        content.clear_widgets()

        if not self.weekly_menu:
            return

        # Верхняя панель дней недели
        week_bar = TopWeekBar(
            weekly_menu=self.weekly_menu,
            current_day_index=day_index,
            on_day_selected=self.on_day_selected
        )
        content.add_widget(week_bar)

        # Панель выбранного дня
        day_menu = self.weekly_menu.days[day_index]
        panel = DayPanel(day_menu=day_menu)
        content.add_widget(panel)

    def on_day_selected(self, index: int):
        self.build_ui_for_day(index)

    def refresh_menu(self):
        token = self.data_manager.load_cached_token()
        if not token:
            self.manager.current = 'login'
            return

        def on_success(menu):
            self.weekly_menu = menu
            self.build_ui_for_day(self.current_day_index)
            MDDialog(title="Успешно", text="Меню обновлено", auto_dismiss=True).open()

        def on_error(error):
            MDDialog(title="Ошибка", text=f"Ошибка обновления: {error}",
                     auto_dismiss=True).open()

        @run_in_thread(on_success, on_error)
        def _refresh():
            return self.data_manager.refresh_menu(token)

        _refresh()

    def go_to_profile(self):
        self.manager.current = 'profile'