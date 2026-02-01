"""Low-level ANSI escape code helpers for cursor positioning and screen control."""

import sys

def cursor_up(n: int = 1) -> None:
    """ANSI escape sequence to move the cursor up."""
    sys.stdout.write(f"\033[{n}A")
    sys.stdout.flush()

def cursor_down(n: int = 1) -> None:
    """ANSI escape sequence to move the cursor down."""
    sys.stdout.write(f"\033[{n}B")
    sys.stdout.flush()

def cursor_to(row: int, col: int) -> None:
    """ANSI escape sequence to move the cursor to a specific position."""
    sys.stdout.write(f"\033[{row};{col}H")
    sys.stdout.flush()

def clear_screen() -> None:
    """ANSI escape sequence to clear the screen."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def hide_cursor() -> None:
    """ANSI escape sequence to hide the cursor."""
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def show_cursor() -> None:
    """ANSI escape sequence to show the cursor."""
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()