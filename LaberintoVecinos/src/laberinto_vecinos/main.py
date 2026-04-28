from __future__ import annotations

import argparse
import random
import sys
from collections.abc import Iterator

import pygame

from laberinto_vecinos.config import (
    CELL,
    DEFAULT_GH,
    DEFAULT_GW,
    DEFAULT_STEPS_PER_FRAME,
    HUD_HEIGHT,
    PANEL_GAP,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    COLOR_BG,
)
from laberinto_vecinos.draw import build_hud_layout, draw_hud, draw_panel, hit_test_hud
from laberinto_vecinos.maze import (
    clear_interior_walls,
    empty_walls,
    ensure_start_goal_open,
    generate_maze_recursive_backtracker,
)
from laberinto_vecinos.search import bfs_gen, dfs_gen


def main() -> None:
    parser = argparse.ArgumentParser(description="Laberinto: BFS vs DFS (Pygame).")
    parser.add_argument("--seed", type=int, default=None, help="Semilla del laberinto aleatorio")
    args = parser.parse_args()

    gw, gh = DEFAULT_GW, DEFAULT_GH
    rng = random.Random(args.seed)
    walls = empty_walls(gw, gh)
    generate_maze_recursive_backtracker(walls, gw, gh, rng)
    start = (1, 1)
    goal = (gw - 2, gh - 2)
    ensure_start_goal_open(walls, start, goal)

    panel_target_w = (WINDOW_WIDTH - 24 - PANEL_GAP) // 2
    cell = max(6, min(CELL, panel_target_w // gw, (WINDOW_HEIGHT - HUD_HEIGHT - 40) // gh))
    panel_w = gw * cell
    total_w = 2 * panel_w + PANEL_GAP
    ox_left = (WINDOW_WIDTH - total_w) // 2
    ox_right = ox_left + panel_w + PANEL_GAP
    oy = HUD_HEIGHT + 36

    gen_bfs: Iterator[SearchStep] | None = None
    gen_dfs: Iterator[SearchStep] | None = None
    last_bfs: SearchStep | None = None
    last_dfs: SearchStep | None = None
    visited_max_bfs = 0
    visited_max_dfs = 0
    sim_running = False
    steps_per_frame = DEFAULT_STEPS_PER_FRAME

    pygame.init()
    pygame.display.set_caption("Laberinto de los vecinos — BFS vs DFS")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    def _start_generators() -> None:
        nonlocal gen_bfs, gen_dfs, last_bfs, last_dfs, visited_max_bfs, visited_max_dfs
        gen_bfs = bfs_gen(walls, start, goal, gw, gh)
        gen_dfs = dfs_gen(walls, start, goal, gw, gh)
        last_bfs = next(gen_bfs)
        last_dfs = next(gen_dfs)
        visited_max_bfs = len(last_bfs.visited)
        visited_max_dfs = len(last_dfs.visited)

    def _reset_search_only() -> None:
        nonlocal gen_bfs, gen_dfs, last_bfs, last_dfs, visited_max_bfs, visited_max_dfs, sim_running
        sim_running = False
        gen_bfs = gen_dfs = None
        last_bfs = last_dfs = None
        visited_max_bfs = visited_max_dfs = 0

    app_running = True
    while app_running:
        editing = not sim_running and gen_bfs is None
        layout = build_hud_layout(screen.get_width())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    app_running = False
                elif event.key == pygame.K_SPACE:
                    if gen_bfs is None:
                        _start_generators()
                    sim_running = not sim_running
                elif event.key == pygame.K_r and editing:
                    walls[:] = empty_walls(gw, gh)
                    generate_maze_recursive_backtracker(walls, gw, gh, rng)
                    ensure_start_goal_open(walls, start, goal)
                    _reset_search_only()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                hit = hit_test_hud(layout, event.pos)
                if hit == "toggle_run":
                    if gen_bfs is None:
                        _start_generators()
                    sim_running = not sim_running
                elif hit == "reset_search":
                    _reset_search_only()
                elif hit == "random_maze" and editing:
                    walls[:] = empty_walls(gw, gh)
                    generate_maze_recursive_backtracker(walls, gw, gh, rng)
                    ensure_start_goal_open(walls, start, goal)
                    _reset_search_only()
                elif hit == "clear_interior" and editing:
                    clear_interior_walls(walls, gw, gh)
                    ensure_start_goal_open(walls, start, goal)
                    _reset_search_only()
                elif hit == "steps_m":
                    steps_per_frame = max(1, steps_per_frame - 1)
                elif hit == "steps_p":
                    steps_per_frame = min(32, steps_per_frame + 1)
                elif editing and event.pos[1] >= HUD_HEIGHT:
                    cell_hit = _screen_to_grid(event.pos, ox_left, oy, cell, gw, gh, ox_right)
                    if cell_hit is not None:
                        gx, gy = cell_hit
                        if (gx, gy) != start and (gx, gy) != goal and 0 < gx < gw - 1 and 0 < gy < gh - 1:
                            if event.button == 1:
                                walls[gx][gy] = True
                            elif event.button == 3:
                                walls[gx][gy] = False
                            _reset_search_only()

        if sim_running and (gen_bfs is not None or gen_dfs is not None):
            for _ in range(steps_per_frame):
                if gen_bfs is not None and last_bfs is not None and not last_bfs.done:
                    try:
                        last_bfs = next(gen_bfs)
                        visited_max_bfs = max(visited_max_bfs, len(last_bfs.visited))
                        if last_bfs.done:
                            gen_bfs = None
                    except StopIteration:
                        gen_bfs = None
                if gen_dfs is not None and last_dfs is not None and not last_dfs.done:
                    try:
                        last_dfs = next(gen_dfs)
                        visited_max_dfs = max(visited_max_dfs, len(last_dfs.visited))
                        if last_dfs.done:
                            gen_dfs = None
                    except StopIteration:
                        gen_dfs = None
                if gen_bfs is None and gen_dfs is None:
                    sim_running = False
                    break

        screen.fill(COLOR_BG)
        done_bfs = last_bfs.done if last_bfs else False
        done_dfs = last_dfs.done if last_dfs else False
        ok_bfs = last_bfs.success if last_bfs else False
        ok_dfs = last_dfs.success if last_dfs else False
        draw_hud(
            screen,
            layout,
            editing=editing,
            sim_running=sim_running,
            steps_per_frame=steps_per_frame,
            gw=gw,
            gh=gh,
            visited_bfs=visited_max_bfs,
            visited_dfs=visited_max_dfs,
            done_bfs=done_bfs,
            done_dfs=done_dfs,
            ok_bfs=ok_bfs,
            ok_dfs=ok_dfs,
        )
        draw_panel(
            screen,
            ox_left,
            oy,
            cell,
            gw,
            gh,
            walls,
            start,
            goal,
            last_bfs,
            is_bfs=True,
            title="BFS (anchura)",
        )
        draw_panel(
            screen,
            ox_right,
            oy,
            cell,
            gw,
            gh,
            walls,
            start,
            goal,
            last_dfs,
            is_bfs=False,
            title="DFS (profundidad)",
        )

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit(0)


def _screen_to_grid(
    pos: tuple[int, int],
    ox_left: int,
    oy: int,
    cell: int,
    gw: int,
    gh: int,
    ox_right: int,
) -> tuple[int, int] | None:
    mx, my = pos
    for ox in (ox_left, ox_right):
        if ox <= mx < ox + gw * cell and oy <= my < oy + gh * cell:
            gx = (mx - ox) // cell
            gy = (my - oy) // cell
            if 0 <= gx < gw and 0 <= gy < gh:
                return gx, gy
    return None


if __name__ == "__main__":
    main()
