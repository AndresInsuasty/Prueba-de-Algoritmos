from __future__ import annotations

from collections.abc import Iterator

from sorting_race.models import SortStep


def _merge(
    arr: list[int],
    lo: int,
    mid: int,
    hi: int,
) -> Iterator[SortStep]:
    left = arr[lo : mid + 1]
    right = arr[mid + 1 : hi + 1]
    i = j = 0
    k = lo
    while i < len(left) and j < len(right):
        li = lo + i
        rj = mid + 1 + j
        yield SortStep(i=li, j=rj)
        if left[i] <= right[j]:
            arr[k] = left[i]
            i += 1
        else:
            arr[k] = right[j]
            j += 1
        k += 1
    while i < len(left):
        yield SortStep(i=lo + i, j=k)
        arr[k] = left[i]
        i += 1
        k += 1
    while j < len(right):
        yield SortStep(i=mid + 1 + j, j=k)
        arr[k] = right[j]
        j += 1
        k += 1


def _sort_range(arr: list[int], lo: int, hi: int) -> Iterator[SortStep]:
    if hi <= lo:
        return
    mid = (lo + hi) // 2
    yield from _sort_range(arr, lo, mid)
    yield from _sort_range(arr, mid + 1, hi)
    yield from _merge(arr, lo, mid, hi)


def merge_sort_gen(arr: list[int]) -> Iterator[SortStep]:
    n = len(arr)
    if n > 1:
        yield from _sort_range(arr, 0, n - 1)
