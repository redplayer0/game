from __future__ import annotations

import random
from dataclasses import dataclass, field

import pyxel
import toml

from actions import Effect
from card import Card, MonsterCard
from globals import monster_decks, monster_selected_cards
from item import Item

classes = toml.load("characters.toml")
monsters = toml.load("monsters.toml")


@dataclass(kw_only=True)
class Entity:
    etype: str
    name: str = None
    id: int = None
    is_enemy: bool = False
    is_elite: bool = False
    position: tuple[int, int] = None
    initiative: int = 0
    has_acted: bool = False
    is_active: bool = False
    cards: list[Card] = field(default_factory=list)
    level: int = 0
    lv_hp: list[int] = None
    hp: int = None
    on_hit_effects: list[Effect] = field(default_factory=list)
    after_hit_effects: list[Effect] = field(default_factory=list)
    on_move_effects: list[Effect] = field(default_factory=list)

    @property
    def is_alive(self):
        return self.hp > 0

    def draw(self):
        if self.position:
            x, y = self.position
            pyxel.text(
                x * 32 + 4,
                y * 32 + 4,
                f"{self.name or self.etype} {self.hp}",
                1,
            )
            if self.initiative:
                pyxel.text(x * 32 + 4, y * 32 + 10, str(self.initiative), 1)
            if self.is_active:
                pyxel.rectb(x * 32 + 1, y * 32 + 1, 29, 29, 9)
                pyxel.rectb(x * 32 + 2, y * 32 + 2, 27, 27, 9)


@dataclass(kw_only=True)
class Character(Entity):
    in_hand: bool = False
    half_selected: str | bool = None
    stamina: int = None
    exp: int = 0
    hp: int = None

    @property
    def max_hp(self):
        return self.elv_hp[self.level] if self.is_elite else self.lv_hp[self.level - 1]

    def __post_init__(self):
        if not self.id:
            self.id = random.randint(0, 10000)
        if self.position:
            self.position = tuple(self.position)
        if not self.hp:
            self.hp = self.lv_hp[self.level - 1]

    def draw(self):
        if self.in_hand:
            x, y = pyxel.mouse_x, pyxel.mouse_y
            pyxel.text(x - 12, y - 8, self.etype, 1)
            return
        super().draw()

    @staticmethod
    def load(etype):
        if etype not in classes:
            return
        edata = classes[etype]
        if "cards" in edata:
            edata["cards"] = [Card.load(data) for data in edata["cards"]]
        if "items" in edata:
            edata["items"] = [Item.load(data) for data in edata["items"]]
        return Character(**edata)


@dataclass(kw_only=True)
class Monster(Entity):
    lv_mov: list[int] = None
    lv_damage: list[int] = None
    lv_range: list[int] = None
    elv_hp: list[int] = None
    elv_mov: list[int] = None
    elv_damage: list[int] = None
    elv_range: list[int] = None
    hp: int = None
    mov: int = None
    damage: int = None
    range: int = None

    def __post_init__(self):
        if not self.id:
            self.id = random.randint(0, 10000)
        if self.position:
            self.position = tuple(self.position)
        lv = self.level
        if self.is_elite:
            if not self.hp:
                self.hp = self.elv_hp[lv]
            self.mov = self.elv_mov[lv]
            self.damage = self.elv_damage[lv]
            self.range = self.elv_range[lv]
        else:
            if not self.hp:
                self.hp = self.lv_hp[lv]
            self.mov = self.lv_mov[lv]
            self.damage = self.lv_damage[lv]
            self.range = self.lv_range[lv]

    @property
    def max_hp(self):
        return self.elv_hp[self.level] if self.is_elite else self.lv_hp[self.level]

    @staticmethod
    def load(etype):
        if etype not in monsters:
            print(f"No monster of type [{etype}]")
            return
        edata = monsters[etype]
        if etype not in monster_decks:
            monster_decks[etype] = [MonsterCard.load(data) for data in edata["cards"]]
        if etype not in monster_selected_cards:
            monster_selected_cards[etype] = 0
        edata["cards"] = monster_decks[etype]
        return Monster(**edata)
