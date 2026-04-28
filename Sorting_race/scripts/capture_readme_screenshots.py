#!/usr/bin/env python3
"""Genera capturas PNG en docs/sorting_race/ para el README del repositorio."""
from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from sorting_race.config import COLOR_BG, WINDOW_HEIGHT, WINDOW_WIDTH
from sorting_race.draw import build_hud_layout, draw_hud, draw_quadrant
from sorting_race.main import Game, _build_quadrants
from sorting_race.models import GamePhase


def _blit_game(surface: pygame.Surface, game: Game) -> None:
    layout = build_hud_layout(surface.get_width())
    surface.fill(COLOR_BG)
    draw_hud(
        surface,
        layout,
        phase=game.phase,
        n=game.n,
        steps=game.steps_per_frame,
        seed=game.seed_value,
        bet_index=game.bet_index,
        names=game.names,
        finish_order=game.finish_order if game.phase == GamePhase.RESULT else None,
        bet_won=game.bet_won(),
    )
    quads = _build_quadrants(WINDOW_WIDTH, WINDOW_HEIGHT)
    winner = game.finish_order[0] if game.finish_order else None
    for i, rect in enumerate(quads):
        rank = None
        if game.phase == GamePhase.RESULT and i in game.finish_order:
            rank = game.finish_order.index(i) + 1
        draw_quadrant(
            surface,
            rect,
            title=game.names[i],
            arr=game.tracks[i],
            step=game.last_step[i],
            phase=game.phase,
            quad_index=i,
            bet_index=game.bet_index,
            finish_rank=rank,
            winner_index=winner,
        )


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    repo_root = Path(__file__).resolve().parents[2]
    out_dir = repo_root / "docs" / "sorting_race"
    out_dir.mkdir(parents=True, exist_ok=True)

    g1 = Game(initial_n=64, seed=99)
    g1.bet_index = 2
    _blit_game(screen, g1)
    pygame.image.save(screen, str(out_dir / "01-apuesta.png"))

    g2 = Game(initial_n=64, seed=99)
    g2.steps_per_frame = 4
    g2.start_race()
    for _ in range(150):
        if g2.phase != GamePhase.RACING:
            break
        g2.tick_race()
    _blit_game(screen, g2)
    pygame.image.save(screen, str(out_dir / "02-carrera.png"))

    g3 = Game(initial_n=64, seed=99)
    g3.bet_index = 0
    g3.start_race()
    while g3.phase == GamePhase.RACING:
        g3.tick_race()
    _blit_game(screen, g3)
    pygame.image.save(screen, str(out_dir / "03-resultado.png"))

    pygame.quit()
    print(f"Capturas guardadas en: {out_dir}")


if __name__ == "__main__":
    main()
