"""Turn-based battle system."""

from __future__ import annotations

import random

from archadium.combat.combat_ui import render_battle_status, render_enemy_art, show_combat_actions
from archadium.combat.enemies import Enemy
from archadium.display.console import console
from archadium.display.effects import dramatic_pause, screen_shake, typewriter
from archadium.display.ui import separator
from archadium.engine.events import event_bus
from archadium.engine.state import GameState
from archadium.entities.player import Player


class BattleResult:
    """Outcome of a battle."""

    def __init__(self, victory: bool, fled: bool = False, xp: int = 0, gold: int = 0) -> None:
        self.victory = victory
        self.fled = fled
        self.xp = xp
        self.gold = gold


class Battle:
    """Manages a turn-based combat encounter."""

    def __init__(self, player: Player, enemy: Enemy) -> None:
        self.player = player
        self.state = player.state
        self.enemy = enemy
        self.defending = False
        self.turn_count = 0

    def run(self) -> BattleResult:
        """Run the full battle loop and return the result."""
        console.print()
        separator(style="bright_red")
        typewriter(f"A {self.enemy.name} appears!", style="enemy.name")
        if self.enemy.description:
            console.print(f"[enemy.desc]{self.enemy.description}[/]")
        render_enemy_art(self.enemy)
        console.print()

        event_bus.publish("battle_start", enemy=self.enemy)

        while self.state.is_alive and self.enemy.is_alive:
            self.turn_count += 1
            render_battle_status(
                self.player.name,
                self.state.hp,
                self.state.max_hp,
                self.enemy,
            )

            # Player turn
            result = self._player_turn()
            if result is not None:
                return result

            if not self.enemy.is_alive:
                break

            # Enemy turn
            self._enemy_turn()

        if not self.state.is_alive:
            return self._defeat()

        return self._victory()

    def _player_turn(self) -> BattleResult | None:
        """Handle player's turn. Returns BattleResult if battle ends, else None."""
        self.defending = False
        show_combat_actions()
        console.print()

        while True:
            try:
                raw = console.input("[prompt]Combat> [/]").strip()
            except EOFError:
                raw = "4"

            if raw in ("1", "attack"):
                self._do_attack()
                return None
            elif raw in ("2", "defend"):
                self._do_defend()
                return None
            elif raw in ("3", "use", "item"):
                if self._do_use_item():
                    return None
                continue
            elif raw in ("4", "flee", "run"):
                fled = self._do_flee()
                if fled:
                    return BattleResult(victory=False, fled=True)
                return None
            else:
                console.print("[error]Choose 1-4.[/]")

    def _do_attack(self) -> None:
        damage = self.enemy.take_damage(self.player.effective_attack)
        screen_shake(f"You strike the {self.enemy.name} for {damage} damage!", style="damage")
        event_bus.publish("player_attack", damage=damage, enemy=self.enemy)

    def _do_defend(self) -> None:
        self.defending = True
        console.print("[info]You brace yourself for the next attack.[/]")

    def _do_use_item(self) -> bool:
        """Try to use a consumable. Returns True if an item was used."""
        consumables = [
            item_id
            for item_id in self.state.inventory
            if (item := self.player.registry.get(item_id)) and item.item_type == "consumable"
        ]
        if not consumables:
            console.print("[info]You have no usable items.[/]")
            return False

        console.print("[info]Consumables:[/]")
        seen: dict[str, str] = {}
        for item_id in consumables:
            if item_id not in seen:
                item = self.player.registry.get(item_id)
                if item:
                    seen[item_id] = item.name

        options = list(seen.items())
        for i, (_, name) in enumerate(options, 1):
            console.print(f"  [dialogue.choice]{i}.[/] {name}")
        console.print(f"  [dialogue.choice]0.[/] Cancel")

        try:
            choice = int(console.input("[prompt]> [/]").strip())
        except (ValueError, EOFError):
            return False

        if choice == 0 or choice < 1 or choice > len(options):
            return False

        item_id = options[choice - 1][0]
        msg = self.player.use_item(item_id)
        console.print(f"[heal]{msg}[/]")
        return True

    def _do_flee(self) -> bool:
        chance = 0.5 + (self.turn_count * 0.05)
        if random.random() < chance:
            console.print("[info]You flee from battle![/]")
            event_bus.publish("battle_flee", enemy=self.enemy)
            return True
        console.print("[error]You failed to escape![/]")
        return False

    def _enemy_turn(self) -> None:
        """Handle the enemy's turn."""
        base_damage = self.enemy.attack
        if self.defending:
            base_damage = base_damage // 2

        actual = self.state.take_damage(base_damage)
        screen_shake(
            f"The {self.enemy.name} attacks you for {actual} damage!",
            style="damage",
        )
        event_bus.publish("enemy_attack", damage=actual, enemy=self.enemy)

    def _victory(self) -> BattleResult:
        console.print()
        separator(style="bright_green")
        typewriter(f"You defeated the {self.enemy.name}!", style="success")

        xp = self.enemy.xp_reward
        gold = self.enemy.gold_reward
        self.state.gold += gold

        leveled = self.state.add_xp(xp)
        console.print(f"[gold]+{gold} gold[/]  [info]+{xp} XP[/]")
        if leveled:
            console.print(f"[success]Level up! You are now level {self.state.level}![/]")

        self.state.defeated_enemies.append(self.enemy.enemy_id)
        self.state.set_flag(f"defeated_{self.enemy.enemy_id}")
        event_bus.publish("battle_victory", enemy=self.enemy, xp=xp, gold=gold)
        separator(style="bright_green")

        return BattleResult(victory=True, xp=xp, gold=gold)

    def _defeat(self) -> BattleResult:
        console.print()
        separator(style="bright_red")
        typewriter("You have been defeated...", style="error")
        dramatic_pause(1.5)
        event_bus.publish("battle_defeat", enemy=self.enemy)
        return BattleResult(victory=False)
