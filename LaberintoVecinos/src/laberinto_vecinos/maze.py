from __future__ import annotations

import random


def empty_walls(gw: int, gh: int) -> list[list[bool]]:
    """Solo borde perimetral como muro; interior libre."""
    w = [[False] * gh for _ in range(gw)]
    for x in range(gw):
        w[x][0] = True
        w[x][gh - 1] = True
    for y in range(gh):
        w[0][y] = True
        w[gw - 1][y] = True
    return w


def generate_maze_recursive_backtracker(walls: list[list[bool]], gw: int, gh: int, rng: random.Random) -> None:
    """Rellena interior con muros y talla pasillos (gw, gh impares recomendado)."""
    for x in range(gw):
        for y in range(gh):
            walls[x][y] = True
    stack: list[tuple[int, int]] = [(1, 1)]
    walls[1][1] = False
    while stack:
        cx, cy = stack[-1]
        choices: list[tuple[int, int, int, int]] = []
        for dx, dy in ((0, 2), (0, -2), (2, 0), (-2, 0)):
            nx, ny = cx + dx, cy + dy
            if 1 <= nx < gw - 1 and 1 <= ny < gh - 1 and walls[nx][ny]:
                wx, wy = cx + dx // 2, cy + dy // 2
                choices.append((nx, ny, wx, wy))
        if choices:
            nx, ny, wx, wy = rng.choice(choices)
            walls[nx][ny] = False
            walls[wx][wy] = False
            stack.append((nx, ny))
        else:
            stack.pop()


def clear_interior_walls(walls: list[list[bool]], gw: int, gh: int) -> None:
    for x in range(1, gw - 1):
        for y in range(1, gh - 1):
            walls[x][y] = False


def ensure_start_goal_open(walls: list[list[bool]], start: tuple[int, int], goal: tuple[int, int]) -> None:
    sx, sy = start
    gx, gy = goal
    walls[sx][sy] = False
    walls[gx][gy] = False
