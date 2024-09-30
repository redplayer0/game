from __future__ import annotations

import random
from dataclasses import dataclass, field
from pprint import pprint

import pyxel

from card import Card
from item import Item

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


@dataclass(kw_only=True)
class Entity:
    etype: str
    id: int = None
    name: str = None
    is_enemy: bool = False
    is_elite: bool = False
    in_hand: bool = False
    position: tuple[int, int] = None
    initiative: int = 0
    half_selected: str | bool = None
    has_acted: bool = False
    is_active: bool = False
    cards: list[Card] = field(default_factory=list)
    items: list[Item] = field(default_factory=list)
    actions: list = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            self.id = random.randint(0, 10000)

    def draw(self):
        if self.in_hand:
            x, y = pyxel.mouse_x, pyxel.mouse_y
            pyxel.text(x - 12, y - 8, self.etype, 1)
        elif self.position:
            x, y = self.position
            pyxel.text(x * 32 + 4, y * 32 + 4, self.etype, 1)
            if self.name:
                pyxel.text(x * 32 + 4, y * 32 + 10, self.name, 1)
            if self.is_active:
                pyxel.rectb(x * 32 + 1, y * 32 + 1, 29, 29, 9)
                pyxel.rectb(x * 32 + 2, y * 32 + 2, 27, 27, 9)
