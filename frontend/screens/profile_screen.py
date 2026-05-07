"""
Экран профиля сотрудника.
"""
from kivy.metrics import dp


import os
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.fitimage import FitImage
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock

from services.data_manager import DataManager
from services.local_storage import get_avatar_path, save_avatar_path
from utils.threading_helper import run_in_thread

from kivy.lang import Builder

from ui.theme import RADIUS_XL
from kivy.metrics import dp

# Загружаем kv-стили
Builder.load_file(os.path.join(os.path.dirname(__file__), "profile_screen.kv"))


class ProfileScreen(MDScreen):
    def __init__(self, data_manager: DataManager, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = data_manager
        self.bind(on_pre_enter=self.load_profile)

    def load_profile(self, *args):
        # Очищаем динамическую часть (контейнер с id content_area)
        content = self.ids.content_area
        content.clear_widgets()

        profile = self.data_manager.load_cached_profile()
        if not profile:
            MDDialog(title="Ошибка", text="Профиль не найден, выполните вход заново",
                     auto_dismiss=True).open()
            self.manager.current = 'login'
            return

        # Аватарка с возможностью смены
        avatar_box = MDRelativeLayout(size_hint=(None, None), size=("120dp", "120dp"),
                                      pos_hint={'center_x': 0.5})
        self.avatar_image = FitImage(source=get_avatar_path() or "default_avatar.png",
                                     radius=[60], size_hint=(1,1))
        avatar_box.add_widget(self.avatar_image)

        change_btn = MDFlatButton(text="Сменить фото", pos_hint={'center_x': 0.5},
                                  on_release=self.change_avatar)
        content.add_widget(avatar_box)
        content.add_widget(change_btn)

        # Информация о сотруднике
        info_list = MDList()
        fields = [
            ("ФИО", profile.full_name),
            ("Должность", profile.position),
            ("Подразделение", profile.plant),
        ]
        for title, value in fields:
            info_list.add_widget(
                OneLineListItem(text=f"{title}: {value}")
            )
        content.add_widget(info_list)

        # Кнопка "Выйти"
        logout_btn = MDRaisedButton(
            text="Выйти",
            size_hint=(1, None),
            height=dp(50),
            elevation=0,  # без тени
            radius=[RADIUS_XL, RADIUS_XL, RADIUS_XL, RADIUS_XL],  # 4 одинаковых значения
            on_release=self.logout
        )
        content.add_widget(logout_btn)

    def change_avatar(self, instance):
        from kivymd.uix.dialog import MDDialog
        MDDialog(title="Инфо", text="Смена фото будет доступна позже").open()

    def _on_avatar_selected(self, selection):
        if selection:
            path = selection[0]
            save_avatar_path(path)                  # копирует в локальное хранилище
            # Устанавливаем источник на сохранённый файл
            self.avatar_image.source = get_avatar_path()
            # Принудительно перезагружаем изображение в виджете
            self.avatar_image.reload()

    def logout(self, instance):
        dialog = MDDialog(
            title="Выход",
            text="Вы уверены, что хотите выйти?",
            buttons=[
                MDFlatButton(
                    text="Отмена",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Выйти",
                    elevation=0,
                    radius=[RADIUS_XL, RADIUS_XL, RADIUS_XL, RADIUS_XL],
                    on_release=lambda x: self._confirm_logout(dialog)
                )
            ]
        )
        dialog.open()

    def _confirm_logout(self, dialog):
        dialog.dismiss()
        self.data_manager.logout()
        self.manager.current = 'login'

    def go_back(self):
        self.manager.current = 'day_menu'