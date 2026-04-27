from __future__ import annotations

import pygame

from sorting_race.config import (
    COLOR_BAR,
    COLOR_BET_SELECTED,
    COLOR_HIGHLIGHT,
    COLOR_HUD_BG,
    COLOR_LOSE,
    COLOR_MUTED,
    COLOR_PIVOT,
    COLOR_QUADRANT_BORDER,
    COLOR_TEXT,
    COLOR_WIN,
    HUD_HEIGHT,
)
from sorting_race.models import GamePhase, SortStep


def _font(size: int) -> pygame.font.Font:
    return pygame.font.Font(None, size)


def draw_hud(
    surface: pygame.Surface,
    *,
    phase: GamePhase,
    n: int,
    steps: int,
    seed: int | None,
    bet_index: int | None,
    names: list[str],
    finish_order: list[int] | None,
    bet_won: bool | None,
) -> None:
    hud = pygame.Rect(0, 0, surface.get_width(), HUD_HEIGHT)
    pygame.draw.rect(surface, COLOR_HUD_BG, hud)
    font = _font(20)
    small = _font(16)

    lines = [
        "SPACE iniciar carrera · R nueva permutación · 1-4 apuesta · Clic en cuadrante",
        f"n={n}   pasos/frame={steps}   [ / ] tamaño   + / - velocidad   ESC salir",
    ]
    if seed is not None:
        lines[1] += f"   semilla={seed}"

    y = 8
    for line in lines:
        surface.blit(small.render(line, True, COLOR_MUTED), (12, y))
        y += 22

    if phase == GamePhase.BETTING:
        if bet_index is not None:
            msg = f"Apuesta: {names[bet_index]}"
        else:
            msg = "Apuesta: (elegí con 1-4 o clic; opcional)"
        surface.blit(font.render(msg, True, COLOR_TEXT), (12, 56))
    elif phase == GamePhase.RACING:
        surface.blit(font.render("Carrera en curso…", True, COLOR_TEXT), (12, 56))
    elif phase == GamePhase.RESULT and finish_order is not None:
        first = names[finish_order[0]]
        result = f"Ganador: {first}"
        if bet_index is not None:
            result += " — ¡Acertaste!" if bet_won else " — No acertaste la apuesta."
        else:
            result += " — (sin apuesta)"
        if bet_index is None:
            color = COLOR_TEXT
        elif bet_won:
            color = COLOR_WIN
        else:
            color = COLOR_LOSE
        surface.blit(font.render(result, True, color), (12, 56))


def draw_quadrant(
    surface: pygame.Surface,
    rect: pygame.Rect,
    *,
    title: str,
    arr: list[int],
    step: SortStep | None,
    phase: GamePhase,
    quad_index: int,
    bet_index: int | None,
    finish_rank: int | None,
    winner_index: int | None,
) -> None:
    pygame.draw.rect(surface, COLOR_QUADRANT_BORDER, rect, 1)
    inner = rect.inflate(-8, -8)
    title_font = _font(22)
    surface.blit(title_font.render(title, True, COLOR_TEXT), (inner.x + 4, inner.y + 2))

    chart = pygame.Rect(inner.x, inner.y + 30, inner.width, inner.height - 36)
    if not arr:
        return

    max_v = max(arr)
    if max_v <= 0:
        max_v = 1
    n = len(arr)
    bar_w = max(1, chart.w // n)
    gap = 1
    usable_h = chart.h - 4

    hi_idx: set[int] = set()
    if step:
        if step.i is not None:
            hi_idx.add(step.i)
        if step.j is not None:
            hi_idx.add(step.j)

    for idx, val in enumerate(arr):
        h = int(val / max_v * usable_h)
        x = chart.x + idx * bar_w + gap // 2
        w = bar_w - gap
        y = chart.bottom - h
        rect_bar = pygame.Rect(x, y, w, h)
        if step and step.pivot is not None and idx == step.pivot:
            color = COLOR_PIVOT
        elif idx in hi_idx:
            color = COLOR_HIGHLIGHT
        else:
            color = COLOR_BAR
        pygame.draw.rect(surface, color, rect_bar)

    if phase == GamePhase.BETTING and bet_index == quad_index:
        pygame.draw.rect(surface, COLOR_BET_SELECTED, rect, 3)

    if phase == GamePhase.RESULT and finish_rank is not None:
        rank_font = _font(26)
        label = f"{finish_rank}º"
        if winner_index == quad_index:
            label += " — ganó"
        surf = rank_font.render(label, True, COLOR_WIN if winner_index == quad_index else COLOR_MUTED)
        surface.blit(surf, (inner.right - surf.get_width() - 6, inner.y + 4))
