"""
Карточка блюда с названием и КБЖУ.
"""

from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from shared_models.schemas import Dish


class DishCard(MDCard):
    def __init__(self, dish: Dish, **kwargs):
        super().__init__(**kwargs)
        self.dish = dish
        self.orientation = "vertical"
        self.padding = "12dp"
        self.spacing = "4dp"
        self.size_hint_y = None
        self.height = "100dp"
        self.radius = "12dp"

        # Название блюда
        name_label = MDLabel(
            text=dish.name,
            font_style="Subtitle1",
            bold=True,
            size_hint_y=None,
            height="24dp"
        )
        # КБЖУ
        macros = f"Калории: {dish.calories} ккал | Б: {dish.proteins}г  Ж: {dish.fats}г  У: {dish.carbs}г"
        macro_label = MDLabel(
            text=macros,
            font_style="Caption",
            size_hint_y=None,
            height="20dp",
            text_color=(0.4, 0.4, 0.4, 1)
        )
        # Аллергены (если есть)
        if dish.allergens:
            allergens_text = "Аллергены: " + ", ".join(dish.allergens)
            aller_label = MDLabel(
                text=allergens_text,
                font_style="Caption",
                size_hint_y=None,
                height="20dp",
                text_color=(0.9, 0.3, 0.3, 1)
            )
            self.add_widget(aller_label)

        self.add_widget(name_label)
        self.add_widget(macro_label)