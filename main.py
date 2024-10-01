from __future__ import annotations

import pyxel

from actions import Move
from card import Card
from entity import Entity
from globals import action_stack, board, entities, log, messages, pickers, scenario
from item import Item
from mechanics import to_entity_setup
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
    # update fading messages
    for msg in messages[:]:
        if msg[1] == 0:
            messages.remove(msg)
        else:
            msg[1] -= 1
    # if current picker has objects do not update hovered tile
    if not pickers[-1].objects:
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        tile = (mx // 32, my // 32)
        scenario.hovered_tile = tile if tile in board else None
    # update picker
    pickers[-1].update()
    # if action stack then update
    if action_stack:
        action_stack[-1].update()
    # try click on picker
    if pickers[-1].on_click():
        return
    # try to click for action if did not click for picker
    if action_stack:
        if action_stack[-1].on_click():
            action_stack.pop()


def draw():
    # clear screen
    pyxel.cls(7)
    # draw board
    for tile, objects in board.items():
        draw_tile(tile, 0)
    # draw actions
    if action_stack:
        action_stack[-1].draw()
    # draw cursor
    draw_inner_tile(scenario.hovered_tile, 10)
    # draw entities
    for e in entities:
        e.draw()
    # draw pickers
    if not pyxel.btn(pyxel.MOUSE_BUTTON_MIDDLE):
        pickers[-1].draw()
    # draw action stack for debug
    # for y, s in enumerate(action_stack):
    #     pyxel.text(4, 4 + y * 6, str(s), 1)
    # log view
    n = 5 if len(log) > 5 else len(log)
    for y, msg in enumerate(reversed(log[-n::])):
        if msg[1]:
            text = f"{msg[0]} x{msg[1]+1}"
        else:
            text = msg[0]
        pyxel.rect(3, 230 - y * 8 - 1, len(text) * 4 + 1, 7, 6)
        pyxel.text(4, 230 - y * 8, text, 1)


def load():
    e = Entity(etype="rogue", position=(5, 1))
    e.items = [
        Item("Potion", 3, "Heal 3 hp"),
        Item("Cloak", 5, "Invisible", "body", False),
    ]
    e.cards = [
        Card(
            name="slash",
            initiative=12,
            level=1,
            top=[Move(range=3)],
            bot=[Move(range=2)],
        ),
        Card(
            name="hack",
            initiative=87,
            level=1,
        ),
    ]
    entities.append(e)
    e = Entity(etype="brute", position=(5, 3))
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
    to_entity_setup()
    pyxel.run(update, draw)


if __name__ == "__main__":
    load()
    main()
