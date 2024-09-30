from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pyxel

from globals import entities, scenario

if TYPE_CHECKING:
    from card import Card
    from entity import Entity


@dataclass(kw_only=True)
class Action:
    half: str = None
    instant: bool = False
    lose: bool = False
    x: int = 10
    y: int = 0
    w: int = 160
    h: int = 0
    is_hovered: bool = False
    user: Entity = None
    card: Card = None

    def update(self, mx, my):
        x, y, w, h = self.x, self.y, self.w, self.h
        self.is_hovered = x <= mx <= x + w and y <= my <= y + h
        return self.is_hovered

    def draw(self):
        x, y, w, h = self.x, self.y, self.w, self.h
        pyxel.rect(x, y, w, h, 12 if self.is_hovered else 6)
        pyxel.rectb(x, y, w, h, 1)
        pyxel.text(x + 4, y + 4, self.description, 0)


@dataclass(kw_only=True)
class Move(Action):
    range: int
    fly: bool = False
    jump: bool = False
    tiles: list[tuple[int, int]] = field(default_factory=list)

    def on_click(self):
        hovered_tile = scenario.hovered_tile
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
