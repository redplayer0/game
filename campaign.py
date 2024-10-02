from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entity import Character, Monster


@dataclass
class Campaign:
    characters: list[Character] = field(default_factory=list)

    def load(self):
        pass


@dataclass
class Scenario:
    active_entity: Character | Monster = None
    hovered_tile: tuple[int, int] = None
    turn: int = 0
    elements: dict[str, int] = field(default_factory=dict)
