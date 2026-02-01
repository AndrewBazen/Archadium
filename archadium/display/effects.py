"""Terminal display effects: typewriter, fade, etc."""

import random
import time

from archadium.display.ansi import (
    clear_screen,
    hide_cursor,
    show_cursor,
)
from archadium.display.console import console


def typewriter(text: str, delay: float = 0.03, style: str = "", end: str = "\n") -> None:
    """Typewriter effect for text display."""
    for char in text:
        console.print(char, style=style, end="", highlight=False)
        if char not in (" ", "\n"):
            time.sleep(delay)
    console.print(end, end="")


def fade_in_lines(lines: list[str], delay: float = 0.12, style: str = "") -> None:
    """Fade in lines of text one by one."""
    for line in lines:
        console.print(line, style=style)
        time.sleep(delay)


def screen_shake(text: str, intensity: int = 2, cycles: int = 3, style: str = "damage") -> None:
    """Simulate a screen shake effect."""
    hide_cursor()
    for _ in range(cycles):
        offset = random.randint(0, intensity)
        padding = " " * offset
        console.print(f"{padding}{text}", style=style, end="\r")
        time.sleep(0.05)
    console.print(text, style=style)
    show_cursor()


def flash_text(
    text: str,
    style_a: str = "bold bright_white",
    style_b: str = "dim white",
    cycles: int = 3,
    delay: float = 0.15,
) -> None:
    """Flash text between two styles."""
    hide_cursor()
    for i in range(cycles * 2):
        style = style_a if i % 2 == 0 else style_b
        console.print(f"\r{text}", style=style, end="")
        time.sleep(delay)
    console.print(f"\r{text}", style=style_a)
    show_cursor()


def dramatic_pause(seconds: float = 1.0) -> None:
    for _ in range(3):
        console.print(".", end="")
        time.sleep(seconds / 3)
    console.print()