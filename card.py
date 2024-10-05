from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pyxel

import actions
from globals import action_stack

if TYPE_CHECKING:
    from entity import Character


@dataclass(kw_only=True)
class Half:
    half: str
    actions: list[actions.Action]
    user: Character
    card: Card = None
    callback: str = None
    disabled: bool = False
    x: int = 10
    y: int = 0
    w: int = 160
    h: int = 0
    is_hovered: bool = False

    def __post_init__(self):
        self.h = 8 + sum([action.lines for action in self.actions]) * 6

    def on_click(self):
        if self.user.half_selected is None:
            self.user.half_selected = self.half
        else:
            self.user.half_selected = True
        for action in reversed(self.actions):
            action.user = self.user
            action.card = self.card
            action_stack.append(action)
        if self.callback:
            self.callback()
        return True

    def update(self, mx, my):
        if not self.disabled:
            x, y, w, h = self.x, self.y, self.w, self.h
            self.is_hovered = x <= mx <= x + w and y <= my <= y + h
            return self.is_hovered

    def draw(self):
        x, y, w, h = self.x, self.y, self.w, self.h
        pyxel.rect(x, y, w, h, 12 if self.is_hovered else 13 if self.disabled else 6)
        pyxel.rectb(x, y, w, h, 1)
        for iy, ability in enumerate(self.actions):
            pyxel.text(x + 4, y + 4 + iy * 6, ability.text, 0)


@dataclass(kw_only=True)
class Card:
    name: str
    initiative: int
    level: int
    top: list[actions.Action] = field(default_factory=list)
    bot: list[actions.Action] = field(default_factory=list)
    etype: str = None
    x: int = 10
    y: int = 0
    w: int = 160
    h: int = 0
    is_hovered: bool = False
    is_discarded: bool = False
    is_lost: bool = False
    is_passive: bool = False
    selected: int = 0
    is_checked: bool = False
    on_click: str = None

    def __post_init__(self):
        self.h = 26 + sum([ability.lines for ability in self.top + self.bot]) * 6

    def toggle_select(self):
        if self.selected == 0:
            self.selected = 1
        elif self.selected == 1:
            self.selected = 2
        else:
            self.selected = 0

    def toggle_checked(self):
        self.is_checked = not self.is_checked

    def update(self, mx, my):
        x, y, w, h = self.x, self.y, self.w, self.h
        self.is_hovered = x <= mx <= x + w and y <= my <= y + h
        return self.is_hovered

    def draw(self):
        x, y, w, h = self.x, self.y, self.w, self.h
        col = 6
        if self.selected == 1:
            col = 14
        elif self.selected == 2:
            col = 8
        elif self.is_discarded:
            col = 13
        elif self.is_lost:
            col = 4
        elif self.is_hovered:
            col = 12
        pyxel.rect(x, y, w, h, col)
        pyxel.rectb(x, y, w, h, 10 if self.is_checked else 1)
        pyxel.text(x + 4, y + 4, self.title, 0)
        pyxel.text(x + 4, y + 10, "-----", 0)
        iy = 1
        for ability in self.top:
            pyxel.text(x + 4, y + 10 + iy * 6, ability.text, 0)
            iy += 1
        pyxel.text(x + 4, y + 10 + iy * 6, "-----", 0)
        iy += 1
        for ability in self.bot:
            pyxel.text(x + 4, y + 10 + iy * 6, ability.text, 0)
            iy += 1

    @property
    def top_description(self):
        return "\n".join([ability.text for ability in self.top])

    @property
    def bot_description(self):
        return "\n".join([ability.text for ability in self.bot])

    @property
    def title(self):
        return f"{self.initiative} {self.name} lv: {self.level}"

    @staticmethod
    def load(data):
        data["top"] = [actions.Action.load(a) for a in data["top"]]
        data["bot"] = [actions.Action.load(a) for a in data["bot"]]
        card = Card(**data)
        return card


@dataclass(kw_only=True)
class MonsterCard:
    initiative: int
    shuffle: bool = False
    actions: list[actions.Action] = field(default_factory=list)
    x: int = 10
    y: int = 0
    w: int = 160
    h: int = 0
    is_hovered: bool = False
    is_discarded: bool = False
    is_lost: bool = False
    is_passive: bool = False
    selected: bool = False
    on_click: str = None

    def __post_init__(self):
        self.h = 26 + sum([ability.lines for ability in self.actions]) * 6

    def update(self, mx, my):
        x, y, w, h = self.x, self.y, self.w, self.h
        self.is_hovered = x <= mx <= x + w and y <= my <= y + h
        return self.is_hovered

    def draw(self):
        x, y, w, h = self.x, self.y, self.w, self.h
        col = 6
        if self.selected == 1:
            col = 4
        elif self.selected == 2:
            col = 14
        elif self.is_hovered:
            col = 12
        pyxel.rect(x, y, w, h, col)
        pyxel.rectb(x, y, w, h, 1)
        pyxel.text(x + 4, y + 4, self.title, 0)
        pyxel.text(x + 4, y + 10, "-----", 0)
        iy = 1
        for ability in self.actions:
            pyxel.text(x + 4, y + 10 + iy * 6, ability.text, 0)
            iy += 1

    @property
    def description(self):
        return "\n".join([ability.text for ability in self.actions])

    @property
    def title(self):
        return f"Initiative {self.initiative}"

    @staticmethod
    def load(data):
        data["actions"] = [actions.Action.load(a) for a in data["actions"]]
        card = MonsterCard(**data)
        return card
