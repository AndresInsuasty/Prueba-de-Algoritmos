#!/usr/bin/env python3
"""Genera capturas en docs/laberinto_vecinos/ para el README raíz."""
from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from laberinto_vecinos.config import COLOR_BG, DEFAULT_GH, DEFAULT_GW, HUD_HEIGHT, PANEL_GAP, WINDOW_WIDTH
from laberinto_vecinos.draw import build_hud_layout, draw_hud, draw_panel
from laberinto_vecinos.maze import empty_walls, ensure_start_goal_open, generate_maze_recursive_backtracker
from laberinto_vecinos.search import bfs_gen, dfs_gen


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    repo = Path(__file__).resolve().parents[2]
    out = repo / "docs" / "laberinto_vecinos"
    out.mkdir(parents=True, exist_ok=True)

    gw, gh = DEFAULT_GW, DEFAULT_GH
    rng = random.Random(11)
    walls = empty_walls(gw, gh)
    generate_maze_recursive_backtracker(walls, gw, gh, rng)
    start, goal = (1, 1), (gw - 2, gh - 2)
    ensure_start_goal_open(walls, start, goal)

    from laberinto_vecinos.config import CELL

    panel_target_w = (WINDOW_WIDTH - 24 - PANEL_GAP) // 2
    cell = max(6, min(CELL, panel_target_w // gw, (720 - HUD_HEIGHT - 40) // gh))
    panel_w = gw * cell
    total_w = 2 * panel_w + PANEL_GAP
    ox_left = (WINDOW_WIDTH - total_w) // 2
    ox_right = ox_left + panel_w + PANEL_GAP
    oy = HUD_HEIGHT + 36

    layout = build_hud_layout(WINDOW_WIDTH)

    def shot(sim_running: bool, editing: bool, lb, ld, vb: int, vd: int, name: str) -> None:
        screen.fill(COLOR_BG)
        draw_hud(
            screen,
            layout,
            editing=editing,
            sim_running=sim_running,
            steps_per_frame=2,
            gw=gw,
            gh=gh,
            visited_bfs=vb,
            visited_dfs=vd,
            done_bfs=lb.done if lb else False,
            done_dfs=ld.done if ld else False,
            ok_bfs=lb.success if lb else False,
            ok_dfs=ld.success if ld else False,
        )
        draw_panel(screen, ox_left, oy, cell, gw, gh, walls, start, goal, lb, is_bfs=True, title="BFS (anchura)")
        draw_panel(screen, ox_right, oy, cell, gw, gh, walls, start, goal, ld, is_bfs=False, title="DFS (profundidad)")
        pygame.image.save(screen, str(out / name))

    gb = bfs_gen(walls, start, goal, gw, gh)
    gd = dfs_gen(walls, start, goal, gw, gh)
    lb = next(gb)
    ld = next(gd)
    shot(False, True, lb, ld, len(lb.visited), len(ld.visited), "01-edicion.png")

    for _ in range(8000):
        if not lb.done:
            lb = next(gb)
        if not ld.done:
            ld = next(gd)
        if lb.done and ld.done:
            break
    shot(True, False, lb, ld, len(lb.visited), len(ld.visited), "02-en-carrera.png")

    shot(False, False, lb, ld, len(lb.visited), len(ld.visited), "03-resultado.png")

    pygame.quit()
    print(f"Capturas en: {out}")


if __name__ == "__main__":
    main()
