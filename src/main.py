#!/usr/bin/env python3
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
        ├── prompt user to select a pattern (interactive menu)
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


def select_pattern():
    """
    Display an interactive menu and return the user's chosen pattern name.

    Runs before curses starts so the menu prints cleanly to the normal
    terminal. ITERATION: loops until the user enters a valid choice.

    Returns:
        str: A valid key from the PATTERNS registry.
    """
    pattern_list = list(PATTERNS.keys())

    print("\n  Conway's Game of Life \n")
    print("  Select a starting pattern:\n")

    # ITERATION — print each available pattern with its index
    for idx, name in enumerate(pattern_list, start=1):
        print(f"    [{idx}] {name}")

    print()

    # ITERATION — keep prompting until a valid choice is made
    while True:
        try:
            raw = input("  Enter number and press Enter: ").strip()
            choice = int(raw)
            if 1 <= choice <= len(pattern_list):
                selected = pattern_list[choice - 1]
                print(f"\n  Starting with: {selected}\n")
                return selected
            limit = len(pattern_list)
            print(f"  Enter a number between 1 and {limit}.")
        except ValueError:
            print("  Invalid input — enter a number.")


def run(stdscr, args):
    """
    Initialise the grid and renderer, then drive the simulation loop.

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
    
def start(screen, args):
    """
    calls run() function and passes the screen to it
    """
    run(screen, args)


def main():
    """
    Program entry point.
    """
    args = parse_args()

    # if the user did not pass --pattern on the CLI, show the menu
    if args.pattern == DEFAULT_PATTERN:
        args.pattern = select_pattern()

        def start(stdscr):
            """
            Sets up the terminal for drawing
            """
            run(stdscr, args)

    try:
        curses.wrapper(start)
    except KeyboardInterrupt:
        # clean exit on Ctrl-C — no stack trace printed to terminal
        sys.exit(0)


if __name__ == "__main__":
    main()