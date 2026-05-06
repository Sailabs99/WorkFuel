"""
Карточка блюда. Стили полностью заданы в dish_card.kv.
"""

from kivymd.uix.card import MDCard
from shared_models.schemas import Dish

from kivy.lang import Builder
import os

Builder.load_file(os.path.join(os.path.dirname(__file__), "dish_card.kv"))


class DishCard(MDCard):
    def __init__(self, dish: Dish, **kwargs):
        self.dish = dish
        super().__init__(**kwargs)