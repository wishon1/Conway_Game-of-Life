"""
main.py - Entry point of the program.

Architecture:
    main.py intentionally contains NO Conway rules and NO rendering
    implementation details.

    It orchestrates collaboration between:
        grid.py      → simulation engine
        renderer.py  → terminal visualization
        patterns.py  → reusable seed patterns

Execution flow:
    main()
        ├── parse arguments
        ├── create Grid
        ├── stamp selected pattern
        ├── initialise curses Renderer
        ├── enter simulation loop
        │     ├── render frame
        │     ├── process keyboard input
        │     ├── advance generation
        │     └── sleep
        └── exit cleanly on 'q'
"""
import argparse
import curses
import sys
import time

from grid import Grid
from patterns import PATTERNS, stamp_pattern
from renderer import Renderer

# Default configuration for the simulation
DEFAULT_ROWS = 30
DEFAULT_COLS = 80
DEFAULT_DELAY = 0.12
DEFAULT_PATTERN = "glider"


def parse_args():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    arg_parser = argparse.ArgumentParser(description="Conways Game of life")

    arg_parser.add_argument(
        "--rows",
        type=int,
        default=DEFAULT_ROWS,
        help="Grid height in cells"
    )

    arg_parser.add_argument(
        "--cols",
        type=int,
        default=DEFAULT_COLS,
        help="Grid width in cells"
    )

    arg_parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY,
        help="Delay between generations in seconds"
    )

    arg_parser.add_argument(
        "--pattern",
        choices=PATTERNS.keys(),
        default=DEFAULT_PATTERN,
        help="Seed pattern to start with (default: glider)"
    )

    return arg_parser.parse_args()


def run(stdscr, args):
    """
    Initialise the grid and renderer, then drive the simulation loop.

    This function is passed to curses.wrapper so the terminal is always
    restored cleanly on exit or crash.

    Args:
        stdscr: The curses standard screen provided by curses.wrapper.
        args (argparse.Namespace): Parsed command line arguments.
    """
    # create grid and stamp the chosen seed pattern at the center
    grid = Grid(args.rows, args.cols)

    center_row = args.rows // 2
    center_col = args.cols // 2
    stamp_pattern(grid, PATTERNS[args.pattern], center_row, center_col)

    # initialise renderer — owns all terminal I/O from this point
    renderer = Renderer(stdscr, args.rows, args.cols)
    renderer.init_colors()

    generation = 0

    # ITERATION: the simulation loop.
    # Each pass through this loop is one tick of the Game of Life universe.
    while True:
        # draw current universe state
        renderer.draw(grid, generation)

        # non-blocking keyboard input — stdscr configured nodelay in Renderer
        key = stdscr.getch()

        # quit on 'q' or 'Q'
        if key in (ord('q'), ord('Q')):
            break

        # advance the universe by one generation
        grid.next_generation()

        generation += 1
        time.sleep(args.delay)


def main():
    """
    Program entry point.

    Parses arguments and hands control to curses.wrapper which handles
    terminal initialisation and guaranteed cleanup on exit or crash.
    """
    args = parse_args()

    try:
        curses.wrapper(lambda stdscr: run(stdscr, args))
    except KeyboardInterrupt:
        # clean exit on Ctrl-C — no stack trace printed to terminal
        sys.exit(0)


if __name__ == "__main__":
    main()