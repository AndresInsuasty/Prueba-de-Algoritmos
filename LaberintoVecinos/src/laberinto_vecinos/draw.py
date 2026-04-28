from __future__ import annotations

from dataclasses import dataclass

import pygame

from laberinto_vecinos.config import (
    COLOR_BTN,
    COLOR_BTN_ACTIVE,
    COLOR_BTN_BORDER,
    COLOR_BTN_DISABLED,
    COLOR_BTN_TEXT,
    COLOR_FLOOR,
    COLOR_FRONTIER_BFS,
    COLOR_FRONTIER_DFS,
    COLOR_GOAL,
    COLOR_HUD,
    COLOR_MUTED,
    COLOR_PATH,
    COLOR_START,
    COLOR_TEXT,
    COLOR_VISITED_BFS,
    COLOR_VISITED_DFS,
    COLOR_WALL,
    HUD_HEIGHT,
)
from laberinto_vecinos.models import SearchStep


def _font(px: int) -> pygame.font.Font:
    return pygame.font.Font(None, px)


@dataclass(slots=True)
class HudLayout:
    btn_toggle_run: pygame.Rect
    btn_reset_search: pygame.Rect
    btn_random_maze: pygame.Rect
    btn_clear_interior: pygame.Rect
    steps_minus: pygame.Rect
    steps_plus: pygame.Rect


def build_hud_layout(screen_w: int) -> HudLayout:
    h = 30
    y = 118
    x = 8
    btn_toggle_run = pygame.Rect(x, y, 118, h)
    x += 126
    btn_reset_search = pygame.Rect(x, y, 150, h)
    x += 158
    btn_random_maze = pygame.Rect(x, y, 160, h)
    x += 168
    btn_clear_interior = pygame.Rect(x, y, 150, h)
    x += 158
    steps_minus = pygame.Rect(min(x, screen_w - 100), y, 40, h)
    steps_plus = pygame.Rect(steps_minus.right + 56, y, 40, h)
    return HudLayout(
        btn_toggle_run=btn_toggle_run,
        btn_reset_search=btn_reset_search,
        btn_random_maze=btn_random_maze,
        btn_clear_interior=btn_clear_interior,
        steps_minus=steps_minus,
        steps_plus=steps_plus,
    )


def hit_test_hud(layout: HudLayout, pos: tuple[int, int]) -> str | None:
    if not (0 <= pos[1] < HUD_HEIGHT):
        return None
    pairs = [
        (layout.btn_toggle_run, "toggle_run"),
        (layout.btn_reset_search, "reset_search"),
        (layout.btn_random_maze, "random_maze"),
        (layout.btn_clear_interior, "clear_interior"),
        (layout.steps_minus, "steps_m"),
        (layout.steps_plus, "steps_p"),
    ]
    for r, name in pairs:
        if r.collidepoint(pos):
            return name
    return None


