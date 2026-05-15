# Algorithm Notes

## Conway's Game of Life — The Rules

Each cell is either **alive** (1) or **dead** (0). Every generation,
four rules are applied simultaneously to every cell based on how many
of its 8 neighbors are alive:

| Rule | Condition | Outcome |
|------|-----------|---------|
| 1 | Live cell, fewer than 2 live neighbors | Dies — underpopulation |
| 2 | Live cell, 2 or 3 live neighbors | Survives |
| 3 | Live cell, more than 3 live neighbors | Dies — overpopulation |
| 4 | Dead cell, exactly 3 live neighbors | Becomes alive — reproduction |

These four rules produce emergent complexity from trivially simple
local logic. Patterns like gliders, oscillators, and still lifes all
arise from nothing more than these four conditions applied repeatedly.

---

## Algorithmic Patterns

### Iteration

The grid update uses a classic double nested loop:

```python
for row in range(self.rows):        # outer: iterate over rows
    for col in range(self.cols):    # inner: iterate over cols
        n = self._count_neighbors(row, col, NEIGHBOR_DIRECTIONS, 0)
        # apply Conway's rules to compute next state
```

**Time complexity:** O(rows × cols) per generation — every cell is
visited exactly once.

**Space complexity:** O(rows × cols) for the double-buffer. Both boards
are allocated once at `__init__` and reused forever. No heap allocation
inside the game loop.

**Memory access pattern:** The outer loop iterates over rows, the inner
loop over columns — row-major order. This matches how Python stores a
list-of-lists in memory, meaning each inner iteration accesses the next
contiguous memory address. Sequential access like this is cache-friendly
on any modern processor.

A column-major traversal of the same grid would produce identical
output but stride across memory on every inner step, causing cache
misses at scale. Row-major is the correct choice here.

---

### Recursion

Neighbor counting is implemented as a recursive walk over a fixed
8-direction tuple:

```python
def _count_neighbors(self, row, col, directions, idx):
    # base case — all 8 directions have been checked
    if idx == len(directions):
        return 0

    delta_row, delta_col = directions[idx]
    neighbor_row = (row + delta_row) % self.rows   # toroidal wrap
    neighbor_col = (col + delta_col) % self.cols
    neighbor_value = self._current_grid[neighbor_row][neighbor_col]

    # recursive case — add this neighbor, check the next direction
    return neighbor_value + self._count_neighbors(
        row, col, directions, idx + 1
    )
```

**Base case:** `idx == len(directions)` — all 8 directions checked,
return 0.

**Recursive case:** read the neighbor at `directions[idx]`, add its
value (0 or 1), recurse with `idx + 1`.

**Recursion depth:** exactly 8 for every call — bounded and constant
regardless of grid size. No risk of stack overflow.

**Note:** In a performance-critical context this would be replaced with
8 explicit array lookups summed directly — no function call overhead,
no stack frames. The recursive form here demonstrates the pattern
explicitly.

---

## Double-Buffer Pattern

The grid maintains two boards — `_current` and `_next`. Every generation:

1. Read all cell states from `_current`
2. Write all next states to `_next`
3. Swap references — `_current, _next = _next, _current`

This guarantees that all cells are evaluated against the same
generation state. Without double-buffering, a cell updated early in
the loop would influence cells updated later in the same pass —
corrupting the simulation.

The swap itself is O(1) — just two reference reassignments, no memory
allocation or copying.

---

## Toroidal Topology

The grid wraps at the edges — a cell on the right edge treats the left
edge as its neighbor, and the same applies to top and bottom:

```python
neighbor_row = (row + delta_row) % self.rows
neighbor_col = (col + delta_col) % self.cols
```

Modulo arithmetic maps any out-of-bounds index back to the opposite
edge in one operation. This keeps patterns alive at boundaries and
prevents edge cells from having fewer than 8 neighbors, which would
require special-case logic throughout the neighbor count.

---

## Complexity Summary

| Operation | Time | Space |
|-----------|------|-------|
| `next_generation()` | O(rows × cols) | O(1) extra — double-buffer pre-allocated |
| `_count_neighbors()` | O(1) — depth always 8 | O(8) stack frames |
| `stamp_pattern()` | O(pattern size) | O(1) |
| Full simulation, N generations | O(N × rows × cols) | O(rows × cols) |
