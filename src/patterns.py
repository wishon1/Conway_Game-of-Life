"""
This module contains the main pattern for Conways Game of life.

Module function:
    - Define reusable Conway seed patterns
    - Stamp patterns onto a Grid object
    - Keep pattern data isolated from simulation logic

Design decision:
    Patterns are represented as tuples of relative coordinate offsets.
    This keeps them immutable, lightweight, and reusable.

    Each pattern is defined relative to an origin (0, 0).
    stamp_pattern() translates the pattern to any desired position
    on the Grid.

Coordinate convention:
    (row_offset, col_offset)

Example:
    GLIDER = (
        (0, 1),
        (1, 2),
        (2, 0),
        (2, 1),
        (2, 2),
    )

    If stamped at (10, 20), the live cells become:
        (10, 21)
        (11, 22)
        (12, 20)
        (12, 21)
        (12, 22)
"""
# Oscillator patterns
BLINKER = (
    (0, 0),
    (0, 1),
    (0, 2),
)

# Spaceship patterns
GLIDER = (
    (0, 1),
    (1, 2),
    (2, 0),
    (2, 1),
    (2, 2),
)

# The registry used by main.py for command line selection.
PATTERNS = {
    "blinker": BLINKER,
    "glider": GLIDER,
}

def stamp_pattern(grid, pattern, start_row, start_col):
    """
    method to stamp a conway pattern into a grid; it will iterate
    each pair in the pattern and translate it relative to the 'start'

    Args:
        grid (Grid): Target Grid object.

        pattern (tuple[tuple[int, int]]): Iterable of relative coordinate offsets.

        start_row (int): Row origin where the pattern begins.

        start_col (int): Column origin where the pattern starts.
    """
    for row, col in pattern:
        grid.set_alivestart(start_row + row, start_col + col)
