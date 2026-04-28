from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SearchStep:
    """Un fotograma de la visualización: visitados, frontera y estado."""

    visited: frozenset[tuple[int, int]]
    frontier: tuple[tuple[int, int], ...]
    current: tuple[int, int] | None
    done: bool
    success: bool
    path: tuple[tuple[int, int], ...]  # vacío hasta encontrar meta


def neighbors4(x: int, y: int) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]]:
    return (x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)


def reconstruct_path(parent: dict[tuple[int, int], tuple[int, int] | None], goal: tuple[int, int]) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    cur: tuple[int, int] | None = goal
    while cur is not None:
        out.append(cur)
        cur = parent.get(cur)
    out.reverse()
    return out
