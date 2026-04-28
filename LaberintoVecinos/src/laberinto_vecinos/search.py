from __future__ import annotations

from collections import deque
from collections.abc import Iterator

from laberinto_vecinos.models import SearchStep, neighbors4, reconstruct_path


def _is_wall(walls: list[list[bool]], gw: int, gh: int, x: int, y: int) -> bool:
    if x < 0 or y < 0 or x >= gw or y >= gh:
        return True
    return walls[x][y]


def bfs_gen(
    walls: list[list[bool]],
    start: tuple[int, int],
    goal: tuple[int, int],
    gw: int,
    gh: int,
) -> Iterator[SearchStep]:
    """BFS: cede un paso al expandir la cola (frontera en ancho)."""
    q: deque[tuple[int, int]] = deque([start])
    visited: set[tuple[int, int]] = {start}
    parent: dict[tuple[int, int], tuple[int, int] | None] = {start: None}

    yield SearchStep(
        visited=frozenset(visited),
        frontier=tuple(q),
        current=None,
        done=False,
        success=False,
        path=(),
    )

    while q:
        u = q.popleft()
        if u == goal:
            path = tuple(reconstruct_path(parent, goal))
            yield SearchStep(
                visited=frozenset(visited),
                frontier=tuple(q),
                current=u,
                done=True,
                success=True,
                path=path,
            )
            return
        for v in neighbors4(u[0], u[1]):
            if not _is_wall(walls, gw, gh, v[0], v[1]) and v not in visited:
                visited.add(v)
                parent[v] = u
                q.append(v)
        yield SearchStep(
            visited=frozenset(visited),
            frontier=tuple(q),
            current=u,
            done=False,
            success=False,
            path=(),
        )

    yield SearchStep(
        visited=frozenset(visited),
        frontier=(),
        current=None,
        done=True,
        success=False,
        path=(),
    )


def dfs_gen(
    walls: list[list[bool]],
    start: tuple[int, int],
    goal: tuple[int, int],
    gw: int,
    gh: int,
) -> Iterator[SearchStep]:
    """DFS iterativo: la pila es la frontera (se mete por callejones)."""
    stack: list[tuple[int, int]] = [start]
    visited: set[tuple[int, int]] = {start}
    parent: dict[tuple[int, int], tuple[int, int] | None] = {start: None}

    yield SearchStep(
        visited=frozenset(visited),
        frontier=tuple(stack),
        current=start,
        done=False,
        success=False,
        path=(),
    )

    while stack:
        u = stack[-1]
        if u == goal:
            path = tuple(reconstruct_path(parent, goal))
            yield SearchStep(
                visited=frozenset(visited),
                frontier=tuple(stack),
                current=u,
                done=True,
                success=True,
                path=path,
            )
            return
        nxt: tuple[int, int] | None = None
        for v in neighbors4(u[0], u[1]):
            if not _is_wall(walls, gw, gh, v[0], v[1]) and v not in visited:
                nxt = v
                break
        if nxt is not None:
            visited.add(nxt)
            parent[nxt] = u
            stack.append(nxt)
        else:
            stack.pop()
        yield SearchStep(
            visited=frozenset(visited),
            frontier=tuple(stack),
            current=stack[-1] if stack else None,
            done=False,
            success=False,
            path=(),
        )

    yield SearchStep(
        visited=frozenset(visited),
        frontier=(),
        current=None,
        done=True,
        success=False,
        path=(),
    )
