from __future__ import annotations

from copy import copy
from random import choice

import actions
import card as c
import entity
from globals import (
    action_stack,
    entities,
    monster_decks,
    monster_selected_cards,
    pickers,
    scenario,
    visuals,
)
from states import CardSelection, SetupEntities
from ui import Button, Picker
from utils import mlog


def to_entity_setup():
    action_stack.append(SetupEntities())
    ui = Picker()
    ui.add_button(Button("Select Cards", validate_setup, once=True))
    ui.add_button(Button("Exit", lambda: exit()))
    pickers.append(ui)


def validate_setup():
    if all([ent.position for ent in entities if isinstance(ent, entity.Character)]):
        action_stack.pop()
        action_stack.append(CardSelection())
        pickers[-1].add_button(Button("Resolve", callback=initial_resolve), pos=1)
        return True


def initial_resolve():
    if all(e.initiative for e in entities if not e.is_enemy):
        draw_monster_cards()
        set_monster_initiatives()
        action_stack.clear()
        resolve()
    else:
        mlog("Choose cards for every character")
        visuals.shake += 5


def draw_monster_cards():
    monster_types = [e.etype for e in entities if isinstance(e, entity.Monster)]
    for mt in monster_types:
        if mt not in monster_decks or mt not in monster_selected_cards:
            print(f"ERROR {mt} not in decks or initiatives")
            return
        selected_card = choice(
            [card for card in monster_decks[mt] if not card.is_discarded]
        )
        selected_card.selected = True
        monster_selected_cards[mt] = selected_card
    mlog("Drew cards for monsters")


def set_monster_initiatives():
    for e in entities:
        if isinstance(e, entity.Monster):
            e.initiative = monster_selected_cards[e.etype].initiative
    for etype, card in monster_selected_cards.items():
        mlog(f"{etype} initiative set to {card.initiative}")


def resolve():
    entities.sort(key=lambda e: (e.has_acted, e.initiative, e.is_elite, e.id))
    scenario.active_entity = entities[0]
    scenario.active_entity.is_active = True
    if isinstance(scenario.active_entity, entity.Character):
        open_action_selection()
    else:
        monster_selected_action()
    mlog(f"{scenario.active_entity.etype}'s turn!")
    return True


def monster_selected_action():
    mt = scenario.active_entity.etype
    for card_action in reversed(monster_selected_cards[mt].actions):
        action = copy(card_action)
        action.user = scenario.active_entity
        action_stack.append(action)
    ui = Picker()
    ui.add_button(Button("Execute action", callback=execute_action, once=True))
    # ui.add_button(Button("Preview action", callback=preview_action))
    # ui.add_button(Button("Reset action", callback=reset_action))
    pickers.append(ui)


def open_action_selection():
    active = scenario.active_entity
    if not isinstance(active, entity.Character):
        mlog("How did you get here without active entity")
        return
    ui = Picker(disable_scroll=True)
    ui.add_button(Button("Back", close_action_selection))
    used_half = active.half_selected
    for card in [card for card in active.cards if card.selected]:
        ui.objects.append(
            c.Half(
                half="top",
                actions=card.top,
                user=active,
                card=card,
                callback=selected_action,
                disabled=used_half == "top",
            )
        )
        ui.objects.append(
            c.Half(
                half="bot",
                actions=card.bot,
                user=active,
                card=card,
                callback=selected_action,
                disabled=used_half == "bot",
            )
        )
    ui.objects.append(
        c.Half(
            half="top",
            actions=[actions.Attack()],
            user=active,
            callback=selected_action,
            disabled=used_half == "top",
        )
    )
    ui.objects.append(
        c.Half(
            half="bot",
            actions=[actions.Move()],
            user=active,
            callback=selected_action,
            disabled=used_half == "bot",
        )
    )
    ui.adjust()
    pickers.append(ui)


def close_action_selection():
    pickers.pop()
    ui = Picker()
    ui.add_button(Button("Select Action", callback=reopen_action_selection, once=True))
    pickers.append(ui)


def reopen_action_selection():
    pickers.pop()
    open_action_selection()


def selected_action():
    pickers.pop()
    ui = Picker()
    ui.add_button(Button("Execute action", callback=execute_action, once=True))
    ui.add_button(Button("Reset action", callback=reset_action))
    ui.add_button(Button("Skip action", callback=skip_action))
    ui.add_button(Button("Inventory", open_inventory))
    pickers.append(ui)
    return True


def execute_action():
    if not action_stack:
        mlog("No actions in action_stack while trying to execute")
        visuals.shake += 5
        return
    if hasattr(action_stack[-1], "execute"):
        if action_stack[-1].execute():
            action_stack.pop()
            post_execution()


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
        action_stack.pop()
        post_execution()
        mlog("Skipped action")
        return True


def preview_action():
    if not action_stack:
        mlog("No actions in action_stack while trying to preview")
        visuals.shake += 5
    if hasattr(action_stack[-1], "preview"):
        action_stack[-1].preview()
        return True


def open_inventory():
    if active := scenario.active_entity:
        if not isinstance(active, entity.Character):
            mlog("Monsters do not have items")
            return
        if active.items:
            ui = Picker()
            ui.add_button(Button("Back", close_inventory))
            for item in active.items:
                ui.objects.append(item)
            ui.adjust()
            pickers.append(ui)
        else:
            mlog(f"{active.etype} does not have items")


def close_inventory():
    pickers.pop()
    return True


def post_execution():
    if not action_stack:
        pickers.pop()
        if isinstance(scenario.active_entity, entity.Character):
            if scenario.active_entity.half_selected is True:
                scenario.active_entity.has_acted = True
                scenario.active_entity.is_active = False
                if check_end_turn():
                    return
                else:
                    discard_characters_cards(scenario.active_entity)
                    resolve()
            else:
                open_action_selection()
        else:
            scenario.active_entity.has_acted = True
            scenario.active_entity.is_active = False
            if check_end_turn():
                return
            else:
                resolve()


def discard_characters_cards(char):
    for c in char.cards:
        if c.selected:
            c.selected = 0
            if not c.is_lost and not c.is_passive:
                c.is_discarded = True


def check_end_turn():
    if all(e.has_acted for e in entities):
        clear_monster_selected_cards()
        clear_characters_selected_cards()
        end_turn_cleanup()
        prepare_next_turn()
        return True


def clear_monster_selected_cards():
    for mt, card in monster_selected_cards.items():
        card.selected = False
        if card.shuffle:
            for c in monster_decks[mt]:
                c.discarded = False
        else:
            card.is_discarded = True
        monster_selected_cards[mt] = None


def clear_characters_selected_cards():
    for e in entities:
        if isinstance(e, entity.Character):
            discard_characters_cards(e)
            e.half_selected = None
        e.initiative = 0
        e.has_acted = False


def end_turn_cleanup():
    # reset active entity
    scenario.active_entity = None
    # reduce turn counters of effects and clean accordingly
    for e in entities:
        for buff in e.on_hit_effects[:]:
            buff.turns -= 1
            if buff.turns == 0:
                e.on_hit_effects.remove(buff)
                mlog(f"{buff.__class__.__name__} ended on {e.etype}")
        for buff in e.on_move_effects[:]:
            buff.turns -= 1
            if buff.turns == 0:
                e.on_hit_effects.remove(buff)
                mlog(f"{buff.__class__.__name__} ended on {e.etype}")
    # TODO
    # handle elements
    # handle looting


def prepare_next_turn():
    mlog(f"Turn {scenario.turn} is over!")
    scenario.turn += 1
    mlog(f"Turn {scenario.turn}! Select cards!")
    action_stack.append(CardSelection())
