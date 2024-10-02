from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pyxel

import entity
from globals import entities, scenario, visuals
from utils import fill_tile, manhattan_distance, mlog

if TYPE_CHECKING:
    from card import Card, MonsterCard
    from entity import Character, Monster


@dataclass(kw_only=True)
class Action:
    half: str = None
    instant: bool = False
    lose: bool = False
    user: Character | Monster = None
    card: Card | MonsterCard = None
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

    @staticmethod
    def load(data):
        action = globals()[data["action"]]
        del data["action"]
        return action(**data)


@dataclass(kw_only=True)
class Move(Action):
    range: int
    fly: bool = False
    jump: bool = False
    tiles: list[tuple[int, int]] = field(default_factory=list)
    directions = [(-1, 0), (1, 0), (0, 1), (0, -1)]

    def on_click(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            hovered_tile = scenario.hovered_tile
            if not hovered_tile:
                return
            if self.tiles and hovered_tile == self.tiles[-1]:
                self.tiles.pop()
                return
            if len(self.tiles) == self.range:
                mlog(f"You can select up to {self.range} tiles to move")
                visuals.shake += 5
                return
            if hovered_tile not in [e.position for e in entities] + self.tiles:
                x, y = self.tiles[-1] if self.tiles else self.user.position
                neighboors = [(x + d[0], y + d[1]) for d in self.directions]
                if hovered_tile in neighboors:
                    self.tiles.append(hovered_tile)
                else:
                    visuals.shake += 5
        elif pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            self.reset()

    def draw(self):
        for i, tile in enumerate(self.tiles):
            fill_tile(tile, 11)
            x, y = tile
            pyxel.text(x * 32 + 24, y * 32 + 20, str(i + 1), 1)

    def execute(self):
        if isinstance(self.user, entity.Monster):
            return True
        if self.tiles:
            self.user.position = self.tiles[-1]
            self.reset()
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


@dataclass(kw_only=True)
class Attack(Action):
    damage: int
    range: int = 1
    num_targets: int = 1
    pierce: int = 0
    push: int = 0
    pull: int = 0
    inflicts: list[str] = None
    buffs: list[str] = None
    targets: list[tuple[int, int]] = field(default_factory=list)
    directions = [(-1, 0), (1, 0), (0, 1), (0, -1)]

    def on_click(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            hovered_tile = scenario.hovered_tile
            if not hovered_tile:
                return
            if self.targets and hovered_tile == self.targets[-1].position:
                self.targets.pop()
                return
            if len(self.targets) == self.num_targets:
                mlog(f"You can select up to {self.num_targets} targets to attack")
                visuals.shake += 5
                return
            for e in entities:
                if hovered_tile == e.position:
                    if not e.is_enemy:
                        visuals.shake += 5
                        mlog("Must target enemy")
                        return

                    if (
                        manhattan_distance(hovered_tile, self.user.position)
                        <= self.range
                    ):
                        self.targets.append(e)
                        return
                    else:
                        visuals.shake += 5
                        mlog("Out of range")
                        return
        elif pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            self.reset()

    def draw(self):
        for i, tile in enumerate([target.position for target in self.targets]):
            fill_tile(tile, 4)
            x, y = tile
            pyxel.text(x * 32 + 24, y * 32 + 20, str(i + 1), 1)

    def execute(self):
        if isinstance(self.user, entity.Monster):
            return True
        if self.targets:
            for target in self.targets:
                # TODO
                target.hp -= self.damage
            self.reset()
            return True
        else:
            mlog(f"Select up to {self.num_targets} targets to attack")
            visuals.shake += 10

    def reset(self):
        self.targets.clear()

    @property
    def text(self):
        attack = f"Attack {self.damage}"
        if self.pierce:
            attack += f" pierce {self.pierce}"
        if self.pull:
            attack += f" pull {self.pull}"
        if self.push:
            attack += f" pull {self.push}"
        if self.inflicts:
            attack += f" {self.inflicts}"
        if self.num_targets > 1:
            attack += f" [x{self.num_targets}]"
        return attack
