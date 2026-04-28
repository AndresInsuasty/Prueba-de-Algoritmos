from __future__ import annotations

import argparse
import random
import sys

import pygame

from hormigas.ants import spawn_ant_in_nest
from hormigas.config import (
    ANT_COUNT,
    CELL,
    DEFAULT_GRID_H,
    DEFAULT_GRID_W,
    FOOD_PER_CLICK,
    HUD_HEIGHT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    COLOR_BG,
    NEST_RADIUS,
)
from hormigas.draw import build_hud_layout, draw_hud, draw_world, hit_test_hud
from hormigas.models import SimParams
from hormigas.world import World


def _nest_cells() -> list[tuple[int, int]]:
    cx, cy = 4, 4
    r = NEST_RADIUS
    out: list[tuple[int, int]] = []
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if max(abs(dx), abs(dy)) <= r:
                out.append((cx + dx, cy + dy))
    return out


def _compute_grid_size() -> tuple[int, int]:
    avail_w = WINDOW_WIDTH - 24
    avail_h = WINDOW_HEIGHT - HUD_HEIGHT - 16
    gw = max(24, min(DEFAULT_GRID_W, avail_w // CELL))
    gh = max(16, min(DEFAULT_GRID_H, avail_h // CELL))
    return gw, gh


def _origin(gw: int, gh: int) -> tuple[int, int]:
    grid_px_w = gw * CELL
    grid_px_h = gh * CELL
    ox = (WINDOW_WIDTH - grid_px_w) // 2
    oy = HUD_HEIGHT + 8
    return ox, oy


def _screen_to_cell(
    pos: tuple[int, int],
    origin_x: int,
    origin_y: int,
    gw: int,
    gh: int,
) -> tuple[int, int] | None:
    mx, my = pos
    gx = (mx - origin_x) // CELL
    gy = (my - origin_y) // CELL
    if 0 <= gx < gw and 0 <= gy < gh:
        return gx, gy
    return None


def _clear_nest_walls(world: World, nest: set[tuple[int, int]]) -> None:
    for gx, gy in nest:
        if world.in_bounds(gx, gy):
            world.walls[gx][gy] = False


def _scatter_food(world: World, rng: random.Random, nest: set[tuple[int, int]], blobs: int) -> None:
    margin = 4
    for _ in range(blobs):
        for _ in range(80):
            gx = rng.randint(margin, world.gw - margin - 1)
            gy = rng.randint(margin, world.gh - margin - 1)
            if (gx, gy) in nest or world.walls[gx][gy]:
                continue
            world.add_food(gx, gy, rng.uniform(3.0, 7.0))
            break


def _reset_sim(
    rng: random.Random,
    world: World,
    nest: set[tuple[int, int]],
    ant_count: int,
) -> list:
    nest_list = list(nest)
    for x in range(world.gw):
        for y in range(world.gh):
            world.walls[x][y] = False
            world.phero[x][y] = 0.0
            world.food[x][y] = 0.0
    _clear_nest_walls(world, nest)
    _scatter_food(world, rng, nest, blobs=6)
    return [spawn_ant_in_nest(rng, nest_list) for _ in range(ant_count)]


def _respawn_ants(rng: random.Random, nest_list: list[tuple[int, int]], ant_count: int) -> list:
    return [spawn_ant_in_nest(rng, nest_list) for _ in range(ant_count)]


def _apply_hud_action(
    hit: str,
    *,
    sim_running: bool,
    params: SimParams,
    rng: random.Random,
    world: World,
    nest: set[tuple[int, int]],
    nest_list: list[tuple[int, int]],
    ants: list,
) -> tuple[bool, list]:
    """Devuelve (nuevo_sim_running, lista de hormigas)."""
    ants_out = ants
    run = sim_running

    if hit == "toggle_run":
        run = not run
    elif hit == "reset":
        run = False
        params.clamp()
        ants_out = _reset_sim(rng, world, nest, params.ant_count)
    elif hit == "steps_m":
        params.steps_per_frame -= 1
    elif hit == "steps_p":
        params.steps_per_frame += 1
    elif not run:
        if hit == "rho_m":
            params.rho -= 0.002
        elif hit == "rho_p":
            params.rho += 0.002
        elif hit == "alpha_m":
            params.alpha -= 0.05
        elif hit == "alpha_p":
            params.alpha += 0.05
        elif hit == "q_m":
            params.q_deposit -= 0.1
        elif hit == "q_p":
            params.q_deposit += 0.1
        elif hit == "ants_m":
            params.ant_count -= 4
            params.clamp()
            ants_out = _respawn_ants(rng, nest_list, params.ant_count)
        elif hit == "ants_p":
            params.ant_count += 4
            params.clamp()
            ants_out = _respawn_ants(rng, nest_list, params.ant_count)

    params.clamp()
    return run, ants_out


def main() -> None:
    parser = argparse.ArgumentParser(description="Hormigas — colonia, feromonas y comida (Pygame).")
    parser.add_argument("--ants", type=int, default=ANT_COUNT, help="Cantidad inicial de hormigas")
    parser.add_argument("--seed", type=int, default=None, help="Semilla del generador aleatorio")
    args = parser.parse_args()

    gw, gh = _compute_grid_size()
    origin_x, origin_y = _origin(gw, gh)
    nest_list_raw = _nest_cells()
    nest: set[tuple[int, int]] = set()
    for gx, gy in nest_list_raw:
        if 0 <= gx < gw and 0 <= gy < gh:
            nest.add((gx, gy))
    nest_list = list(nest)

    rng = random.Random(args.seed)
    world = World(gw, gh)
    params = SimParams()
    params.ant_count = max(4, min(200, int(args.ants)))
    params.clamp()
    sim_running = False
    ants = _reset_sim(rng, world, nest, params.ant_count)

    pygame.init()
    pygame.display.set_caption("Hormigas — feromonas y comida")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    food_mode = False
    show_pheromone = True
    last_cell: tuple[int, int] | None = None
    brush_left = False
    brush_right = False

    app_running = True
    while app_running:
        layout = build_hud_layout(screen.get_width())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    app_running = False
                elif event.key == pygame.K_SPACE:
                    sim_running = not sim_running
                elif event.key == pygame.K_m:
                    food_mode = not food_mode
                elif event.key == pygame.K_p:
                    show_pheromone = not show_pheromone
                elif event.key == pygame.K_c:
                    world.clear_pheromones()
                elif event.key == pygame.K_g:
                    _scatter_food(world, rng, nest, blobs=4)
                elif event.key == pygame.K_r:
                    sim_running = False
                    params.clamp()
                    ants = _reset_sim(rng, world, nest, params.ant_count)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                hud_hit = hit_test_hud(layout, event.pos)
                if hud_hit is not None:
                    if hud_hit == "toggle_phero":
                        show_pheromone = not show_pheromone
                    elif hud_hit == "clear_phero":
                        world.clear_pheromones()
                    elif hud_hit == "mode_walls":
                        food_mode = False
                    elif hud_hit == "mode_food":
                        food_mode = True
                    else:
                        sim_running, ants = _apply_hud_action(
                            hud_hit,
                            sim_running=sim_running,
                            params=params,
                            rng=rng,
                            world=world,
                            nest=nest,
                            nest_list=nest_list,
                            ants=ants,
                        )
                elif event.pos[1] >= HUD_HEIGHT:
                    if event.button == 1 and food_mode:
                        cell = _screen_to_cell(event.pos, origin_x, origin_y, gw, gh)
                        if cell is not None and cell not in nest:
                            world.add_food(cell[0], cell[1], FOOD_PER_CLICK)
                    elif event.button == 1 and not food_mode:
                        brush_left = True
                        last_cell = _screen_to_cell(event.pos, origin_x, origin_y, gw, gh)
                    elif event.button == 3:
                        brush_right = True
                        last_cell = _screen_to_cell(event.pos, origin_x, origin_y, gw, gh)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    brush_left = False
                    last_cell = None
                elif event.button == 3:
                    brush_right = False
                    last_cell = None
            elif event.type == pygame.MOUSEMOTION:
                if brush_left and not food_mode:
                    cur = _screen_to_cell(event.pos, origin_x, origin_y, gw, gh)
                    if cur is not None and last_cell is not None:
                        world.set_wall_line(last_cell[0], last_cell[1], cur[0], cur[1], True)
                        for ncx, ncy in nest:
                            world.walls[ncx][ncy] = False
                    if cur is not None:
                        last_cell = cur
                elif brush_right:
                    cur = _screen_to_cell(event.pos, origin_x, origin_y, gw, gh)
                    if cur is not None and last_cell is not None:
                        world.set_wall_line(last_cell[0], last_cell[1], cur[0], cur[1], False)
                    if cur is not None:
                        last_cell = cur

        if sim_running:
            world.evaporate(params.rho)
            for _ in range(params.steps_per_frame):
                for ant in ants:
                    ant.step(world, nest, alpha=params.alpha, q_deposit=params.q_deposit)

        screen.fill(COLOR_BG)
        draw_hud(
            screen,
            layout,
            sim_running=sim_running,
            food_mode=food_mode,
            show_pheromone=show_pheromone,
            grid_w=gw,
            grid_h=gh,
            params=params,
        )
        draw_world(
            screen,
            world,
            origin_x,
            origin_y,
            nest,
            ants,
            show_pheromone=show_pheromone,
        )

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
