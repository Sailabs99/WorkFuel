"""
Панель меню одного дня: список блюд и суммарное КБЖУ.
"""

from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from shared_models.schemas import DayMenu
from ui.components.dish_card import DishCard
from ui.theme import WHITE
from kivy.metrics import dp


class DayPanel(MDCard):
    def __init__(self, day_menu: DayMenu, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = WHITE
        self.radius = [dp(16)]
        self.orientation = "vertical"
        self.padding = "16dp"
        self.spacing = "8dp"
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        self.elevation = 0                 # без тени



        # Если выходной – сообщение
        if day_menu.is_weekend or not day_menu.dishes:
            self.add_widget(MDLabel(
                text="Выходной день",
                halign="center",
                theme_text_color="Secondary",
                font_style="Subtitle2"
            ))
        else:
            # Список блюд
            for dish in day_menu.dishes:
                self.add_widget(DishCard(dish=dish))

            # Суммарное КБЖУ
            total_cals = sum(d.calories for d in day_menu.dishes)
            total_prot = sum(d.proteins for d in day_menu.dishes)
            total_fats = sum(d.fats for d in day_menu.dishes)
            total_carbs = sum(d.carbs for d in day_menu.dishes)
            totals_text = f"Итого: {total_cals} ккал, Б: {total_prot:.1f}г, Ж: {total_fats:.1f}г, У: {total_carbs:.1f}г"
            self.add_widget(MDLabel(text=totals_text, font_style="Subtitle2", bold=True, halign="center"))