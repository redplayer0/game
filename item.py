class Item:
    def __init__(
        self,
        name: str,
        cost: int,
        desc: str,
        bodypart: str = None,
        consumable: bool = True,
    ):
        self.name = name
        self.cost = cost
        self.desc = desc
        self.bodypart = bodypart
        self.consumable = consumable

    def use(self):
        pass

    @property
    def text(self):
        return f"{self.cost} {self.name}"
