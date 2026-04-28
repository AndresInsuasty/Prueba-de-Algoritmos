from __future__ import annotations

from dataclasses import dataclass

from hormigas.config import (
    ALPHA,
    ANT_COUNT,
    Q_DEPOSIT,
    RHO,
)


@dataclass
class SimParams:
    """Parámetros ajustables en vivo (valores por defecto = config)."""

    rho: float = RHO
    alpha: float = ALPHA
    q_deposit: float = Q_DEPOSIT
    steps_per_frame: int = 2
    ant_count: int = ANT_COUNT

    def clamp(self) -> None:
        self.rho = max(0.003, min(0.048, round(self.rho, 4)))
        self.alpha = max(0.6, min(3.2, round(self.alpha, 2)))
        self.q_deposit = max(0.25, min(4.5, round(self.q_deposit, 2)))
        self.steps_per_frame = max(1, min(32, int(self.steps_per_frame)))
        self.ant_count = max(4, min(200, int(self.ant_count)))
