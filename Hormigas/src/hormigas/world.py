from __future__ import annotations


def cells_along_segment(x0: int, y0: int, x1: int, y1: int) -> list[tuple[int, int]]:
    """Lista de celdas discretas entre dos puntos (pincel de muros)."""
    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy))
    if steps == 0:
        return [(x0, y0)]
    out: list[tuple[int, int]] = []
    for i in range(steps + 1):
        t = i / steps
        out.append((int(round(x0 + dx * t)), int(round(y0 + dy * t))))
    return out


class World:
    """Grilla: muros, feromonas y comida (valores >= 0)."""

    def __init__(self, gw: int, gh: int) -> None:
        self.gw = gw
        self.gh = gh
        self.walls = [[False] * gh for _ in range(gw)]
        self.phero = [[0.0] * gh for _ in range(gw)]
        self.food = [[0.0] * gh for _ in range(gw)]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.gw and 0 <= y < self.gh

    def is_wall(self, x: int, y: int) -> bool:
        return not self.in_bounds(x, y) or self.walls[x][y]

    def neighbors8(self, x: int, y: int) -> list[tuple[int, int]]:
        out: list[tuple[int, int]] = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if self.in_bounds(nx, ny) and not self.walls[nx][ny]:
                    out.append((nx, ny))
        return out

    def evaporate(self, rho: float) -> None:
        factor = max(0.0, 1.0 - rho)
        for x in range(self.gw):
            row_p = self.phero[x]
            for y in range(self.gh):
                row_p[y] *= factor

    def deposit(self, x: int, y: int, amount: float, cap: float) -> None:
        if not self.in_bounds(x, y) or self.walls[x][y]:
            return
        v = self.phero[x][y] + amount
        self.phero[x][y] = min(cap, v)

    def add_food(self, x: int, y: int, amount: float) -> None:
        if not self.in_bounds(x, y) or self.walls[x][y]:
            return
        self.food[x][y] += amount

    def take_food(self, x: int, y: int) -> bool:
        if self.food[x][y] > 0.01:
            self.food[x][y] = max(0.0, self.food[x][y] - 1.0)
            return True
        return False

    def food_scent(self, x: int, y: int) -> float:
        return self.food[x][y]

    def set_wall_line(self, x0: int, y0: int, x1: int, y1: int, value: bool) -> None:
        for x, y in cells_along_segment(x0, y0, x1, y1):
            if self.in_bounds(x, y):
                self.walls[x][y] = value

    def clear_walls(self) -> None:
        for x in range(self.gw):
            for y in range(self.gh):
                self.walls[x][y] = False

    def clear_pheromones(self) -> None:
        for x in range(self.gw):
            for y in range(self.gh):
                self.phero[x][y] = 0.0
