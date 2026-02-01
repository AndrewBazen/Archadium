"""Rich Console singleton with themed styles for Archadium."""

from rich.console import Console
from rich.theme import Theme

ARCHADIUM_THEME = Theme(
    {
        "title": "bold bright_magenta",
        "subtitle": "dim cyan",
        "room.name": "bold bright_yellow",
        "room.desc": "white",
        "room.exit": "cyan",
        "item.name": "bold bright_green",
        "item.desc": "green",
        "item.rare": "bold bright_magenta",
        "enemy.name": "bold bright_red",
        "enemy.desc": "red",
        "damage": "bold red",
        "heal": "bold green",
        "gold": "bold yellow",
        "dialogue.npc": "bold bright_cyan",
        "dialogue.choice": "bright_white",
        "dialogue.flavor": "dim italic",
        "command": "bold white",
        "prompt": "bold bright_yellow",
        "error": "bold red",
        "success": "bold green",
        "info": "dim white",
        "hud.label": "dim cyan",
        "hud.value": "bold white",
    }
)

console = Console(theme=ARCHADIUM_THEME, highlight=False)