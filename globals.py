from dataclasses import dataclass

from campaign import Scenario


@dataclass
class Visuals:
    shake: int = 0

    def update(self):
        if self.shake > 0:
            self.shake -= 1


action_stack = []
entities = []
pickers = []
messages = []
log = []
board = {(x, y): [] for x in range(6) for y in range(6)}
scenario = Scenario()
visuals = Visuals()
