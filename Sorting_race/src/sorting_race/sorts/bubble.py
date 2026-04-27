from __future__ import annotations

from collections.abc import Iterator

from sorting_race.models import SortStep


def bubble_sort_gen(arr: list[int]) -> Iterator[SortStep]:
    n = len(arr)
    for i in range(n):
        for j in range(0, n - 1 - i):
            yield SortStep(i=j, j=j + 1)
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                yield SortStep(i=j, j=j + 1)
