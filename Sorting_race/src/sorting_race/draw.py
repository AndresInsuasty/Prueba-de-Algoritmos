from __future__ import annotations

from dataclasses import dataclass

import pygame

from sorting_race.config import (
    COLOR_BAR,
    COLOR_BET_SELECTED,
    COLOR_BTN,
    COLOR_BTN_ACTIVE,
    COLOR_BTN_BORDER,
    COLOR_BTN_DISABLED,
    COLOR_BTN_TEXT,
    COLOR_HIGHLIGHT,
    COLOR_HUD_BG,
    COLOR_LOSE,
    COLOR_MUTED,
    COLOR_PIVOT,
    COLOR_QUADRANT_BORDER,
    COLOR_TEXT,
    COLOR_WIN,
    HUD_HEIGHT,
    N_PRESETS,
)
from sorting_race.models import GamePhase, SortStep


def _font(size: int) -> pygame.font.Font:
    return pygame.font.Font(None, size)


@dataclass(slots=True)
class HudLayout:
    """Rectángulos clicables del panel superior (misma geometría que `draw_hud`)."""

    n_buttons: list[tuple[pygame.Rect, int]]
    steps_minus: pygame.Rect
    steps_plus: pygame.Rect
    btn_shuffle: pygame.Rect
    btn_primary: pygame.Rect


def build_hud_layout(screen_w: int) -> HudLayout:
    row_y = HUD_HEIGHT - 44
    btn_h = 34
    x = 8
    n_buttons: list[tuple[pygame.Rect, int]] = []
    btn_w = max(40, min(56, (screen_w - 520) // max(5, len(N_PRESETS))))
    for n in N_PRESETS:
        n_buttons.append((pygame.Rect(x, row_y, btn_w, btn_h), n))
        x += btn_w + 4

    x_vel = min(x + 10, screen_w - 300)
    steps_minus = pygame.Rect(x_vel, row_y, 40, btn_h)
    label_slot = 96
    steps_plus = pygame.Rect(steps_minus.right + 6 + label_slot + 6, row_y, 40, btn_h)

    btn_shuffle = pygame.Rect(screen_w - 270, row_y, 120, btn_h)
    btn_primary = pygame.Rect(screen_w - 142, row_y, 130, btn_h)

    return HudLayout(
        n_buttons=n_buttons,
        steps_minus=steps_minus,
        steps_plus=steps_plus,
        btn_shuffle=btn_shuffle,
        btn_primary=btn_primary,
    )


def hit_test_hud(layout: HudLayout, pos: tuple[int, int]) -> str | None:
    if not (0 <= pos[1] < HUD_HEIGHT):
        return None
    for rect, n in layout.n_buttons:
        if rect.collidepoint(pos):
            return f"n:{n}"
    if layout.steps_minus.collidepoint(pos):
        return "steps_minus"
    if layout.steps_plus.collidepoint(pos):
        return "steps_plus"
    if layout.btn_shuffle.collidepoint(pos):
        return "shuffle"
    if layout.btn_primary.collidepoint(pos):
        return "primary"
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
    if not enabled:
        bg = COLOR_BTN_DISABLED
    elif selected:
        bg = COLOR_BTN_ACTIVE
    else:
        bg = COLOR_BTN
    pygame.draw.rect(surface, bg, rect, border_radius=4)
    pygame.draw.rect(surface, COLOR_BTN_BORDER, rect, 1, border_radius=4)
    label = font.render(text, True, COLOR_BTN_TEXT if enabled else COLOR_MUTED)
    surface.blit(
        label,
        (
            rect.centerx - label.get_width() // 2,
            rect.centery - label.get_height() // 2,
        ),
    )


def draw_hud(
    surface: pygame.Surface,
    layout: HudLayout,
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
    small = _font(16)
    font = _font(20)
    btn_font = _font(19)

    racing = phase == GamePhase.RACING
    surface.blit(
        small.render(
            "Clic en la barra: cantidad de elementos, velocidad (−/+), Nueva, Iniciar u Otra carrera.",
            True,
            COLOR_MUTED,
        ),
        (12, 6),
    )
    seed_txt = f"   semilla={seed}" if seed is not None else ""
    surface.blit(
        small.render(
            f"También podés usar teclado: [ ] tamaño · + / - velocidad{seed_txt}",
            True,
            COLOR_MUTED,
        ),
        (12, 24),
    )

    for rect, nv in layout.n_buttons:
        _draw_button(
            surface,
            rect,
            str(nv),
            btn_font,
            selected=(n == nv),
            enabled=not racing,
        )

    _draw_button(surface, layout.steps_minus, "−", btn_font, enabled=True)
    mid = (layout.steps_minus.right + layout.steps_plus.left) // 2
    steps_label = btn_font.render(str(steps), True, COLOR_TEXT)
    surface.blit(
        steps_label,
        (
            mid - steps_label.get_width() // 2,
            layout.steps_minus.centery - steps_label.get_height() // 2,
        ),
    )
    _draw_button(surface, layout.steps_plus, "+", btn_font, enabled=True)

    _draw_button(surface, layout.btn_shuffle, "Nueva", btn_font, enabled=not racing)

    if phase == GamePhase.BETTING:
        primary_text = "Iniciar"
    elif phase == GamePhase.RACING:
        primary_text = "…"
    else:
        primary_text = "Otra carrera"
    _draw_button(
        surface,
        layout.btn_primary,
        primary_text,
        btn_font,
        enabled=phase != GamePhase.RACING,
    )

    status_y = 46
    if phase == GamePhase.BETTING:
        if bet_index is not None:
            msg = f"Apuesta: {names[bet_index]}"
        else:
            msg = "Apuesta: (opcional) elegí algoritmo en el gráfico o con 1–4"
        surface.blit(font.render(msg, True, COLOR_TEXT), (12, status_y))
    elif phase == GamePhase.RACING:
        surface.blit(font.render("Carrera en curso…", True, COLOR_TEXT), (12, status_y))
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
        surface.blit(font.render(result, True, color), (12, status_y))


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
