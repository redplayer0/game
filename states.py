from __future__ import annotations

import pyxel

from globals import entities, pickers, scenario
from ui import Button, Picker
from utils import mlog


class State:
    def on_click(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass


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


class SetupEntities(State):
    def on_click(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
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


class CardSelection(State):
    def close_card_selection(self):
        if not scenario.active_entity:
            return
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

    def open_card_selection(self):
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
            ui.add_button(Button("Back", self.close_card_selection))
            pickers.append(ui)

    def on_click(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.open_card_selection()
        if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            self.close_card_selection()
