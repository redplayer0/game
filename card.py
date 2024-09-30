from __future__ import annotations

from dataclasses import dataclass, field

import pyxel

from globals import entities


class Action: ...


@dataclass(kw_only=True)
class Card:
    name: str
    initiative: int
    level: int
    top: list[Action] = field(default_factory=list)
    bot: list[Action] = field(default_factory=list)
    x: int = 10
    y: int = 0
    w: int = 160
    h: int = 0
    is_hovered: bool = False
    is_discarded: bool = False
    is_lost: bool = False
    is_passive: bool = False
    selected: int = 0
    on_click: str = None

    def __post_init__(self):
        self.h = 12 + sum([ability.lines for ability in self.top + self.bot])

    def toggle_select(self):
        if self.selected == 0:
            self.selected = 1
        elif self.selected == 1:
            self.selected = 2
        else:
            self.selected = 0

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
        for iy, ability in enumerate(self.top + self.bot):
            pyxel.text(x + 4, y + 10 + iy * 6, ability.text, 0)

    @property
    def top_description(self):
        return "\n".join([ability.text for ability in self.top])

    @property
    def bot_description(self):
        return "\n".join([ability.text for ability in self.bot])

    @property
    def title(self):
        return f"{self.initiative} {self.name} lv: {self.level}"


class Move:
    def __init__(self, range: int):
        self.range = range
        self.user = None
        self.card = None
        self.instant = False
        self.tiles = []

    def update(self, hovered_tile):
        if not hovered_tile:
            return
        if hovered_tile not in [e.position for e in entities]:
            self.tiles.append(hovered_tile)

    def execute(self):
        if self.tiles:
            self.user.position = self.tiles[-1]
            return True

    def reset(self):
        self.tiles.clear()
