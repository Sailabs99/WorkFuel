"""
Экран профиля сотрудника.
"""

import os
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.fitimage import FitImage
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.dialog import MDDialog
from kivy.uix.modalview import ModalView
from kivy.clock import Clock
from plyer import filechooser

from services.data_manager import DataManager
from services.local_storage import get_avatar_path, save_avatar_path, delete_token, delete_profile
from utils.threading_helper import run_in_thread


class ProfileScreen(MDScreen):
    def __init__(self, data_manager: DataManager, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = data_manager

        self.layout = MDBoxLayout(orientation='vertical')

        # Тулбар с кнопкой "Назад" и заголовком
        self.toolbar = MDTopAppBar(
            title="Профиль",
            left_action_items=[["arrow-left", lambda x: self.go_back()]]
        )
        self.layout.add_widget(self.toolbar)

        # Основной контент будет добавлен позже
        self.content_area = MDBoxLayout(orientation='vertical', padding=20, spacing=20)
        self.layout.add_widget(self.content_area)

        self.add_widget(self.layout)
        self.bind(on_pre_enter=self.load_profile)

    def load_profile(self, *args):
        self.content_area.clear_widgets()
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

        # Кнопка изменения фото
        change_btn = MDFlatButton(text="Сменить фото", pos_hint={'center_x': 0.5},
                                  on_release=self.change_avatar)
        self.content_area.add_widget(avatar_box)
        self.content_area.add_widget(change_btn)

        # Информация о сотруднике
        info_list = MDList()
        fields = [
            ("ФИО", profile.full_name),
            ("Должность", profile.position),
            ("Подразделение", profile.plant),
        ]
        for title, value in fields:
            info_list.add_widget(
                OneLineListItem(text=f"{title}: {value}", divider='Inset')  # Исправлено
            )
        self.content_area.add_widget(info_list)

        # Кнопка "Выйти"
        logout_btn = MDRaisedButton(text="Выйти", size_hint=(1, None), height=50,
                                    on_release=self.logout)
        self.content_area.add_widget(logout_btn)

    def change_avatar(self, instance):
        """Открывает выбор файла изображения."""
        try:
            filechooser.open_file(title="Выберите аватар",
                                  filters=["*.png", "*.jpg", "*.jpeg"],
                                  on_selection=self._on_avatar_selected)
        except Exception as e:
            MDDialog(title="Ошибка", text=f"Ошибка открытия файлов: {str(e)}",
                     auto_dismiss=True).open()

    def _on_avatar_selected(self, selection):
        if selection:
            path = selection[0]
            save_avatar_path(path)
            self.avatar_image.source = path

    def logout(self, instance):
        """Выход из аккаунта."""
        dialog = MDDialog(
            title="Выход",
            text="Вы уверены, что хотите выйти?",
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="Выйти", on_release=lambda x: self._confirm_logout(dialog))
            ]
        )
        dialog.open()

    def _confirm_logout(self, dialog):
        dialog.dismiss()
        self.data_manager.logout()
        self.manager.current = 'login'

    def go_back(self):
        self.manager.current = 'day_menu'