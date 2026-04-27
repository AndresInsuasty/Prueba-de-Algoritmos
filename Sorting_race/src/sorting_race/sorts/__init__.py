from __future__ import annotations

from sorting_race.models import SortGenerator
from sorting_race.sorts.bubble import bubble_sort_gen
from sorting_race.sorts.insertion import insertion_sort_gen
from sorting_race.sorts.merge import merge_sort_gen
from sorting_race.sorts.quick import quick_sort_gen

ALGORITHMS: list[tuple[str, SortGenerator]] = [
    ("Burbuja", bubble_sort_gen),
    ("Inserción", insertion_sort_gen),
    ("Quick", quick_sort_gen),
    ("Merge", merge_sort_gen),
]

__all__ = [
    "ALGORITHMS",
    "bubble_sort_gen",
    "insertion_sort_gen",
    "merge_sort_gen",
    "quick_sort_gen",
]
