import random

import pyxel

monster_decks = {}


class Deck:
    def __init__(self):
        self.cards = []
        self.current = None

    def add_card(self, card):
        self.cards.append(card)

    def choose(self):
        self.current = random.choice(
            [card for card in self.cards if not card.discarded]
        )

    def cleanup(self):
        self.current.discarded = True
        if self.current.shuffle:
            for card in self.cards:
                card.discarded = False
        self.current = None


class Entity:
    def __init__(self, etype, position, is_enemy=False, name=None):
        self.etype = etype
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
            pyxel.text(x * 32 + 4, y * 32 + 4, self.etype, 1)
            if self.is_active:
                pyxel.rectb(x * 32 + 1, y * 32 + 1, 29, 29, 9)
                pyxel.rectb(x * 32 + 2, y * 32 + 2, 27, 27, 9)

    def draw_at(self, x, y):
        pyxel.text(x, y, self.etype, 1)

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
