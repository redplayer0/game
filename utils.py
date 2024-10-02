from __future__ import annotations

import pyxel

from globals import log, messages


def manhattan_distance(p1, p2):
    return sum(abs(a - b) for a, b in zip(p1, p2))


def message(msg, time=5):
    messages.append([msg, time * 90])


def mlog(msg):
    if log:
        if msg == log[-1][0]:
            log[-1][1] += 1
            return
    log.append([msg, 0])


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
