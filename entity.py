import random

import pyxel


class Entity:
    def __init__(self, name, position, is_enemy=False):
        self.name = name
        self.position = position
        self.is_enemy = is_enemy
        self.is_elite = False
        self.initiative = 0
        self.id = random.randint(0, 10000)
        self.in_hand = False
        self.cards = []
        self.items = []
        self.used_items = []
        self.has_acted = False
        self.initiative = None
        self.is_active = False
        self.actions = []
        self.half_selected = None

    def draw(self):
        if self.position and not self.in_hand:
            x, y = self.position
            pyxel.text(x * 32 + 4, y * 32 + 4, self.name, 12)
            if self.is_active:
                pyxel.rectb(x * 32, y * 32, 31, 31, 7)
                pyxel.rectb(x * 32 + 1, y * 32 + 1, 29, 29, 7)

    def draw_at(self, x, y):
        pyxel.text(x, y, self.name, 12)

    # def toggle_select(self, card):
    #     if card in self.selected_cards:
    #         self.selected_cards.remove(card)
    #         self.cards.append(card)
    #         card.selected = False
    #         return True
    #     elif card in self.cards:
    #         if len(self.selected_cards) > 1:
    #             self.selected_cards.pop(0)
    #         self.selected_cards.append(card)
    #         self.cards.remove(card)
    #         card.selected = True
    #         return True
