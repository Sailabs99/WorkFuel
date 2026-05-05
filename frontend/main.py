import os
import sys

# Добавляем путь к корню проекта, чтобы работали импорты
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager

from screens.login_screen import LoginScreen
from screens.day_menu_screen import DayMenuScreen
from screens.profile_screen import ProfileScreen
from services.data_manager import DataManager


class DietApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.theme_style = "Light"

        self.data_manager = DataManager()

        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login', data_manager=self.data_manager))
        sm.add_widget(DayMenuScreen(name='day_menu', data_manager=self.data_manager))
        sm.add_widget(ProfileScreen(name='profile', data_manager=self.data_manager))

        return sm


if __name__ == '__main__':
    DietApp().run()