"""
main.py - Entry point of the program
Author : Wisdom A. Honest
Project: Conway Game of life

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
import time

from grid import Grid
from renderer import Renderer
from patterns import PATTERNS, stamp_pattern

# Defualt configuration for the simulation
DEFAULT_ROWS = 30
DEFAULT_COLS = 80
DEFAULT_DELAY = 0.12
DEFAULT_PATTERN = "glider"

def parse_args():
    """
    parse commandline arguments

    Returns:
        argparse.Namespace: parse command line arguments.
    """
    arg_parser = argparse.ArgumentParser(description="Conways Game of life")

    arg_parser.add_argument(
        "--rows",
        type=int,
        default=DEFAULT_ROWS,
        help="Grid height in the cells"
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
         help="Initial Conway seed pattern"
     )

    return arg_parser.parse_args()


def run(terminal_display, args):
    """
    Run the Conway stimulation inside the Curses session.

    Args:
        terminal_display: curses standard screen object

        args: parsed CLI argumnet.
    """
    # Create a simulation grid for the game
    simulatn_grid = Grid(args.rows, args.cols)

    # stamp the initial pattern near the center of the board
    board_pattern = PATTERNS[args.pattern]

    center_row = args.row // 2
    center_col = args.cols // 2
    stamp_pattern(grid, board_pattern, center_row, center_col)

    # create the renderer
    render = Renderer(terminal_display, args.rows, args.cols)
    renderer.init_colors()

    generation = 0

    while True:
        # draw current universe state
        renderer.draw(grid, generation)

        # non-blocking keyboard input
        key = terminal_display.getch()

        # quit simulation
        if key in (ord('q'), ord('Q')):
            break
        generation += 1
        time.sleep(args.delay)
    
    

