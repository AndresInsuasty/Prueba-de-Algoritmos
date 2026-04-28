from __future__ import annotations

from dataclasses import dataclass

import pygame

from hormigas.ants import Ant
from hormigas.config import (
    CELL,
    COLOR_ANT_RETURN,
    COLOR_ANT_SEARCH,
    COLOR_BTN,
    COLOR_BTN_ACTIVE,
    COLOR_BTN_BORDER,
    COLOR_BTN_DISABLED,
    COLOR_BTN_TEXT,
    COLOR_FLOOR,
    COLOR_FOOD,
    COLOR_FOOD_CORE,
    COLOR_HUD,
    COLOR_MUTED,
    COLOR_NEST,
    COLOR_PHERO,
    COLOR_TEXT,
    COLOR_WALL,
    HUD_HEIGHT,
)
from hormigas.models import SimParams
from hormigas.world import World


def _font(px: int) -> pygame.font.Font:
    return pygame.font.Font(None, px)


def cell_rect(origin_x: int, origin_y: int, gx: int, gy: int) -> pygame.Rect:
    return pygame.Rect(origin_x + gx * CELL, origin_y + gy * CELL, CELL, CELL)


@dataclass(slots=True)
class HudLayout:
    btn_toggle_run: pygame.Rect
    btn_reset: pygame.Rect
    btn_toggle_phero: pygame.Rect
    btn_clear_phero: pygame.Rect
    btn_mode_walls: pygame.Rect
    btn_mode_food: pygame.Rect
    rho_minus: pygame.Rect
    rho_plus: pygame.Rect
    alpha_minus: pygame.Rect
    alpha_plus: pygame.Rect
    q_minus: pygame.Rect
    q_plus: pygame.Rect
    steps_minus: pygame.Rect
    steps_plus: pygame.Rect
    ants_minus: pygame.Rect
    ants_plus: pygame.Rect


def build_hud_layout(screen_w: int) -> HudLayout:
    h = 30
    y1 = 62
    x = 8
    btn_toggle_run = pygame.Rect(x, y1, 108, h)
    x += 116
    btn_reset = pygame.Rect(x, y1, 100, h)
    x += 108
    btn_toggle_phero = pygame.Rect(x, y1, 138, h)
    x += 146
    btn_clear_phero = pygame.Rect(x, y1, 150, h)
    x += 158
    btn_mode_walls = pygame.Rect(x, y1, 88, h)
    x += 96
    btn_mode_food = pygame.Rect(x, y1, 88, h)

    bw, gap = 36, 6
    y2 = 124
    x = 8

    def pair() -> tuple[pygame.Rect, pygame.Rect]:
        nonlocal x
        m = pygame.Rect(x, y2, bw, h)
        x += bw + gap
        p = pygame.Rect(x, y2, bw, h)
        x += bw + 18
        return m, p

    rho_minus, rho_plus = pair()
    alpha_minus, alpha_plus = pair()
    q_minus, q_plus = pair()
    steps_minus, steps_plus = pair()
    ants_minus, ants_plus = pair()

    return HudLayout(
        btn_toggle_run=btn_toggle_run,
        btn_reset=btn_reset,
        btn_toggle_phero=btn_toggle_phero,
        btn_clear_phero=btn_clear_phero,
        btn_mode_walls=btn_mode_walls,
        btn_mode_food=btn_mode_food,
        rho_minus=rho_minus,
        rho_plus=rho_plus,
        alpha_minus=alpha_minus,
        alpha_plus=alpha_plus,
        q_minus=q_minus,
        q_plus=q_plus,
        steps_minus=steps_minus,
        steps_plus=steps_plus,
        ants_minus=ants_minus,
        ants_plus=ants_plus,
    )


def hit_test_hud(layout: HudLayout, pos: tuple[int, int]) -> str | None:
    if not (0 <= pos[1] < HUD_HEIGHT):
        return None
    checks: list[tuple[pygame.Rect, str]] = [
        (layout.btn_toggle_run, "toggle_run"),
        (layout.btn_reset, "reset"),
        (layout.btn_toggle_phero, "toggle_phero"),
        (layout.btn_clear_phero, "clear_phero"),
        (layout.btn_mode_walls, "mode_walls"),
        (layout.btn_mode_food, "mode_food"),
        (layout.rho_minus, "rho_m"),
        (layout.rho_plus, "rho_p"),
        (layout.alpha_minus, "alpha_m"),
        (layout.alpha_plus, "alpha_p"),
        (layout.q_minus, "q_m"),
        (layout.q_plus, "q_p"),
        (layout.steps_minus, "steps_m"),
        (layout.steps_plus, "steps_p"),
        (layout.ants_minus, "ants_m"),
        (layout.ants_plus, "ants_p"),
    ]
    for rect, name in checks:
        if rect.collidepoint(pos):
            return name
    return None