def _draw_button(
    surface: pygame.Surface,
    rect: pygame.Rect,
    text: str,
    font: pygame.font.Font,
    *,
    enabled: bool = True,
    selected: bool = False,
) -> None:
    bg = COLOR_BTN_DISABLED if not enabled else (COLOR_BTN_ACTIVE if selected else COLOR_BTN)
    pygame.draw.rect(surface, bg, rect, border_radius=4)
    pygame.draw.rect(surface, COLOR_BTN_BORDER, rect, 1, border_radius=4)
    col = COLOR_MUTED if not enabled else COLOR_BTN_TEXT
    surf = font.render(text, True, col)
    surface.blit(surf, (rect.centerx - surf.get_width() // 2, rect.centery - surf.get_height() // 2))


def draw_hud(
    surface: pygame.Surface,
    layout: HudLayout,
    *,
    editing: bool,
    sim_running: bool,
    steps_per_frame: int,
    gw: int,
    gh: int,
    visited_bfs: int,
    visited_dfs: int,
    done_bfs: bool,
    done_dfs: bool,
    ok_bfs: bool,
    ok_dfs: bool,
) -> None:
    hud = pygame.Rect(0, 0, surface.get_width(), HUD_HEIGHT)
    pygame.draw.rect(surface, COLOR_HUD, hud)
    f = _font(22)
    s = _font(18)
    btn = _font(19)

    st = "Editá el laberinto (clic / clic der.)" if editing else "Reproducción — BFS vs DFS"
    surface.blit(f.render(st, True, COLOR_TEXT), (10, 8))
    surface.blit(
        s.render(
            "BFS: camino más corto, suele “pintar” más celdas · DFS: menos memoria en la frontera, no garantiza el más corto",
            True,
            COLOR_MUTED,
        ),
        (10, 32),
    )
    stats = (
        f"Visitados (acum.) — BFS: {visited_bfs}  |  DFS: {visited_dfs}  ·  "
        f"BFS: {'meta ✓' if done_bfs and ok_bfs else '…' if not done_bfs else 'sin meta'}  "
        f"·  DFS: {'meta ✓' if done_dfs and ok_dfs else '…' if not done_dfs else 'sin meta'}"
    )
    surface.blit(s.render(stats, True, COLOR_MUTED), (10, 54))
    surface.blit(s.render(f"Grilla {gw}×{gh}  ·  SPACE play/pausa  ·  vel: {steps_per_frame} pasos/f", True, COLOR_MUTED), (10, 76))

    run_label = "Pausar" if sim_running else "Play"
    _draw_button(surface, layout.btn_toggle_run, run_label, btn, enabled=True)
    _draw_button(surface, layout.btn_reset_search, "Reiniciar búsqueda", btn, enabled=True)
    _draw_button(surface, layout.btn_random_maze, "Laberinto aleatorio", btn, enabled=editing and not sim_running)
    _draw_button(surface, layout.btn_clear_interior, "Vaciar interior", btn, enabled=editing and not sim_running)
    _draw_button(surface, layout.steps_minus, "−", btn, enabled=True)
    _draw_button(surface, layout.steps_plus, "+", btn, enabled=True)


def draw_panel(
    surface: pygame.Surface,
    origin_x: int,
    origin_y: int,
    cell: int,
    gw: int,
    gh: int,
    walls: list[list[bool]],
    start: tuple[int, int],
    goal: tuple[int, int],
    step: SearchStep | None,
    *,
    is_bfs: bool,
    title: str,
) -> None:
    title_font = _font(22)
    surface.blit(title_font.render(title, True, COLOR_TEXT), (origin_x, origin_y - 26))
    vcol = COLOR_VISITED_BFS if is_bfs else COLOR_VISITED_DFS
    fcol = COLOR_FRONTIER_BFS if is_bfs else COLOR_FRONTIER_DFS

    for x in range(gw):
        for y in range(gh):
            r = pygame.Rect(origin_x + x * cell, origin_y + y * cell, cell, cell)
            if walls[x][y]:
                pygame.draw.rect(surface, COLOR_WALL, r)
            else:
                pygame.draw.rect(surface, COLOR_FLOOR, r)

    if step is not None:
        for (cx, cy) in step.visited:
            if walls[cx][cy]:
                continue
            r = pygame.Rect(origin_x + cx * cell, origin_y + cy * cell, cell, cell)
            pygame.draw.rect(surface, vcol, r.inflate(-1, -1))
        for (cx, cy) in step.frontier:
            if walls[cx][cy]:
                continue
            r = pygame.Rect(origin_x + cx * cell, origin_y + cy * cell, cell, cell)
            pygame.draw.rect(surface, fcol, r.inflate(-2, -2))
        if step.current and not walls[step.current[0]][step.current[1]]:
            cx, cy = step.current
            r = pygame.Rect(origin_x + cx * cell, origin_y + cy * cell, cell, cell)
            pygame.draw.rect(surface, COLOR_PATH, r.inflate(-3, -3), 2)
        if step.done and step.path:
            for (cx, cy) in step.path:
                r = pygame.Rect(origin_x + cx * cell, origin_y + cy * cell, cell, cell)
                pygame.draw.rect(surface, COLOR_PATH, r.inflate(-max(1, cell // 5), -max(1, cell // 5)))

    sx, sy = start
    gx, gy = goal
    pygame.draw.rect(surface, COLOR_START, pygame.Rect(origin_x + sx * cell, origin_y + sy * cell, cell, cell).inflate(-2, -2))
    pygame.draw.rect(surface, COLOR_GOAL, pygame.Rect(origin_x + gx * cell, origin_y + gy * cell, cell, cell).inflate(-2, -2))
