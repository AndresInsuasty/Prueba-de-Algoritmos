from __future__ import annotations

import random

from hormigas.config import PHERO_CAP, TAU0
from hormigas.world import World


class Ant:
    """Hormiga simplificada: forrajeo estocástico (feromona + ruido + olfato a comida);
    regreso al nido por memoria de camino depositando feromonas (idea ACO)."""

    __slots__ = ("gx", "gy", "carrying", "path_from_nest", "rng")

    def __init__(self, gx: int, gy: int, rng: random.Random) -> None:
        self.gx = gx
        self.gy = gy
        self.carrying = False
        self.path_from_nest: list[tuple[int, int]] = []
        self.rng = rng

    def _pick_neighbor_forage(self, world: World, alpha: float) -> tuple[int, int] | None:
        nbs = world.neighbors8(self.gx, self.gy)
        if not nbs:
            return None
        weights: list[float] = []
        for nx, ny in nbs:
            ph = world.phero[nx][ny]
            scent = world.food_scent(nx, ny)
            w = ((ph + TAU0) ** alpha) * self.rng.uniform(0.55, 1.15)
            if scent > 0.01:
                w *= 35.0 + min(scent, 8.0) * 6.0
            weights.append(max(w, 1e-9))
        return self.rng.choices(nbs, weights=weights, k=1)[0]

    def step(
        self,
        world: World,
        nest_cells: set[tuple[int, int]],
        *,
        alpha: float,
        q_deposit: float,
    ) -> None:
        if not self.carrying:
            nxt = self._pick_neighbor_forage(world, alpha)
            if nxt is None:
                return
            self.path_from_nest.append((self.gx, self.gy))
            self.gx, self.gy = nxt
            if (self.gx, self.gy) not in nest_cells and world.take_food(self.gx, self.gy):
                self.carrying = True
            return

        if self.path_from_nest:
            px, py = self.path_from_nest.pop()
            world.deposit(self.gx, self.gy, q_deposit, PHERO_CAP)
            self.gx, self.gy = px, py
            if (self.gx, self.gy) in nest_cells:
                self.carrying = False
                self.path_from_nest.clear()
            return

        if (self.gx, self.gy) in nest_cells:
            self.carrying = False
            self.path_from_nest.clear()


def spawn_ant_in_nest(rng: random.Random, nest_cells: list[tuple[int, int]]) -> Ant:
    gx, gy = rng.choice(nest_cells)
    return Ant(gx, gy, rng)
