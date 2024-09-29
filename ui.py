import pyxel


class VisualAction:
    def __init__(self, text, callback):
        self.text = text
        self.callback = callback
        self.x = 10
        self.w = 160
        self.h = 30
        self.hovered = False

    def on_click(self):
        self.callback()

    def update(self, mx, my, y):
        x, w, h = self.x, self.w, self.h
        self.hovered = x <= mx <= x + w and y <= my <= y + h
        return self.hovered

    def draw(self, y):
        x, w, h = self.x, self.w, self.h
        pyxel.rect(x, y, w, h, 3)
        pyxel.rectb(x, y, w, h, 6 if not self.hovered else 8)
        pyxel.text(x + 4, y + 4, self.text, 6)


class VisualCard:
    def __init__(self, card, callback):
        self.card = card
        self.callback = callback
        self.scroll = 0
        self.x = 10
        self.w = 160
        self.h = 40
        self.hovered = False

    def on_click(self):
        self.callback()

    def update(self, mx, my, y):
        x, w, h = self.x, self.w, self.h
        self.hovered = x <= mx <= x + w and y <= my <= y + h
        return self.hovered

    def draw(self, y):
        x, w, h = self.x, self.w, self.h
        pyxel.rect(x, y, w, h, 14 if self.card.selected else 3)
        pyxel.rectb(x, y, w, h, 6 if not self.hovered else 8)
        pyxel.text(x + 4, y + 4, self.card.text, 6)


class VisualItem:
    def __init__(self, item):
        self.item = item
        self.callback = item.use
        self.scroll = 0
        self.x = 10
        self.w = 80
        self.h = 40
        self.hovered = False

    def on_click(self):
        self.callback()

    def update(self, mx, my, y):
        x, w, h = self.x, self.w, self.h
        self.hovered = x <= mx <= x + w and y <= my <= y + h
        return self.hovered

    def draw(self, y):
        x, w, h = self.x, self.w, self.h
        pyxel.rect(x, y, w, h, 3)
        pyxel.rectb(x, y, w, h, 6 if not self.hovered else 8)
        pyxel.text(x + 4, y + 4, self.item.text, 6)


class Button:
    def __init__(self, label: str, callback, once=False):
        self.label = label
        self.callback = callback
        self.width = len(self.label) * 4
        self.hovered = False
        self.once = once
        self.x = 260
        self.y = 0
        self.w = self.width + 6
        self.h = 12

    def on_click(self):
        return self.callback()

    def update(self, mx, my):
        x, y, w, h = self.x, self.y, self.w, self.h
        self.hovered = x <= mx <= x + w and y <= my <= y + h
        return self.hovered

    def draw(self):
        x, y, w, h = self.x, self.y, self.w, self.h
        pyxel.rect(x, y, w, h, 3)
        pyxel.rectb(x, y, w, h, 6 if not self.hovered else 8)
        pyxel.text(x + 4, y + 4, self.label, 6)


class Picker:
    def __init__(self):
        self.card_scroll = 0
        self.objects = []
        self.buttons = []
        self.hovered = None

    def add_objects(self, obj):
        self.objects.append(obj)

    def add_button(self, button, pos=None):
        if pos:
            self.buttons.insert(pos, button)
        else:
            self.buttons.append(button)
        self.adjust_buttons()

    def adjust_buttons(self):
        for y, button in enumerate(self.buttons):
            button.y = 6 + y * 16

    def update(self):
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        self.hovered = None
        for button in self.buttons:
            if button.update(mx, my):
                self.hovered = button
        for y, obj in enumerate(self.objects):
            if obj.update(mx, my, 6 + y * (obj.h + 4)):
                self.hovered = obj

    def on_click(self):
        if self.hovered:
            if self.hovered.on_click():
                if self.hovered.once:
                    self.buttons.remove(self.hovered)
                    self.adjust_buttons()
                return True

    def draw(self):
        for button in self.buttons:
            button.draw()
        for y, obj in enumerate(self.objects):
            obj.draw(6 + y * (obj.h + 4))
