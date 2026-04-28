from __future__ import annotations

import argparse
import random
import sys
from collections.abc import Iterator

import pygame

from sorting_race.config import (
    DEFAULT_N,
    DEFAULT_STEPS_PER_FRAME,
    FPS,
    MAX_STEPS,
    MIN_STEPS,
    N_PRESETS,
    VALUE_RANGE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    COLOR_BG,
    HUD_HEIGHT,
)
from sorting_race.draw import build_hud_layout, draw_hud, draw_quadrant, hit_test_hud
from sorting_race.models import GamePhase, SortStep
from sorting_race.sorts import ALGORITHMS


def _build_quadrants(screen_w: int, screen_h: int) -> list[pygame.Rect]:
    pad = 6
    top = HUD_HEIGHT + pad
    avail_w = screen_w - 2 * pad
    avail_h = screen_h - top - pad
    half_w = avail_w // 2 - pad // 2
    half_h = avail_h // 2 - pad // 2
    left = pad
    mid_x = pad + half_w + pad
    return [
        pygame.Rect(left, top, half_w, half_h),
        pygame.Rect(mid_x, top, half_w, half_h),
        pygame.Rect(left, top + half_h + pad, half_w, half_h),
        pygame.Rect(mid_x, top + half_h + pad, half_w, half_h),
    ]


def _random_heights(n: int, rng: random.Random) -> list[int]:
    lo, hi = VALUE_RANGE
    return [rng.randint(lo, hi) for _ in range(n)]


class Game:
    def __init__(self, *, initial_n: int, seed: int | None) -> None:
        self._rng = random.Random(seed)
        self.seed_value = seed
        self.n = max(2, min(512, initial_n))
        self._preset_idx = self._closest_preset_index(initial_n)
        self.steps_per_frame = DEFAULT_STEPS_PER_FRAME
        self.phase = GamePhase.BETTING
        self.bet_index: int | None = None
        self.tracks: list[list[int]] = []
        self.generators: list[Iterator[SortStep] | None] = [None, None, None, None]
        self.last_step: list[SortStep | None] = [None, None, None, None]
        self.finished: list[bool] = [False, False, False, False]
        self.finish_order: list[int] = []
        self.names = [name for name, _ in ALGORITHMS]
        self._new_permutation()

    @staticmethod
    def _closest_preset_index(n: int) -> int:
        best = 0
        for i, v in enumerate(N_PRESETS):
            if abs(v - n) < abs(N_PRESETS[best] - n):
                best = i
        return best

    def _new_permutation(self) -> None:
        self.phase = GamePhase.BETTING
        self.bet_index = None
        heights = _random_heights(self.n, self._rng)
        self._rng.shuffle(heights)
        perm = heights
        self.tracks = [perm[:] for _ in ALGORITHMS]
        self.generators = [None, None, None, None]
        self.last_step = [None, None, None, None]
        self.finished = [False, False, False, False]
        self.finish_order = []

    def set_n(self, n: int) -> None:
        self.n = max(2, min(512, n))
        self._preset_idx = self._closest_preset_index(self.n)
        self._new_permutation()

    def cycle_n_preset(self, delta: int) -> None:
        self._preset_idx = (self._preset_idx + delta) % len(N_PRESETS)
        self.n = N_PRESETS[self._preset_idx]
        self._new_permutation()

    def select_n_value(self, n: int) -> None:
        if n not in N_PRESETS:
            return
        self._preset_idx = N_PRESETS.index(n)
        self.n = n
        self._new_permutation()

    def adjust_steps(self, delta: int) -> None:
        self.steps_per_frame = max(MIN_STEPS, min(MAX_STEPS, self.steps_per_frame + delta))

    def start_race(self) -> None:
        self.phase = GamePhase.RACING
        self.finish_order = []
        self.finished = [False, False, False, False]
        self.last_step = [None, None, None, None]
        perm = self.tracks[0][:]
        self.tracks = [perm[:] for _ in ALGORITHMS]
        self.generators = [gen(arr) for arr, (_, gen) in zip(self.tracks, ALGORITHMS)]

    def tick_race(self) -> None:
        assert self.generators is not None
        for idx, gen in enumerate(self.generators):
            if self.finished[idx] or gen is None:
                continue
            for _ in range(self.steps_per_frame):
                try:
                    self.last_step[idx] = next(gen)
                except StopIteration:
                    self.finished[idx] = True
                    self.finish_order.append(idx)
                    self.last_step[idx] = None
                    break
        if all(self.finished):
            self.phase = GamePhase.RESULT

    def quadrant_at(self, pos: tuple[int, int], quads: list[pygame.Rect]) -> int | None:
        x, y = pos
        for i, r in enumerate(quads):
            if r.collidepoint(x, y):
                return i
        return None

    def bet_won(self) -> bool | None:
        if self.bet_index is None or not self.finish_order:
            return None
        return self.finish_order[0] == self.bet_index


def main() -> None:
    parser = argparse.ArgumentParser(description="Carrera de ordenamientos (Pygame).")
    parser.add_argument("--n", type=int, default=DEFAULT_N, help="Cantidad de barras")
    parser.add_argument("--seed", type=int, default=None, help="Semilla reproducible")
    args = parser.parse_args()

    pygame.init()
    pygame.display.set_caption("Sorting Race — competencia de algoritmos")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    game = Game(initial_n=args.n, seed=args.seed)

    quads = _build_quadrants(WINDOW_WIDTH, WINDOW_HEIGHT)

    running = True
    while running:
        layout = build_hud_layout(screen.get_width())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game._new_permutation()
                elif event.key == pygame.K_SPACE:
                    if game.phase == GamePhase.BETTING:
                        game.start_race()
                    elif game.phase == GamePhase.RESULT:
                        game._new_permutation()
                elif event.key == pygame.K_LEFTBRACKET:
                    game.cycle_n_preset(-1)
                elif event.key == pygame.K_RIGHTBRACKET:
                    game.cycle_n_preset(1)
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                    game.adjust_steps(1)
                elif event.key == pygame.K_MINUS:
                    game.adjust_steps(-1)
                elif pygame.K_1 <= event.key <= pygame.K_4:
                    if game.phase == GamePhase.BETTING:
                        game.bet_index = event.key - pygame.K_1
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                hud_hit = hit_test_hud(layout, event.pos)
                if hud_hit is not None:
                    if hud_hit.startswith("n:") and game.phase != GamePhase.RACING:
                        game.select_n_value(int(hud_hit.split(":", 1)[1]))
                    elif hud_hit == "steps_minus":
                        game.adjust_steps(-1)
                    elif hud_hit == "steps_plus":
                        game.adjust_steps(1)
                    elif hud_hit == "shuffle" and game.phase != GamePhase.RACING:
                        game._new_permutation()
                    elif hud_hit == "primary":
                        if game.phase == GamePhase.BETTING:
                            game.start_race()
                        elif game.phase == GamePhase.RESULT:
                            game._new_permutation()
                elif game.phase == GamePhase.BETTING:
                    hit = game.quadrant_at(event.pos, quads)
                    if hit is not None:
                        game.bet_index = hit

        if game.phase == GamePhase.RACING:
            game.tick_race()

        screen.fill(COLOR_BG)
        draw_hud(
            screen,
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

        winner = game.finish_order[0] if game.finish_order else None
        for i, rect in enumerate(quads):
            rank = None
            if game.phase == GamePhase.RESULT and i in game.finish_order:
                rank = game.finish_order.index(i) + 1
            draw_quadrant(
                screen,
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

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
