import pyxel

from card import Card, Move
from entity import Entity
from globals import action_stack, board, entities, messages, pickers
from item import Item
from ui import Button, Picker, VisualAction, VisualCard, VisualItem

rose_pine = [
    0x000000,
    0x191724,
    0x1F1D2E,
    0x26233A,
    0x6E6A86,
    0x908CAA,
    0xE0DEF4,
    0xEB6F92,
    0xF6C177,
    0xEBBCBA,
    0x31748F,
    0x9CCFD8,
    0xC4A7E7,
    0x21202E,
    0x403D52,
    0x524F67,
]


def message(msg, time=5):
    messages.append([msg, time * 90])


class New:
    def __init__(self):
        self.turn = 0
        self.active_entity: Entity = None
        self.hovered_tile: tuple[int, int] = None
        pyxel.init(320, 240, fps=90)
        pyxel.mouse(True)
        pyxel.colors.from_list(rose_pine)
        action_stack.append(self.setup_entities)
        ui = Picker()
        ui.add_button(
            Button(
                "Select Cards",
                self.validate_setup,
                once=True,
            ),
        )
        ui.add_button(
            Button("Exit", lambda: exit()),
        )
        pickers.append(ui)

    def run(self):
        pyxel.run(self.update, self.draw)

    def open_inventory(self):
        def close_inventory():
            pickers.pop()
            return True

        if self.active_entity:
            if self.active_entity.items:
                ui = Picker()
                ui.add_button(Button("Back", close_inventory))
                for item in self.active_entity.items:
                    ui.add_objects(VisualItem(item))
                pickers.append(ui)

    def set_active_entity(self):
        if not self.active_entity and self.hovered_tile:
            filtered_entities = [
                e
                for e in entities
                if e.position == self.hovered_tile and not e.is_enemy
            ]
            if filtered_entities:
                ent = filtered_entities[0]
                self.active_entity = ent
                self.active_entity.is_active = True
                return True

    def setup_entities(self):
        if self.active_entity and self.hovered_tile:
            if [e for e in entities if e.position == self.hovered_tile]:
                return
            self.active_entity.position = self.hovered_tile
            self.active_entity.in_hand = False
            self.active_entity.is_active = False
            self.active_entity = None
        else:
            if self.set_active_entity():
                self.active_entity.in_hand = True

    def validate_setup(self):
        if all([e.position for e in entities]):
            action_stack.append(self.open_card_selection)
            print(pickers[-1].objects)
            pickers[-1].add_button(
                Button(
                    "Resolve",
                    callback=self.first_resolve,
                ),
                pos=1,
            )
            return True

    def check_end_turn(self):
        if all(e.has_acted for e in entities):
            for e in entities:
                for c in e.cards:
                    c.selected = 0
                e.has_acted = False
                e.half_selected = None
                e.initiative = 0
            self.active_entity = None
            message(f"Turn {self.turn} is over!")
            self.turn += 1
            return True

    def first_resolve(self):
        if self.resolve():
            ui = Picker()
            ui.add_button(
                Button(
                    "Select Action",
                    callback=self.open_action_selection,
                    once=True,
                ),
            )
            pickers.append(ui)

    def resolve(self):
        if all(e.initiative for e in entities):
            entities.sort(
                key=lambda e: (
                    e.has_acted,
                    e.initiative,
                    e.is_elite,
                    e.id,
                )
            )
            self.active_entity = entities[0]
            self.active_entity.is_active = True
            message(f"{self.active_entity.name}'s turn!")
            return True
        else:
            message("Choose cards for every character")

    def execute_action(self):
        if hasattr(self.active_entity.actions[-1], "execute"):
            if self.active_entity.actions[-1].execute():
                self.active_entity.actions.pop()
                if self.active_entity.actions:
                    pickers.pop()
                    return True
                else:
                    if self.active_entity.half_selected is True:
                        self.active_entity.has_acted = True
                        self.active_entity.is_active = False
                        pickers.pop()
                        if self.check_end_turn():
                            pickers.pop()
                            return True
                        else:
                            return self.resolve()
                    else:
                        pickers.pop()
                        return True

    def open_action_selection(self):
        def close_action_selection():
            if self.active_entity.actions:
                pickers.pop()
                ui = Picker()
                ui.add_button(
                    Button(
                        "Execute action",
                        callback=self.execute_action,
                        once=True,
                    ),
                )
                ui.add_button(
                    Button(
                        "Inventory",
                        self.open_inventory,
                    ),
                )
                pickers.append(ui)
                return True
            else:
                pickers.pop()
                return True

        def set_action(actions, card, half):
            if self.active_entity.half_selected is None:
                self.active_entity.half_selected = half
            else:
                self.active_entity.half_selected = True
            for action in reversed(actions):
                action.user = self.active_entity
                action.card = card
                if action.instant:
                    action.execute()
                else:
                    self.active_entity.actions.append(action)
            close_action_selection()
            return True

        if self.active_entity:
            active = self.active_entity
            if active.actions:
                return
            ui = Picker()
            ui.add_button(Button("Back", close_action_selection))
            for card in [card for card in active.cards if card.selected]:
                if active.half_selected != "top":
                    ui.add_objects(
                        VisualAction(
                            text=card.top,
                            callback=lambda: set_action(card.top_actions, card, "top"),
                        ),
                    )
                if active.half_selected != "bot":
                    ui.add_objects(
                        VisualAction(
                            text=card.bot,
                            callback=lambda: set_action(card.bot_actions, card, "bot"),
                        ),
                    )
            if active.half_selected != "top":
                ui.add_objects(
                    VisualAction(
                        text="Default Attack 2",
                        callback=lambda: set_action([Move(2)], card, "top"),
                    ),
                )
            if active.half_selected != "bot":
                ui.add_objects(
                    VisualAction(
                        text="Default Move 2",
                        callback=lambda: set_action([Move(2)], card, "bot"),
                    ),
                )
            pickers.append(ui)
        else:
            message("How did you get here without active entity")

    def open_card_selection(self):
        def close_card_selection():
            active = self.active_entity
            selections = sum(c.selected for c in active.cards)
            if selections != 3:
                message("Choose correct number of cards")
            else:
                active.initiative = [
                    card.initiative for card in active.cards if card.selected == 1
                ][0]
                message(f"{active.name} initiative set to {active.initiative}")
            self.active_entity.is_active = False
            self.active_entity = None
            pickers.pop()
            return True

        if self.set_active_entity():
            active = self.active_entity
            ui = Picker()
            ui.add_button(Button("Back", close_card_selection))
            for card in active.cards:
                ui.add_objects(
                    VisualCard(
                        card=card,
                        callback=card.toggle_select,
                    ),
                )
            pickers.append(ui)

    def update(self):
        for msg in messages[:]:
            if msg[1] == 0:
                messages.remove(msg)
            else:
                msg[1] -= 1

        if pickers:
            pickers[-1].update()
            if pickers[-1].objects:
                pass
            else:
                mx, my = pyxel.mouse_x, pyxel.mouse_y
                tile = (mx // 32, my // 32)
                self.hovered_tile = tile if tile in board else None
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if pickers:
                if pickers[-1].on_click():
                    return
            if self.active_entity:
                if self.active_entity.actions:
                    self.active_entity.actions[-1].update(self.hovered_tile)
                    return
            if action_stack:
                res = action_stack[-1]()
                if res:
                    action_stack.pop()

    def draw(self):
        pyxel.cls(1)
        for tile, objects in board.items():
            self.draw_tile(tile, 6)
        for e in entities:
            e.draw()
        self.draw_tile(self.hovered_tile, 8)
        if ent := self.active_entity:
            if ent.in_hand:
                x, y = pyxel.mouse_x, pyxel.mouse_y
                ent.draw_at(x + 8, y + 8)
        if not pyxel.btn(pyxel.MOUSE_BUTTON_MIDDLE):
            pickers[-1].draw()
        stack = " ".join([a.__name__ for a in action_stack])
        pyxel.text(4, 4, stack, 6)
        # pyxel.text(4, 12, str(len(pickers)), 6)
        for y, msg in enumerate(reversed(messages)):
            pyxel.rect(3, 230 - y * 8 - 1, len(msg[0]) * 4 + 1, 7, 0)
            pyxel.text(4, 230 - y * 8, msg[0], 6)

    def draw_tile(self, tile, color):
        if tile:
            x, y = tile
            pyxel.rectb(x * 32, y * 32, 31, 31, color)


if __name__ == "__main__":
    e = Entity("rogue", (1, 3))
    e.items = [
        Item("Potion", 3, "Heal 3 hp"),
        Item("Cloak", 5, "Invisible", "body", False),
    ]
    e.cards = [
        Card(
            "slash",
            12,
            "Attack 6, Gain 1 Exp",
            "Move 3, Push 2 (target one adjacent enemy)",
        ),
        Card(
            "hack",
            87,
            "Attack 2, Disarm",
            "Any enemy targeting an adjacent to you ally attacks you instead",
        ),
    ]
    entities.append(e)
    e = Entity("brute", (4, 2))
    e.cards = [
        Card(
            "club",
            12,
            "Attack 12, Gain 1 Exp",
            "Move 3, Push 2 (target one adjacent enemy)",
        ),
        Card(
            "smash",
            87,
            "Attack 2, Disarm",
            "Any enemy targeting an adjacent to you ally attacks you instead",
        ),
    ]
    entities.append(e)
    client = New()
    client.run()
