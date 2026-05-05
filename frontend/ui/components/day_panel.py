"""
Панель меню одного дня: список блюд, суммарное КБЖУ и кнопка "Подробнее".
"""

from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from shared_models.schemas import DayMenu
from ui.components.dish_card import DishCard


class DayPanel(MDCard):
    def __init__(self, day_menu: DayMenu, **kwargs):
        super().__init__(**kwargs)
        self.day_menu = day_menu
        self.orientation = "vertical"
        self.padding = "16dp"
        self.spacing = "8dp"
        self.size_hint_y = None
        # Высота будет автоматически подбираться в зависимости от содержимого
        self.bind(minimum_height=self.setter('height'))
        self.radius = "16dp"

        # Заголовок дня (день недели + дата)
        date_str = day_menu.date.strftime("%d.%m.%Y")
        title = f"{day_menu.weekday}, {date_str}"
        self.add_widget(MDLabel(text=title, font_style="H6", bold=True))

        # Если выходной, показываем соответствующее сообщение
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
            self.add_widget(MDLabel(text=totals_text, font_style="Subtitle2", bold=True))

            # Кнопка "Подробнее"
            btn = MDFlatButton(text="Подробнее", pos_hint={'center_x': 0.5})
            btn.bind(on_release=self.show_details)
            self.add_widget(btn)

    def show_details(self, instance):
        """Открывает диалоговое окно с подробной информацией."""
        if not self.day_menu.summary:
            return
        dialog = MDDialog(
            title="Описание меню",
            text=self.day_menu.summary,
            buttons=[MDFlatButton(text="Закрыть", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()