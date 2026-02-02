"""Combat UI helpers: health bars, battle status display."""

from rich.panel import Panel

from archadium.entities.enemies import Enemy
from archadium.display.console import console
from archadium.display.ui import health_bar


def render_battle_status(
    player_name: str,
    player_hp: int,
    player_max_hp: int,
    enemy: Enemy,
) -> None:
    """Render the combat status panel showing both combatants."""
    player_bar = health_bar(player_hp, player_max_hp, label=player_name)
    enemy_bar = health_bar(enemy.hp, enemy.max_hp, label=enemy.name)

    content = f"{enemy_bar}\n\n{player_bar}"

    panel = Panel(
        content,
        title=" Combat ",
        border_style="bright_red",
        padding=(0, 1),
    )
    console.print(panel)


def render_enemy_art(enemy: Enemy) -> None:
    """Display enemy ASCII art if available."""
    if enemy.ascii_art:
        for line in enemy.ascii_art:
            console.print(line, style="enemy.name")


def show_combat_actions() -> None:
    """Display available combat actions."""
    console.print("[dialogue.choice]1.[/] Attack")
    console.print("[dialogue.choice]2.[/] Defend")
    console.print("[dialogue.choice]3.[/] Use Item")
    console.print("[dialogue.choice]4.[/] Flee")
