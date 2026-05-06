"""
Верхняя панель с днями недели для быстрой навигации.
"""

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from datetime import date, timedelta
from kivymd.uix.card import MDCard
from kivymd.app import MDApp


class WeekDayButton(MDCard):
    """Кнопка-чип для одного дня."""
    def __init__(self, day_date: date, weekday_name: str, is_selected: bool, **kwargs):
        super().__init__(**kwargs)
        self.day_date = day_date
        self.ripple_behavior = True
        self.size_hint = (None, None)
        self.size = (dp(56), dp(56))
        self.radius = dp(12)
        self.elevation = 0
        app = MDApp.get_running_app()
        self.md_bg_color = app.theme_cls.primary_color if is_selected else (0.9, 0.9, 0.9, 1)
        self.padding = "4dp"

        self.add_widget(MDLabel(
            text=f"{weekday_name[:3]}\n{day_date.day}",
            halign="center",
            font_style="Caption",
            text_color=(1,1,1,1) if is_selected else (0,0,0,1)
        ))


class TopWeekBar(ScrollView):
    """Горизонтальная панель для выбора дня недели с центрированием содержимого."""
    def __init__(self, weekly_menu, current_day_index: int, on_day_selected, **kwargs):
        super().__init__(**kwargs)
        self.do_scroll_x = True
        self.do_scroll_y = False
        self.size_hint_y = None
        self.height = dp(70)

        self.weekly_menu = weekly_menu
        self.current_index = current_day_index
        self.on_day_selected = on_day_selected
        self.buttons = []

        # Горизонтальный контейнер для кнопок
        self.box = MDBoxLayout(orientation='horizontal', spacing=dp(5), size_hint=(None, 1))
        self.box.bind(minimum_width=self.box.setter('width'))

        app = MDApp.get_running_app()
        for i, day_menu in enumerate(weekly_menu.days):
            btn = WeekDayButton(
                day_date=day_menu.date,
                weekday_name=day_menu.weekday,
                is_selected=(i == current_day_index)
            )
            btn.bind(on_release=self._create_day_callback(i))
            self.buttons.append(btn)
            self.box.add_widget(btn)

        self.add_widget(self.box)

        # Пересчитываем отступы при изменении ширины панели или контента
        self.bind(width=self._update_padding)
        self.box.bind(width=self._update_padding)

    def _update_padding(self, *args):
        """Центрируем контент, добавляя левый отступ, когда он уже панели."""
        total_buttons_width = self.box.width
        available = self.width
        if total_buttons_width < available:
            # центрируем – padding слева = половина свободного места
            self.box.padding = [int((available - total_buttons_width) / 2), 0, 0, 0]
        else:
            # контент занимает больше – убираем дополнительный отступ
            self.box.padding = [0, 0, 0, 0]

    def _create_day_callback(self, index):
        def callback(instance):
            app = MDApp.get_running_app()
            for i, btn in enumerate(self.buttons):
                if i == index:
                    btn.md_bg_color = app.theme_cls.primary_color
                    btn.children[0].text_color = (1,1,1,1)
                else:
                    btn.md_bg_color = (0.9, 0.9, 0.9, 1)
                    btn.children[0].text_color = (0,0,0,1)
            self.on_day_selected(index)
        return callback

    def set_active_day(self, index: int):
        if 0 <= index < len(self.buttons):
            self.buttons[index].dispatch('on_release')