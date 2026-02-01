"""Frame-by-frame animation engine for terminal sequences."""

import time

from archadium.display.ansi import (
    clear_screen,
    cursor_to,
    hide_cursor,
    show_cursor,
)
from archadium.display.console import console


def play_frames(
    frames: list[list[str]],
    fps: float = 8.0,
    style: str = "",
    start_row: int = 1,
) -> None:
    """Play a sequence of ASCII art frames as an animation.

    Each frame is a list of strings (lines). Frames are displayed at the given
    fps rate, using cursor repositioning for flicker-free updates.
    """ 
    if not frames:
        return
    delay = 1.0 / fps
    hide_cursor()

    try:
        for frame in frames:
            cursor_to(start_row, 1)
            for line in frame:
                console.print(line, style=style)
            time.sleep(delay)
    finally:
        show_cursor()