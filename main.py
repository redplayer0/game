from __future__ import annotations

import pyxel

from actions import Move
from card import Card
from entity import Entity
from globals import action_stack, board, entities, log, messages, pickers, scenario
from item import Item
from mechanics import validate_setup
from states import CardSelection, SetupEntities
from ui import Button, Picker
from utils import draw_inner_tile, draw_tile

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


def update():
    for msg in messages[:]:
        if msg[1] == 0:
            messages.remove(msg)
        else:
            msg[1] -= 1

    if not pickers[-1].objects:
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        tile = (mx // 32, my // 32)
        scenario.hovered_tile = tile if tile in board else None
    pickers[-1].update()
    action_stack[-1].update()
    if pickers[-1].on_click():
        return
    if scenario.active_entity:
        if scenario.active_entity.actions:
            scenario.active_entity.actions[-1].update(scenario.hovered_tile)
            return
    if action_stack[-1].on_click():
        action_stack.pop()


def draw():
    pyxel.cls(7)
    for tile, objects in board.items():
        draw_tile(tile, 0)
    if active := scenario.active_entity:
        if active.actions:
            if hasattr(active.actions[-1], "tiles"):
                for tile in active.actions[-1].tiles:
                    fill_tile(tile, 6)
    draw_inner_tile(scenario.hovered_tile, 10)
    for e in entities:
        e.draw()
    if not pyxel.btn(pyxel.MOUSE_BUTTON_MIDDLE):
        pickers[-1].draw()
    # stack = " ".join([a.__name__ for a in action_stack])
    # pyxel.text(4, 4, stack, 1)
    # pyxel.text(4, 12, str(len(pickers)), 6)
    # for y, msg in enumerate(reversed(messages)):
    #     pyxel.rect(3, 230 - y * 8 - 1, len(msg[0]) * 4 + 1, 7, 6)
    #     pyxel.text(4, 230 - y * 8, msg[0], 1)
    n = 5 if len(log) > 5 else len(log)
    for y, msg in enumerate(reversed(log[-n::])):
        if msg[1]:
            text = f"{msg[0]} x{msg[1]+1}"
        else:
            text = msg[0]
        pyxel.rect(3, 230 - y * 8 - 1, len(text) * 4 + 1, 7, 6)
        pyxel.text(4, 230 - y * 8, text, 1)


def load():
    e = Entity(etype="rogue", position=(1, 3))
    e.items = [
        Item("Potion", 3, "Heal 3 hp"),
        Item("Cloak", 5, "Invisible", "body", False),
    ]
    e.cards = [
        Card(
            name="slash",
            initiative=12,
            level=1,
        ),
        Card(
            name="hack",
            initiative=87,
            level=1,
        ),
    ]
    entities.append(e)
    e = Entity(etype="brute", position=(4, 2))
    e.cards = [
        Card(
            name="club",
            initiative=12,
            level=1,
        ),
        Card(
            name="smash",
            initiative=87,
            level=1,
        ),
    ]
    entities.append(e)


def main():
    pyxel.init(320, 240, fps=90)
    pyxel.mouse(True)
    # pyxel.colors.from_list(rose_pine)
    action_stack.append(SetupEntities())
    ui = Picker()
    ui.add_button(
        Button(
            "Select Cards",
            validate_setup,
            once=True,
        ),
    )
    ui.add_button(
        Button("Exit", lambda: exit()),
    )
    pickers.append(ui)

    pyxel.run(update, draw)


if __name__ == "__main__":
    load()
    main()
