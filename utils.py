from __future__ import annotations

import heapq

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


def a_star(start, goal, positions, max_x, max_y, is_valid=None):
    def heuristic(a, b):
        # Using Manhattan distance as heuristic
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(node):
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for direction in directions:
            neighbor = (node[0] + direction[0], node[1] + direction[1])
            if (
                0 <= neighbor[0] <= max_x
                and 0 <= neighbor[1] <= max_y
                and neighbor in positions
                and is_valid(neighbor)
            ):
                neighbors.append(neighbor)
        return neighbors

    def a_star_recursive(current, open_list, closed_list, g_costs, f_costs, came_from):
        if not open_list:
            return None  # No path found

        # Select node in open_list with the smallest f_cost
        current = min(open_list, key=lambda node: f_costs[node])

        # If we've reached the goal, reconstruct and return the path
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]

        # Move current node from open_list to closed_list
        open_list.remove(current)
        closed_list.append(current)

        for neighbor in get_neighbors(current):
            if neighbor in closed_list:
                continue

            tentative_g_cost = (
                g_costs[current] + 1
            )  # Assume distance between adjacent nodes is 1

            if neighbor not in open_list:
                open_list.append(neighbor)
            elif tentative_g_cost >= g_costs[neighbor]:
                continue  # This is not a better path

            # This path is the best so far, record it
            came_from[neighbor] = current
            g_costs[neighbor] = tentative_g_cost
            f_costs[neighbor] = tentative_g_cost + heuristic(neighbor, goal)

        return a_star_recursive(
            current, open_list, closed_list, g_costs, f_costs, came_from
        )

    # Initialize all the lists and dictionaries
    open_list = [start]
    closed_list = []
    g_costs = {start: 0}
    f_costs = {start: heuristic(start, goal)}
    came_from = {}

    return a_star_recursive(start, open_list, closed_list, g_costs, f_costs, came_from)


def a_star_iterative(
    start, goal, positions, max_x, max_y, side=None, is_valid=None, get_cost=None
):
    def heuristic(a, b):
        # Using Manhattan distance as heuristic
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(node):
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for direction in directions:
            neighbor = (node[0] + direction[0], node[1] + direction[1])
            if (
                0 <= neighbor[0] <= max_x
                and 0 <= neighbor[1] <= max_y
                and neighbor in positions
                and is_valid(neighbor, side)
            ):
                neighbors.append(neighbor)
        return neighbors

    # Initialize all the lists and dictionaries
    open_list = []
    heapq.heappush(open_list, (0, start))
    came_from = {}
    g_costs = {start: 0}
    f_costs = {start: heuristic(start, goal)}

    while open_list:
        # Pop the node with the smallest f_cost
        _, current = heapq.heappop(open_list)

        # If we've reached the goal, reconstruct and return the path
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]

        for neighbor in get_neighbors(current):
            # Assume distance between adjacent nodes is 1
            tentative_g_cost = g_costs[current] + 1 + get_cost(neighbor)

            if neighbor not in g_costs or tentative_g_cost < g_costs[neighbor]:
                came_from[neighbor] = current
                g_costs[neighbor] = tentative_g_cost
                f_costs[neighbor] = tentative_g_cost + heuristic(neighbor, goal)
                heapq.heappush(open_list, (f_costs[neighbor], neighbor))

    return None  # No path found
