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

# You'll need to import PATTERNS from patterns.py
# from patterns import PATTERNS

# ---------------------------------------------------------------------------
# Default simulation configuration.
# ---------------------------------------------------------------------------
DEFAULT_ROWS = 30
DEFAULT_COLS = 80
DEFAULT_DELAY = 0.12
DEFAULT_PATTERN = "glider"

def parse_args():
    """
    parse commandline arguments

    Returns:
        argparse.Namespace:
            Parse CLI arguments.
    """
    arg_parser = argparse.ArgumentParser(description="Conways Game of life")

    arg_parser.add_argument(
        "--rows",
        type=int,
        default=DEFAULT_ROWS,  # Fixed: was defualt
        help="Grid height in the cells"
    )
    
    arg_parser.add_argument(
        "--cols",
        type=int,
        default=DEFAULT_COLS,  # Fixed: was defualt
        help="Grid width in cells"
    )

    arg_parser.add_argument(  # Fixed: was atg_parser
        "--delay",  # Fixed: should be --delay (not --delays to match variable)
        type=float,
        default=DEFAULT_DELAY,  # Fixed: was defualt
        help="Delay between generations in seconds"   
    )

    # Commented out until you import PATTERNS
    # arg_parser.add_argument(
    #     "--pattern",
    #     choices=PATTERNS.keys(),
    #     default=DEFAULT_PATTERN,
    #     help="Initial Conway seed pattern"
    # )

    return arg_parser.parse_args()  # Fixed: was parser

# For testing the argument parser
if __name__ == "__main__":
    args = parse_args()
    print(f"Rows: {args.rows}")
    print(f"Cols: {args.cols}")
    print(f"Delay: {args.delay}")
    # print(f"Pattern: {args.pattern}")