from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from campaign import Scenario

if TYPE_CHECKING:
    from entity import Entity


@dataclass
class Visuals:
    shake: int = 0

    def update(self):
        if self.shake > 0:
            self.shake -= 1


action_stack = []
entities: list[Entity] = []
pickers = []
messages = []
log = []
board = {(x, y): [] for x in range(6) for y in range(6)}
scenario = Scenario()
visuals = Visuals()
monster_decks = {}
monster_selected_cards = {}
