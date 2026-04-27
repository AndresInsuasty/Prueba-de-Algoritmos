from __future__ import annotations

from collections.abc import Iterator

from sorting_race.models import SortStep


def insertion_sort_gen(arr: list[int]) -> Iterator[SortStep]:
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0:
            yield SortStep(i=j, j=j + 1)
            if arr[j] > key:
                arr[j + 1] = arr[j]
                j -= 1
            else:
                break
        arr[j + 1] = key
        yield SortStep(i=j + 1, j=i)
