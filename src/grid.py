"""
grid.py — The brain of the game.

Author : Wisdom A. Honest
Project: Conway Game of life

This module tracks which cells are alive or dead, counts neighbors, applies
Conway's rules, and advances to the next generation. It knows nothing about
screens or terminals.
"""

# The 8 cardinal and diagonal directions surrounding any cell.
# Defined once at module level — never recreated per call.
NEIGHBOR_DIRECTIONS = (
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1), (0, 1),
    (1, -1), (1, 0), (1, 1),
)


class Grid:
    """
    Manages the game board with two layers; current and next.

    Attributes:
        rows (int): Number of rows in the grid.
        cols (int): Number of columns in the grid.
    """

    def __init__(self, rows, cols):
        """
        Create an empty board with the given size. Sets up both layers
        once and reuses them.

        Args:
            rows (int): Number of rows in the grid.
            cols (int): Number of columns in the grid.
        """
        self.rows = rows
        self.cols = cols

        # double buffer — _current is read, _next is written each tick
        self._current_grid = self._empty_board()
        self._next_grid = self._empty_board()

        # snapshot of _current before the last next_generation() call
        self._previous_grid = self._empty_board()

    def set_alive(self, row, col):
        """
        Set cell (row, col) to alive.

        Args:
            row (int): Row index.
            col (int): Column index.
        """
        if self._in_bounds(row, col):
            self._current_grid[row][col] = 1

    def is_alive(self, row, col):
        """
        Return True if cell (row, col) is alive in the current generation.

        Args:
            row (int): Row index.
            col (int): Column index.

        Returns:
            bool: True if the cell is alive, False otherwise.
        """
        return self._current_grid[row][col] == 1

    def was_alive(self, row, col):
        """
        Return True if cell (row, col) was alive in the previous generation.

        Args:
            row (int): Row index.
            col (int): Column index.

        Returns:
            bool: True if the cell was alive last generation, False otherwise.
        """
        return self._previous_grid[row][col] == 1

    def next_generation(self):
        """
        Advance the universe by one generation in-place.

        I structured it this way to keep things efficient while staying
        clear:

        ALGORITHM:
            1. First, copy the current grid into _previous so we can use
               it for neighbor counting.
            2. Then, for every cell, count its live neighbors (using the
               recursive helper).
            3. Apply Conway's four rules to decide if the cell lives or
               dies in the next generation, and store that in _next.
            4. Finally, swap the references to _current and _next —
               O(1) with no extra memory allocation.

        ITERATION:
            The nested loops go through every cell exactly once per
            generation, row by row (row-major order). This matches how
            Python stores the list-of-lists, so it's reasonably
            cache-friendly. Time complexity is O(rows * cols) per
            generation, which is the best you can do for Game of Life.
            Space-wise, we use two grids total (double buffering), but
            they're allocated once at the start and reused forever.

        RISC-V / HPC note:
            Row-major traversal means each inner iteration accesses the
            next contiguous memory address. At the scale of the 400-code
            HPC project this internship targets, access pattern discipline
            like this compounds into meaningful throughput gains.
        """
        # snapshot current state before overwriting — used by was_alive()
        for row in range(self.rows):
            for col in range(self.cols):
                self._previous_grid[row][col] = self._current_grid[row][col]

        # ITERATION — nested loops traverse every cell in the grid
        for row in range(self.rows):        # outer: iterate over rows
            for col in range(self.cols):    # inner: iterate over cols

                live_neighbor_count = self._count_neighbors(
                    row, col, NEIGHBOR_DIRECTIONS, 0
                )
                cell_is_alive = self._current_grid[row][col] == 1

                if cell_is_alive:
                    # rules 1, 2, 3 — survival or death of a live cell
                    self._next_grid[row][col] = (
                        1 if live_neighbor_count in (2, 3) else 0
                    )
                else:
                    # rule 4 — reproduction into a dead cell
                    self._next_grid[row][col] = (
                        1 if live_neighbor_count == 3 else 0
                    )

        # swap buffers — O(1) reference swap, no memory allocation
        self._current_grid, self._next_grid = (
            self._next_grid, self._current_grid
        )

    def _count_neighbors(self, row, col, directions, idx):
        """
        Count the live neighbors of cell (row, col) by recursively
        checking each direction.

        RECURSION:
            Base case  : when idx reaches the end of the directions list,
                         return 0.
            Recursive  : look up the neighbor in the current direction,
                         add its value (0 or 1), and recurse to the next
                         direction.

        The grid is toroidal (it wraps around at the edges), so a cell
        on the right edge sees the left edge as its neighbor, and same
        for top/bottom. Recursion depth is always exactly 8, so it's
        perfectly safe regardless of grid size.

        Note: In real performance-critical code this would be replaced
        with eight direct lookups and a sum — no function call overhead,
        no stack frames. This version is here to show the pattern
        clearly, as requested.

        Args:
            row        (int)  : Row index of the cell being evaluated.
            col        (int)  : Column index of the cell being evaluated.
            directions (tuple): The NEIGHBOR_DIRECTIONS constant.
            idx        (int)  : Current position in the directions tuple.

        Returns:
            int: Count of live neighbors in the range [0, 8].
        """
        # base case — all 8 directions have been checked
        if idx == len(directions):
            return 0

        delta_row, delta_col = directions[idx]

        # toroidal wrap — modulo maps out-of-bounds indices to opposite edge
        neighbor_row = (row + delta_row) % self.rows
        neighbor_col = (col + delta_col) % self.cols
        neighbor_value = self._current_grid[neighbor_row][neighbor_col]

        # recursive case — add this neighbor and check the next direction
        return neighbor_value + self._count_neighbors(
            row, col, directions, idx + 1
        )

    def _in_bounds(self, row, col):
        """
        Return True if (row, col) is a valid cell index.

        Args:
            row (int): Row index.
            col (int): Column index.

        Returns:
            bool: True if within grid bounds, False otherwise.
        """
        return 0 <= row < self.rows and 0 <= col < self.cols

    def _empty_board(self):
        """
        Allocate and return a rows x cols board filled with zeros.

        Returns:
            list[list[int]]: 2D list of integers, all initialised to 0.
        """
        return [[0] * self.cols for _ in range(self.rows)]