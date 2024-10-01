from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pyxel

from globals import entities, scenario, visuals
from utils import fill_tile, mlog

if TYPE_CHECKING:
    from card import Card
    from entity import Entity


@dataclass(kw_only=True)
class Action:
    half: str = None
    instant: bool = False
    lose: bool = False
    user: Entity = None
    card: Card = None
    skippable: bool = True

    def on_click(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass

    def execute(self):
        pass

    @property
    def lines(self):
        return len(self.text.split("\n"))


@dataclass(kw_only=True)
class Move(Action):
    range: int
    fly: bool = False
    jump: bool = False
    tiles: list[tuple[int, int]] = field(default_factory=list)

    def on_click(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            hovered_tile = scenario.hovered_tile
            if not hovered_tile:
                return
            if hovered_tile not in [e.position for e in entities]:
                self.tiles.append(hovered_tile)
        elif pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            self.reset()

    def draw(self):
        for tile in self.tiles:
            fill_tile(tile, 11)

    def execute(self):
        if self.tiles:
            self.user.position = self.tiles[-1]
            return True
        else:
            mlog(f"Select up to {self.range} tiles to move")
            visuals.shake += 10

    def reset(self):
        self.tiles.clear()

    @property
    def text(self):
        move = "Fly" if self.fly else "Jump" if self.jump else "Move"
        return f"{move} {self.range}"
