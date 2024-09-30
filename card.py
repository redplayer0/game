from globals import board, entities


class Card:
    def __init__(
        self,
        name: str,
        initiative: int,
        top: str,
        bot: str,
        top_actions=None,
        bot_actions=None,
    ):
        self.name = name
        self.initiative = initiative
        self.top = top
        self.bot = bot
        self.selected = 0
        self.top_actions = top_actions or []
        self.bot_actions = bot_actions or []

    def toggle_select(self):
        if self.selected == 0:
            self.selected = 1
        elif self.selected == 1:
            self.selected = 2
        else:
            self.selected = 0

    @property
    def text(self):
        return f"{self.initiative} {self.name} {self.selected if self.selected else ""}"


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


# @dataclass
# class Attack:
#     user: Entity
#     numtargets: int
#     range: int
#     targets: list[Entity] = field(default_factory=list)
