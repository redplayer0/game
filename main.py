from __future__ import annotations

import pyxel

from card import Card, Move
from entity import Entity
from globals import action_stack, board, entities, log, messages, pickers, scenario
from item import Item
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


def message(msg, time=5):
    messages.append([msg, time * 90])


def mlog(msg):
    if log:
        if msg == log[-1][0]:
            log[-1][1] += 1
            return
    log.append([msg, 0])


def main():
    pyxel.init(320, 240, fps=90)
    pyxel.mouse(True)
    # pyxel.colors.from_list(rose_pine)
    action_stack.append(setup_entities)
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


def open_inventory():
    def close_inventory():
        pickers.pop()
        return True

    if active := scenario.active_entity:
        if active.items:
            ui = Picker()
            ui.add_button(Button("Back", close_inventory))
            for item in active.items:
                ui.add_objects(VisualItem(item))
            pickers.append(ui)


def set_active_entity():
    if not scenario.active_entity and scenario.hovered_tile:
        filtered_entities = [
            e
            for e in entities
            if e.position == scenario.hovered_tile and not e.is_enemy
        ]
        if filtered_entities:
            ent = filtered_entities[0]
            scenario.active_entity = ent
            scenario.active_entity.is_active = True
            return True


def setup_entities():
    if scenario.active_entity and scenario.hovered_tile:
        if [e for e in entities if e.position == scenario.hovered_tile]:
            return
        scenario.active_entity.position = scenario.hovered_tile
        scenario.active_entity.in_hand = False
        scenario.active_entity.is_active = False
        scenario.active_entity = None
    else:
        if set_active_entity():
            scenario.active_entity.in_hand = True


def validate_setup():
    if all([e.position for e in entities]):
        action_stack.append(open_card_selection)
        pickers[-1].add_button(
            Button(
                "Resolve",
                callback=first_resolve,
            ),
            pos=1,
        )
        return True


def check_end_turn():
    if all(e.has_acted for e in entities):
        for e in entities:
            for c in e.cards:
                c.selected = 0
            e.has_acted = False
            e.half_selected = None
            e.initiative = 0
        scenario.active_entity = None
        mlog(f"Turn {scenario.turn} is over!")
        scenario.turn += 1
        return True


def first_resolve():
    if resolve():
        ui = Picker()
        ui.add_button(
            Button(
                "Select Action",
                callback=open_action_selection,
                once=True,
            ),
        )
        pickers.append(ui)


def resolve():
    if all(e.initiative for e in entities):
        entities.sort(
            key=lambda e: (
                e.has_acted,
                e.initiative,
                e.is_elite,
                e.id,
            )
        )
        scenario.active_entity = entities[0]
        scenario.active_entity.is_active = True
        mlog(f"{scenario.active_entity.etype}'s turn!")
        return True
    else:
        mlog("Choose cards for every character")


def reset_action():
    if hasattr(scenario.active_entity.actions[-1], "reset"):
        scenario.active_entity.actions[-1].reset()
        return True


def execute_action():
    if hasattr(scenario.active_entity.actions[-1], "execute"):
        if scenario.active_entity.actions[-1].execute():
            scenario.active_entity.actions.pop()
            if scenario.active_entity.actions:
                pickers.pop()
                return True
            else:
                if scenario.active_entity.half_selected is True:
                    scenario.active_entity.has_acted = True
                    scenario.active_entity.is_active = False
                    pickers.pop()
                    if check_end_turn():
                        pickers.pop()
                        return True
                    else:
                        return resolve()
                else:
                    pickers.pop()
                    return True


def open_action_selection():
    def close_action_selection():
        if scenario.active_entity.actions:
            pickers.pop()
            ui = Picker()
            ui.add_button(
                Button(
                    "Execute action",
                    callback=execute_action,
                    once=True,
                ),
            )
            ui.add_button(
                Button(
                    "Reset action",
                    callback=reset_action,
                ),
            )
            ui.add_button(
                Button(
                    "Inventory",
                    open_inventory,
                ),
            )
            pickers.append(ui)
            return True
        else:
            pickers.pop()
            return True

    def set_action(actions, card, half):
        if scenario.active_entity.half_selected is None:
            scenario.active_entity.half_selected = half
        else:
            scenario.active_entity.half_selected = True
        for action in reversed(actions):
            action.user = scenario.active_entity
            action.card = card
            if action.instant:
                action.execute()
            else:
                scenario.active_entity.actions.append(action)
        close_action_selection()
        return True

    if scenario.active_entity:
        active = scenario.active_entity
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
        mlog("How did you get here without active entity")


def open_card_selection():
    def close_card_selection():
        active = scenario.active_entity
        selections = sum(c.selected for c in active.cards)
        if selections != 3:
            mlog("Choose correct number of cards")
        else:
            active.initiative = [
                card.initiative for card in active.cards if card.selected == 1
            ][0]
            mlog(f"{active.etype} initiative set to {active.initiative}")
        scenario.active_entity.is_active = False
        scenario.active_entity = None
        pickers.pop()
        return True

    if set_active_entity():
        active = scenario.active_entity
        ui = Picker(
            objects=[
                card
                for card in active.cards
                if not any([card.is_lost, card.is_discarded, card.is_passive])
            ]
        )
        for card in ui.objects:
            card.on_click = card.toggle_select
        ui.add_button(Button("Back", close_card_selection))
        pickers.append(ui)


def update():
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
            scenario.hovered_tile = tile if tile in board else None
    if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
        if pickers:
            if pickers[-1].on_click():
                return
        if scenario.active_entity:
            if scenario.active_entity.actions:
                scenario.active_entity.actions[-1].update(scenario.hovered_tile)
                return
        if action_stack:
            res = action_stack[-1]()
            if res:
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


if __name__ == "__main__":
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
    main()
