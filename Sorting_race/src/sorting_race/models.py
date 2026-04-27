from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Iterator


@dataclass(frozen=True, slots=True)
class SortStep:
    """Un paso visible del algoritmo (comparación, intercambio o escritura)."""

    i: int | None = None
    j: int | None = None
    pivot: int | None = None


SortGenerator = Callable[[list[int]], Iterator[SortStep]]


class GamePhase(Enum):
    BETTING = auto()
    RACING = auto()
    RESULT = auto()
