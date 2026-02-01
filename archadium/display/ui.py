"""HUD, health, inventory, and other UI elements."""

from rich.panel import Panel
from rich.table import Table

from archadium.display.console import console


def health_bar(current: int, maximum: int, width: int = 20, label: str = "HP") -> str:
    """Return a colored health bar string using Rich markup."""
    ratio = max(0, min(1, current / maximum)) if maximum > 0 else 1
    filled = int(ratio * width)
    empty = width - filled

    if ratio > 0.6:
        color = "green"
    elif ratio > 0.3:
        color = "yellow"
    else:
        color = "red"

    bar = f"[bold {color}]{'█' * filled}[/][dim]{'░' * empty}[/]"
    return f"[hud.label]{label}:[/] {bar} [hud.value]{current}/{maximum}[/]"


def render_hud(
    player_name: str,
    hp: int,
    max_hp: int,
    level: int,
    gold: int,
    weapon: str = "fists",
    room_name: str = "",
) -> None:
    """Render the game HUD with player stats and room information."""
    hp_bar = health_bar(hp, max_hp)
    lines = [
        f"[hud.label]Name:[/]   [hud.value]{player_name}[/]   [hud.label]Level:[/] [hud.value]{level}[/]",
        hp_bar,
        f"[gold]Gold: {gold}[/]    [hud.label]Weapon:[/] [item.name]{weapon}[/]",
    ]

    title = f" {room_name} " if room_name else " Archadium "
    panel = Panel("\n".join(lines), title=title, border_style="bright_blue", padding=(0, 1))
    console.print(panel)


def inventory_table(items: list[dict]) -> None:
    """Render the inventory as a Rich table.
    
    Each item dict should have: name, item_type, description, and optionally quantity.
    """
    table = Table(title="Inventory", border_style="bright_blue", show_lines=True)
    table.add_column("Item", style="item.name", min_width=15)
    table.add_column("Type", style="info", min_width=10)
    table.add_column("Qty", justify="right", style="hud.value", min_width=4)
    table.add_column("Description", style="item.desc")

    if not items:
        table.add_row("(empty)", "-", "-", "You carry nothing.")
    else:
        for item in items:
            table.add_row(
                item["name"],
                item.get("item_type", "misc"),
                str(item.get("quantity", 1)),
                item.get("description", ""),
            )
    console.print(table)


def choice_menu(prompt_text: str, choices: list[str]) -> int:
    """Display a menu of choices and return the selected index."""
    console.print()
    console.print(f"[dialogue.npc]{prompt_text}[/]")
    for i, choice in enumerate(choices, 1):
        console.print(f"  [dialogue.choice]{i}.[/] {choice}")
    console.print()

    try:
        raw = console.input(f"[prompt]> [/]")
        idx = int(raw.strip()) - 1
        if 0 <= idx < len(choices):
            return idx
    except (ValueError, EOFError):
        pass

    console.print("[error]Invalid choice.[/]")
    return -1


def separator(style: str = "dim cyan") -> None:
    """Display a separator line with a specific style."""
    console.rule(style=style)