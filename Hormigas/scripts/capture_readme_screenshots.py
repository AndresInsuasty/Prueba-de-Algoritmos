#!/usr/bin/env python3
"""Genera capturas PNG en docs/hormigas/ para el README del repositorio."""
from __future__ import annotations

import os
import random
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from hormigas.config import COLOR_BG, WINDOW_HEIGHT, WINDOW_WIDTH
from hormigas.draw import build_hud_layout, draw_hud, draw_world
from hormigas.main import _compute_grid_size, _nest_cells, _origin, _reset_sim
from hormigas.models import SimParams
from hormigas.world import World


def _blit_frame(
    screen: pygame.Surface,
    *,
    world: World,
    nest: set[tuple[int, int]],
    ants: list,
    gw: int,
    gh: int,
    origin_x: int,
    origin_y: int,
    params: SimParams,
    sim_running: bool,
    food_mode: bool,
    show_pheromone: bool,
) -> None:
    layout = build_hud_layout(screen.get_width())
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


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    repo_root = Path(__file__).resolve().parents[2]
    out_dir = repo_root / "docs" / "hormigas"
    out_dir.mkdir(parents=True, exist_ok=True)

    gw, gh = _compute_grid_size()
    origin_x, origin_y = _origin(gw, gh)
    nest: set[tuple[int, int]] = set()
    for gx, gy in _nest_cells():
        if 0 <= gx < gw and 0 <= gy < gh:
            nest.add((gx, gy))

    rng = random.Random(7)
    world = World(gw, gh)
    params = SimParams()
    params.clamp()
    ants = _reset_sim(rng, world, nest, params.ant_count)

    for x in range(22, 52):
        if world.in_bounds(x, 16):
            world.walls[x][16] = True
    for y in range(10, 26):
        if world.in_bounds(38, y):
            world.walls[38][y] = True

    _blit_frame(
        screen,
        world=world,
        nest=nest,
        ants=ants,
        gw=gw,
        gh=gh,
        origin_x=origin_x,
        origin_y=origin_y,
        params=params,
        sim_running=False,
        food_mode=False,
        show_pheromone=True,
    )
    pygame.image.save(screen, str(out_dir / "01-pausa-y-panel.png"))

    for _ in range(2500):
        world.evaporate(params.rho)
        for _s in range(params.steps_per_frame):
            for ant in ants:
                ant.step(world, nest, alpha=params.alpha, q_deposit=params.q_deposit)

    _blit_frame(
        screen,
        world=world,
        nest=nest,
        ants=ants,
        gw=gw,
        gh=gh,
        origin_x=origin_x,
        origin_y=origin_y,
        params=params,
        sim_running=True,
        food_mode=False,
        show_pheromone=True,
    )
    pygame.image.save(screen, str(out_dir / "02-simulacion-feromonas.png"))

    rng2 = random.Random(3)
    world2 = World(gw, gh)
    ants2 = _reset_sim(rng2, world2, nest, params.ant_count)
    for gx in range(15, 60, 4):
        for gy in range(24, 30):
            if world2.in_bounds(gx, gy) and (gx, gy) not in nest:
                world2.add_food(gx, gy, 2.5)
    for x in range(28, 45):
        if world2.in_bounds(x, 20):
            world2.walls[x][20] = True

    _blit_frame(
        screen,
        world=world2,
        nest=nest,
        ants=ants2,
        gw=gw,
        gh=gh,
        origin_x=origin_x,
        origin_y=origin_y,
        params=params,
        sim_running=False,
        food_mode=True,
        show_pheromone=False,
    )
    pygame.image.save(screen, str(out_dir / "03-muros-y-comida.png"))

    pygame.quit()
    print(f"Capturas guardadas en: {out_dir}")


if __name__ == "__main__":
    main()
