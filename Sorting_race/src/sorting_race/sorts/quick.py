from __future__ import annotations

from collections.abc import Iterator

from sorting_race.models import SortStep


def quick_sort_gen(arr: list[int]) -> Iterator[SortStep]:
    """Quicksort in-place (Lomuto) con pila explícita; un yield por comparación o swap relevante."""
    if len(arr) <= 1:
        return
    stack: list[tuple[int, int]] = [(0, len(arr) - 1)]
    while stack:
        lo, hi = stack.pop()
        if lo >= hi:
            continue
        pivot_idx = hi
        pivot_val = arr[hi]
        i = lo
        for j in range(lo, hi):
            yield SortStep(i=i, j=j, pivot=pivot_idx)
            if arr[j] <= pivot_val:
                if i != j:
                    arr[i], arr[j] = arr[j], arr[i]
                    yield SortStep(i=i, j=j, pivot=pivot_idx)
                i += 1
        if i != hi:
            arr[i], arr[hi] = arr[hi], arr[i]
            yield SortStep(i=i, j=hi, pivot=pivot_idx)
        p = i
        stack.append((lo, p - 1))
        stack.append((p + 1, hi))
