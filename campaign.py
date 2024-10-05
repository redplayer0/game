from __future__ import annotations

from dataclasses import dataclass, field

import entity


@dataclass
class Campaign:
    characters: list[entity.Character] = field(default_factory=list)

    def load(self):
        pass


@dataclass
class Scenario:
    active_entity: entity.Entity = None
    hovered_tile: tuple[int, int] = None
    turn: int = 1
    elements: dict[str, int] = field(default_factory=dict)
