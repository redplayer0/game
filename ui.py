from __future__ import annotations

from dataclasses import dataclass, field

import pyxel

from card import Card
from item import Item


@dataclass
class Button:
    label: str
    callback: str
    is_hovered: bool = False
    once: bool = False
    x: int = 260
    y: int = 0
    w: int = 0
    h: int = 12

    def __post_init__(self):
        self.w = len(self.label) * 4 + 6

    def on_click(self):
        return self.callback()

    def update(self, mx, my):
        x, y, w, h = self.x, self.y, self.w, self.h
        self.is_hovered = x <= mx <= x + w and y <= my <= y + h
        return self.is_hovered

    def draw(self):
        x, y, w, h = self.x, self.y, self.w, self.h
        pyxel.rect(x, y, w, h, 6 if not self.is_hovered else 12)
        pyxel.rectb(x, y, w, h, 1)
        pyxel.text(x + 4, y + 4, self.label, 0)


@dataclass(kw_only=True)
class Picker:
    objects: list[Card | Item] = field(default_factory=list)
    buttons: list[Button] = field(default_factory=list)
    hovered: Card = None
    disable_scroll: bool = False

    def __post_init__(self):
        self.adjust()

    def add_button(self, button, pos=None):
        if pos:
            self.buttons.insert(pos, button)
        else:
            self.buttons.append(button)
        self.adjust_buttons()

    def adjust_buttons(self):
        for y, button in enumerate(self.buttons):
            button.y = 6 + y * 16

    def adjust(self):
        if self.objects:
            y = 4
            for obj in self.objects:
                obj.y = y
                y += obj.h + 4

    def scroll(self, value):
        if value == 1:
            self.objects.insert(0, self.objects.pop())
        elif value == -1:
            self.objects.append(self.objects.pop(0))

    def on_click(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self.hovered:
                if self.hovered.on_click():
                    if isinstance(self.hovered, Button) and self.hovered.once:
                        self.buttons.remove(self.hovered)
                        self.adjust_buttons()
                    return True

    def update(self):
        self.hovered = None
        x, y = pyxel.mouse_x, pyxel.mouse_y
        if not self.disable_scroll:
            if value := pyxel.mouse_wheel:
                if self.objects:
                    self.scroll(value)
                    self.adjust()
        for obj in self.objects + self.buttons:
            if obj.update(x, y):
                self.hovered = obj

    def draw(self):
        for card in self.objects:
            card.draw()
        for button in self.buttons:
            button.draw()

    def clear(self):
        for obj in self.objects:
            if hasattr(obj, "callback"):
                obj.callback = None
