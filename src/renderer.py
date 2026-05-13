#!/usr/bin/env python3
"""
renderer.py — Handles everything you see on screen.

This module draws the game, animates new and dying cells, and shows the
generation counter. It reads the grid but never changes it.

Cell states and their visual representation:
    ALIVE  — cell survived from last generation  → bright green  '█'
    NEW    — cell just came alive this generation → cyan blink    '▓'
    DEAD   — cell just died this generation       → red fade      '░'
    EMPTY  — cell has been dead                   → empty         ' '
"""

import curses

ALIVE = 0
NEW = 1
DEAD = 2
EMPTY = 3

# Initialize cell state with block elements to give the grid a dense,
# intentional look in any terminal.
SYMBOL = {
    ALIVE: '\u2588',   # █  full block
    NEW:   '\u2593',   # ▓  dark shade
    DEAD:  '\u2591',   # ░  light shade
    EMPTY: ' ',
}

# Animation constants.
#
# BLINK_SPEED — frames per half-cycle for NEW cell blink.
#   A value of 3 means the symbol alternates every 3 frames.
#   Fast enough to be visible, slow enough to read at default speed.
#
# FADE_FRAMES — generations a DEAD cell shows its fade symbol.
#   Set to 1: one frame of '░' then gone. Gives moving patterns a
#   short motion trail — the slide effect.
BLINK_SPEED = 3
FADE_FRAMES = 1


class Renderer:
    """
    Controls everything you see on screen.
    Reads the grid to draw cells, but never changes it.

    Attributes:
        row_count (int): Grid height in cells.
        col_count (int): Grid width in cells.
    """

    def __init__(self, screen, row_count, col_count):
        """
        Set up the renderer with screen size and make sure key presses
        don't freeze the game loop.

        Args:
            screen: The curses standard screen passed in by curses.wrapper.
            row_count (int): Number of grid rows to render.
            col_count (int): Number of grid columns to render.
        """
        self._screen = screen
        self.row_count = row_count
        self.col_count = col_count
        self._frame_number = 0

        # configure curses session
        curses.curs_set(0)
        self._screen.nodelay(True)
        self._screen.keypad(True)

    def init_colors(self):
        """
        Initialise curses color pairs for each cell state.

        Color pair index mapping:
            1 → ALIVE  : bright green on black
            2 → NEW    : cyan on black  (blink)
            3 → DEAD   : red on black   (fade)
            4 → EMPTY  : black on black (invisible)
            5 → INFO   : white on blue  (status bar)
        """
        curses.start_color()
        curses.use_default_colors()

        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN,  curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED,   curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE)

    def draw(self, grid, generation):
        """
        Draw the entire game screen. Check every cell, animate NEW and
        DEAD cell transitions, then update the display.

        ITERATION:
            Nested loops visit every cell exactly once per frame in
            row-major order, matching grid.py's memory layout.

        Args:
            grid (Grid)      : The current game state. Read-only.
            generation (int) : Current generation count for status bar.
        """
        self._screen.erase()

        # ITERATION — draw every cell in the grid row by row
        # correct
        for row in range(self.row_count):
            for col in range(self.col_count):
                state = self._get_cell_state(grid, row, col)
                symbol, style = self._pick_symbol(state)
                self._place_cell(row, col, symbol, style)

        self._show_info(generation)
        self._screen.refresh()
        self._frame_number += 1

    def _get_cell_state(self, grid, row, col):
        """
        Figure out if a cell is ALIVE, NEW, DEAD, or EMPTY by comparing
        this generation to the last one.

        Args:
            grid (Grid): The current game state.
            row  (int) : Row index.
            col  (int) : Column index.

        Returns:
            int: One of the module-level state constants
        """
        now_alive = grid.is_alive(row, col)
        was_alive = grid.was_alive(row, col)

        if now_alive and was_alive:
            return ALIVE
        if now_alive and not was_alive:
            return NEW
        if not now_alive and was_alive:
            return DEAD
        return EMPTY

    def _pick_symbol(self, state):
        """
        Return the symbol and color for a cell state.
        NEW cells blink on and off. DEAD cells fade briefly before
        vanishing. ALIVE and EMPTY cells are static.

        Args:
            state (int): One of ALIVE, NEW, DEAD, EMPTY.

        Returns:
            tuple[str, int]: (symbol character, curses attribute int)
        """
        if state == ALIVE:
            return SYMBOL[ALIVE], curses.color_pair(1) | curses.A_BOLD

        if state == NEW:
            # newly born cells blink on and off
            # current frame position inside the full blink cycle
            current_frame = self._frame_number % (BLINK_SPEED * 2)

            # first half of the cycle shows the symbol
            symbol = SYMBOL[NEW] if current_frame < BLINK_SPEED else ' '
            return symbol, curses.color_pair(2) | curses.A_BOLD

        if state == DEAD:
            # recently dead cells briefly show a fade symbol
            fade_symbol = (
                SYMBOL[DEAD] if self._frame_number % FADE_FRAMES == 0
                else ' '
            )
            return fade_symbol, curses.color_pair(3)

        # EMPTY — invisible
        return SYMBOL[EMPTY], curses.color_pair(4)

    def _place_cell(self, row, col, symbol, style):
        """
        Draw one cell on screen. If the cell is outside the terminal
        window, ignore it quietly so the game doesn't crash.

        Args:
            row    (int): Row position on screen.
            col    (int): Column position on screen.
            symbol (str): Single character to draw.
            style  (int): Curses attribute (color pair + style flags).
        """
        try:
            self._screen.addch(row, col, symbol, style)
        except curses.error:
            pass

    def _show_info(self, generation):
        """
        Show the generation counter and quit instructions at the bottom
        of the screen in white text on a blue background.

        Args:
            generation (int): Current generation number.
        """
        max_row, max_col = self._screen.getmaxyx()
        info_text = (
            f" Generation: {generation:<6} | "
            f"Conway's Game of Life| "
            f"Press 'q' to quit "
        )
        # truncate to terminal width — prevents crash on narrow terminals
        info_text = info_text[:max_col - 1]

        try:
            self._screen.addstr(
                max_row - 1, 0,
                info_text.ljust(max_col - 1),
                curses.color_pair(5)
            )
        except curses.error:
            pass