from __future__ import annotations

from card import Half
from globals import action_stack, entities, pickers, scenario, visuals
from states import CardSelection, SetupEntities
from ui import Button, Picker
from utils import mlog


def to_entity_setup():
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


def close_inventory():
    pickers.pop()
    return True


def open_inventory():
    if active := scenario.active_entity:
        if active.items:
            ui = Picker()
            ui.add_button(Button("Back", close_inventory))
            for item in active.items:
                ui.objects.append(item)
            ui.adjust()
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
    if all([e.position for e in entities if e.is_enemy == False]):
        action_stack.pop()
        action_stack.append(CardSelection())
        pickers[-1].add_button(
            Button(
                "Resolve",
                callback=initial_resolve,
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
        action_stack.append(CardSelection())
        return True


def initial_resolve():
    if resolve():
        action_stack.pop()
        close_action_selection()


def close_action_selection():
    ui = Picker()
    ui.add_button(
        Button(
            "Select Action",
            callback=open_action_selection,
            once=True,
        ),
    )
    pickers.append(ui)


def selected_action():
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
            "Skip action",
            callback=skip_action,
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


def open_action_selection():
    if scenario.active_entity:
        active = scenario.active_entity
        ui = Picker(disable_scroll=True)
        ui.add_button(Button("Back", close_action_selection))
        for card in [card for card in active.cards if card.selected]:
            if active.half_selected != "top":
                ui.objects.append(
                    Half(
                        half="top",
                        actions=card.top,
                        user=active,
                        card=card,
                        callback=selected_action,
                    )
                )
            if active.half_selected != "bot":
                ui.objects.append(
                    Half(
                        half="bot",
                        actions=card.bot,
                        user=active,
                        card=card,
                        callback=selected_action,
                    )
                )
        ui.adjust()
        pickers.append(ui)
    else:
        mlog("How did you get here without active entity")


def resolve():
    if all(e.initiative for e in entities if e.is_enemy == False):
        for e in entities:
            if e.is_enemy:
                e.initiative = 100
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
        visuals.shake += 5


def reset_action():
    if not action_stack:
        mlog("No actions in action_stack while trying to reset")
        visuals.shake += 5
        return
    if hasattr(action_stack[-1], "reset"):
        action_stack[-1].reset()
        return True


def skip_action():
    if not action_stack:
        mlog("No actions in action_stack while trying to skip")
        visuals.shake += 5
        return
    if action_stack[-1].skippable:
        # TODO
        # DO what happens in execute but do not execute
        mlog("Skipped action")
        return True


def execute_action():
    if not action_stack:
        mlog("No actions in action_stack while trying to execute")
        visuals.shake += 5
        return
    if hasattr(action_stack[-1], "execute"):
        if action_stack[-1].execute():
            action_stack.pop()
            if not action_stack:
                pickers.pop()
                if scenario.active_entity.half_selected is True:
                    scenario.active_entity.has_acted = True
                    scenario.active_entity.is_active = False
                    pickers.pop()
                    if check_end_turn():
                        # TODO
                        # here go to card selection again and do end turn stuff
                        return True
                    else:
                        resolve()
                        open_action_selection()
                else:
                    open_action_selection()
