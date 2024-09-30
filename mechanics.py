from __future__ import annotations

from globals import action_stack, entities, pickers, scenario
from states import CardSelection
from ui import Button, Picker
from utils import mlog


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


def validate_setup():
    if all([e.position for e in entities]):
        action_stack.append(CardSelection())
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