def _draw_button(
    surface: pygame.Surface,
    rect: pygame.Rect,
    text: str,
    font: pygame.font.Font,
    *,
    selected: bool = False,
    enabled: bool = True,
) -> None:
    bg = COLOR_BTN_DISABLED if not enabled else (COLOR_BTN_ACTIVE if selected else COLOR_BTN)
    pygame.draw.rect(surface, bg, rect, border_radius=4)
    pygame.draw.rect(surface, COLOR_BTN_BORDER, rect, 1, border_radius=4)
    col = COLOR_MUTED if not enabled else COLOR_BTN_TEXT
    surf = font.render(text, True, col)
    surface.blit(surf, (rect.centerx - surf.get_width() // 2, rect.centery - surf.get_height() // 2))


def draw_world(
    surface: pygame.Surface,
    world: World,
    origin_x: int,
    origin_y: int,
    nest_cells: set[tuple[int, int]],
    ants: list[Ant],
    *,
    show_pheromone: bool,
) -> None:
    for x in range(world.gw):
        for y in range(world.gh):
            r = cell_rect(origin_x, origin_y, x, y)
            if world.walls[x][y]:
                pygame.draw.rect(surface, COLOR_WALL, r)
            else:
                pygame.draw.rect(surface, COLOR_FLOOR, r)
                if show_pheromone:
                    ph = world.phero[x][y]
                    if ph > 0.04:
                        t = min(1.0, ph / 10.0)
                        c = (
                            int(40 + t * (COLOR_PHERO[0] - 40)),
                            int(50 + t * (COLOR_PHERO[1] - 50)),
                            int(60 + t * (COLOR_PHERO[2] - 60)),
                        )
                        inner = r.inflate(-2, -2)
                        pygame.draw.rect(surface, c, inner, border_radius=2)
                fd = world.food[x][y]
                if fd > 0.01:
                    cx, cy = r.center
                    rad = max(4, int(4 + min(fd, 12.0) * 1.2))
                    pygame.draw.circle(surface, COLOR_FOOD, (cx, cy), rad)
                    pygame.draw.circle(surface, COLOR_FOOD_CORE, (cx, cy), max(2, rad // 2))

    for gx, gy in nest_cells:
        r = cell_rect(origin_x, origin_y, gx, gy)
        pygame.draw.rect(surface, COLOR_NEST, r.inflate(-1, -1), border_radius=3)

    for ant in ants:
        r = cell_rect(origin_x, origin_y, ant.gx, ant.gy)
        c = COLOR_ANT_RETURN if ant.carrying else COLOR_ANT_SEARCH
        pygame.draw.circle(surface, c, r.center, max(3, CELL // 3))


def draw_hud(
    surface: pygame.Surface,
    layout: HudLayout,
    *,
    sim_running: bool,
    food_mode: bool,
    show_pheromone: bool,
    grid_w: int,
    grid_h: int,
    params: SimParams,
) -> None:
    hud = pygame.Rect(0, 0, surface.get_width(), HUD_HEIGHT)
    pygame.draw.rect(surface, COLOR_HUD, hud)
    f = _font(22)
    s = _font(18)
    btn_f = _font(19)
    tiny = _font(16)

    status = "Simulación en marcha" if sim_running else "Pausada — ajustá parámetros y pulsá Iniciar"
    surface.blit(f.render(status, True, COLOR_TEXT), (10, 6))
    surface.blit(
        s.render("Ratón: muros (arrastrar) o comida según modo · Teclas: M P C G ESC", True, COLOR_MUTED),
        (10, 30),
    )
    surface.blit(
        s.render(f"Grilla {grid_w}×{grid_h}  ·  SPACE = pausar / reanudar", True, COLOR_MUTED),
        (10, 50),
    )

    run_label = "Pausar" if sim_running else "Iniciar"
    _draw_button(surface, layout.btn_toggle_run, run_label, btn_f, enabled=True)
    _draw_button(surface, layout.btn_reset, "Reiniciar", btn_f, enabled=True)
    _draw_button(
        surface,
        layout.btn_toggle_phero,
        "Ferom. " + ("on" if show_pheromone else "off"),
        btn_f,
        selected=show_pheromone,
        enabled=True,
    )
    _draw_button(surface, layout.btn_clear_phero, "Limpiar ferom.", btn_f, enabled=True)
    _draw_button(surface, layout.btn_mode_walls, "Muros", btn_f, selected=not food_mode, enabled=True)
    _draw_button(surface, layout.btn_mode_food, "Comida", btn_f, selected=food_mode, enabled=True)

    _draw_button(surface, layout.rho_minus, "−", btn_f, enabled=not sim_running)
    _draw_button(surface, layout.rho_plus, "+", btn_f, enabled=not sim_running)
    _draw_button(surface, layout.alpha_minus, "−", btn_f, enabled=not sim_running)
    _draw_button(surface, layout.alpha_plus, "+", btn_f, enabled=not sim_running)
    _draw_button(surface, layout.q_minus, "−", btn_f, enabled=not sim_running)
    _draw_button(surface, layout.q_plus, "+", btn_f, enabled=not sim_running)
    _draw_button(surface, layout.steps_minus, "−", btn_f, enabled=True)
    _draw_button(surface, layout.steps_plus, "+", btn_f, enabled=True)
    _draw_button(surface, layout.ants_minus, "−", btn_f, enabled=not sim_running)
    _draw_button(surface, layout.ants_plus, "+", btn_f, enabled=not sim_running)

    metrics = (
        f"ρ={params.rho:.3f}   α={params.alpha:.2f}   Q={params.q_deposit:.2f}   "
        f"vel={params.steps_per_frame} pasos/f   hormigas={params.ant_count}"
    )
    surf_m = tiny.render(metrics, True, COLOR_MUTED)
    surface.blit(surf_m, (10, 96))
