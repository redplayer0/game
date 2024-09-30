from __future__ import annotations

import pyxel


def draw_tile(tile, color):
    if tile:
        x, y = tile
        pyxel.rectb(x * 32, y * 32, 31, 31, color)


def draw_inner_tile(tile, color):
    if tile:
        x, y = tile
        pyxel.rectb(x * 32 + 1, y * 32 + 1, 29, 29, color)


def fill_tile(tile, color):
    if tile:
        x, y = tile
        pyxel.rect(x * 32 + 1, y * 32 + 1, 29, 29, color)
