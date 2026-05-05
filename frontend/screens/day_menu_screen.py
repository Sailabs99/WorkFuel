"""
Экран с меню на выбранный день.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import ScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from kivy.clock import Clock
from datetime import date

from services.data_manager import DataManager
from ui.components.top_week_bar import TopWeekBar
from ui.components.day_panel import DayPanel
from utils.threading_helper import run_in_thread


class DayMenuScreen(MDScreen):
    def __init__(self, data_manager: DataManager, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = data_manager
        self.current_day_index = date.today().weekday()
        self.weekly_menu = None

        self.layout = MDBoxLayout(orientation='vertical')

        self.toolbar = MDTopAppBar(
            title="Меню",
            right_action_items=[
                ["account-circle", lambda x: self.go_to_profile()],
                ["refresh", lambda x: self.refresh_menu()]
            ]
        )
        self.layout.add_widget(self.toolbar)

        self.content_layout = MDBoxLayout(orientation='vertical')
        self.layout.add_widget(self.content_layout)
        self.add_widget(self.layout)
        self.bind(on_pre_enter=self.on_pre_enter)

    def on_pre_enter(self, *args):
        self.load_or_refresh_menu()

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
        self.content_layout.clear_widgets()

        if not self.weekly_menu:
            return

        self.week_bar = TopWeekBar(
            weekly_menu=self.weekly_menu,
            current_day_index=day_index,
            on_day_selected=self.on_day_selected
        )
        self.content_layout.add_widget(self.week_bar)

        day_menu = self.weekly_menu.days[day_index]
        panel = DayPanel(day_menu=day_menu)

        scroll = ScrollView()
        scroll.add_widget(panel)
        self.content_layout.add_widget(scroll)

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