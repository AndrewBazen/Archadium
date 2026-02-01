"""ASCII art loader and renderer."""

from pathlib import Path

from archadium.display.console import console
from archadium.display.effects import fade_in_lines

DATA_DIR = Path(__file__).parent.parent / "data" / "ascii"


def load_art(name: str) -> list[str]:
    """Load ASCII art file by name from the data directory and returns its lines."""
    path = DATA_DIR / f"{name}.txt"
    if not path.exists():
        return [f"[art not found: {name}]"]
    return path.read_text().splitlines()
    

def render_art(name: str, style: str = "title", animate: bool = True, delay: float = 0.06) -> None:
    """Render ASCII art lines with a specific style."""
    lines = load_art(name)
    if animate:
        fade_in_lines(lines, delay=delay, style=style)
    else:
        for line in lines:
            console.print(line, style=style)
