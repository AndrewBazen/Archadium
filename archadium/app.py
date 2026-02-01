"""Main application entry point — initializes registries, scenes, and runs the game loop."""

from __future__ import annotations

from archadium.combat.battle import Battle
from archadium.combat.enemies import EnemyRegistry
from archadium.display.ansi import clear_screen
from archadium.display.ascii_art import render_art
from archadium.display.console import console
from archadium.display.effects import dramatic_pause, typewriter
from archadium.display.ui import (
    choice_menu,
    inventory_table,
    render_hud,
    separator,
)
from archadium.engine.commands import ParsedCommand, parse_input
from archadium.engine.game_loop import GameLoop
from archadium.engine.state import GameState
from archadium.entities.items import ItemRegistry
from archadium.entities.player import Player
from archadium.world.world_map import WorldMap


# ---------------------------------------------------------------------------
# Shared game context passed to all scenes
# ---------------------------------------------------------------------------

class GameContext:
    """Holds shared state and registries used across all scenes."""

    def __init__(self) -> None:
        self.items = ItemRegistry()
        self.enemies = EnemyRegistry()
        self.world = WorldMap()
        self.state = GameState()
        self.player = Player(self.state, self.items)
        self.pending_enemy_id: str | None = None

    def load_data(self) -> None:
        self.items.load()
        self.enemies.load()
        self.world.load()


# ---------------------------------------------------------------------------
# Title scene
# ---------------------------------------------------------------------------

class TitleScene:
    """Splash screen with new game / load / quit options."""

    def __init__(self, ctx: GameContext) -> None:
        self.ctx = ctx

    def enter(self) -> None:
        clear_screen()
        render_art("title", style="title", animate=True)
        console.print()
        console.print("[subtitle]A text adventure awaits...[/]")
        console.print()

    def update(self) -> str | None:
        choices = ["New Game", "Load Game", "Quit"]
        idx = choice_menu("What would you like to do?", choices)

        if idx == 0:
            return self._new_game()
        elif idx == 1:
            return self._load_game()
        elif idx == 2:
            return "quit"
        return None

    def _new_game(self) -> str:
        console.print()
        try:
            name = console.input("[prompt]Enter your name: [/]").strip()
        except EOFError:
            name = ""
        if not name:
            name = "Hero"
        self.ctx.state = GameState(player_name=name)
        self.ctx.player = Player(self.ctx.state, self.ctx.items)
        console.print(f"\n[success]Welcome, {name}. Your adventure begins...[/]")
        dramatic_pause(1.0)
        return "explore"

    def _load_game(self) -> str | None:
        loaded = GameState.load()
        if loaded is None:
            console.print("[error]No save file found.[/]")
            return None
        self.ctx.state = loaded
        self.ctx.player = Player(self.ctx.state, self.ctx.items)
        console.print(f"[success]Welcome back, {loaded.player_name}.[/]")
        dramatic_pause(0.8)
        return "explore"


# ---------------------------------------------------------------------------
# Exploration scene
# ---------------------------------------------------------------------------

class ExploreScene:
    """Main gameplay loop — moving, looking, items, and triggering combat."""

    def __init__(self, ctx: GameContext) -> None:
        self.ctx = ctx
        self._looked = False

    def enter(self) -> None:
        clear_screen()
        self._looked = False
        self._do_look()

    def update(self) -> str | None:
        room = self.ctx.world.get_room(self.ctx.state.current_room)
        if room is None:
            console.print(f"[error]Room '{self.ctx.state.current_room}' not found.[/]")
            return "title"

        # Check for enemies in room on first visit
        if not self._looked:
            self._do_look()

        console.print()
        try:
            raw = console.input("[prompt]> [/]").strip()
        except EOFError:
            return "quit"

        if not raw:
            return None

        cmd = parse_input(raw)
        return self._handle(cmd)

    # -- command dispatch ---------------------------------------------------

    def _handle(self, cmd: ParsedCommand) -> str | None:
        handlers = {
            "look": self._cmd_look,
            "move": self._cmd_move,
            "take": self._cmd_take,
            "drop": self._cmd_drop,
            "examine": self._cmd_examine,
            "inventory": self._cmd_inventory,
            "equip": self._cmd_equip,
            "unequip": self._cmd_unequip,
            "use": self._cmd_use,
            "stats": self._cmd_stats,
            "attack": self._cmd_attack,
            "talk": self._cmd_talk,
            "save": self._cmd_save,
            "load": self._cmd_load,
            "help": self._cmd_help,
            "quit": self._cmd_quit,
        }
        handler = handlers.get(cmd.verb)
        if handler is None:
            console.print("[error]Unknown command. Type 'help' for a list of commands.[/]")
            return None
        return handler(cmd)

    # -- look ---------------------------------------------------------------

    def _do_look(self) -> None:
        room = self.ctx.world.get_room(self.ctx.state.current_room)
        if room is None:
            return

        if room.on_enter_flag:
            self.ctx.state.set_flag(room.on_enter_flag)

        separator()
        render_hud(
            player_name=self.ctx.player.name,
            hp=self.ctx.state.hp,
            max_hp=self.ctx.state.max_hp,
            level=self.ctx.state.level,
            gold=self.ctx.state.gold,
            weapon=self.ctx.player.weapon_name,
            room_name=room.name,
        )
        console.print()
        console.print(f"[room.desc]{room.description}[/]")

        if room.ambient:
            console.print(f"[dialogue.flavor]{room.ambient}[/]")

        # Items on the ground
        if room.items:
            console.print()
            for item_id in room.items:
                item = self.ctx.items.get(item_id)
                name = item.name if item else item_id
                console.print(f"  [item.name]{name}[/] is here.")

        # Enemies present
        alive_enemies = [
            eid for eid in room.enemies
            if eid not in self.ctx.state.defeated_enemies
        ]
        if alive_enemies:
            console.print()
            for eid in alive_enemies:
                template = self.ctx.enemies.get(eid)
                name = template.name if template else eid
                console.print(f"  [enemy.name]{name}[/] lurks here.")

        # NPCs
        if room.npcs:
            console.print()
            for npc in room.npcs:
                console.print(f"  [dialogue.npc]{npc}[/] is here.")

        # Exits
        exits = []
        for ex in room.exits:
            accessible = ex.is_accessible(self.ctx.state.flags)
            tag = "" if accessible else " [dim](locked)[/]"
            desc = f" — {ex.description}" if ex.description else ""
            exits.append(f"[room.exit]{ex.direction}[/]{desc}{tag}")

        if exits:
            console.print()
            console.print("[hud.label]Exits:[/] " + ", ".join(exits))

        self._looked = True

    def _cmd_look(self, cmd: ParsedCommand) -> None:
        self._do_look()

    # -- movement -----------------------------------------------------------

    def _cmd_move(self, cmd: ParsedCommand) -> str | None:
        if not cmd.args:
            console.print("[error]Move where? Specify a direction.[/]")
            return None

        direction = cmd.args[0]
        room = self.ctx.world.get_room(self.ctx.state.current_room)
        if room is None:
            return None

        exit_obj = room.get_exit(direction)
        if exit_obj is None:
            console.print(f"[error]You can't go {direction}.[/]")
            return None

        if not exit_obj.is_accessible(self.ctx.state.flags):
            console.print(f"[error]{exit_obj.lock_message}[/]")
            return None

        self.ctx.state.current_room = exit_obj.target_room
        self._looked = False
        clear_screen()
        self._do_look()

        # Auto-trigger combat if room has alive enemies
        new_room = self.ctx.world.get_room(self.ctx.state.current_room)
        if new_room:
            alive = [
                eid for eid in new_room.enemies
                if eid not in self.ctx.state.defeated_enemies
            ]
            if alive:
                self.ctx.pending_enemy_id = alive[0]
                return "combat"

        return None

    # -- items --------------------------------------------------------------

    def _cmd_take(self, cmd: ParsedCommand) -> None:
        if not cmd.args:
            console.print("[error]Take what?[/]")
            return

        room = self.ctx.world.get_room(self.ctx.state.current_room)
        if room is None:
            return

        target = cmd.arg_text
        for item_id in list(room.items):
            item = self.ctx.items.get(item_id)
            if item and target in item.name.lower():
                room.items.remove(item_id)
                self.ctx.player.add_item(item_id)
                console.print(f"[success]You pick up the {item.name}.[/]")
                return

        console.print("[error]You don't see that here.[/]")

    def _cmd_drop(self, cmd: ParsedCommand) -> None:
        if not cmd.args:
            console.print("[error]Drop what?[/]")
            return

        room = self.ctx.world.get_room(self.ctx.state.current_room)
        if room is None:
            return

        target = cmd.arg_text
        for item_id in list(self.ctx.state.inventory):
            item = self.ctx.items.get(item_id)
            if item and target in item.name.lower():
                self.ctx.player.remove_item(item_id)
                room.items.append(item_id)
                console.print(f"[info]You drop the {item.name}.[/]")
                return

        console.print("[error]You don't have that.[/]")

    def _cmd_examine(self, cmd: ParsedCommand) -> None:
        if not cmd.args:
            console.print("[error]Examine what?[/]")
            return

        target = cmd.arg_text

        # Check inventory first
        for item_id in self.ctx.state.inventory:
            item = self.ctx.items.get(item_id)
            if item and target in item.name.lower():
                console.print(f"[item.name]{item.name}[/] — [item.desc]{item.description}[/]")
                if item.attack_bonus:
                    console.print(f"  [hud.label]Attack bonus:[/] +{item.attack_bonus}")
                if item.defense_bonus:
                    console.print(f"  [hud.label]Defense bonus:[/] +{item.defense_bonus}")
                if item.heal_amount:
                    console.print(f"  [hud.label]Heals:[/] {item.heal_amount} HP")
                if item.value:
                    console.print(f"  [gold]Value: {item.value} gold[/]")
                return

        # Check room items
        room = self.ctx.world.get_room(self.ctx.state.current_room)
        if room:
            for item_id in room.items:
                item = self.ctx.items.get(item_id)
                if item and target in item.name.lower():
                    console.print(f"[item.name]{item.name}[/] — [item.desc]{item.description}[/]")
                    return

        console.print("[error]You don't see that here.[/]")

    def _cmd_inventory(self, cmd: ParsedCommand) -> None:
        items = self.ctx.player.inventory_display()
        inventory_table(items)

    def _cmd_equip(self, cmd: ParsedCommand) -> None:
        if not cmd.args:
            console.print("[error]Equip what?[/]")
            return

        target = cmd.arg_text
        for item_id in self.ctx.state.inventory:
            item = self.ctx.items.get(item_id)
            if item and target in item.name.lower():
                err = self.ctx.player.equip(item_id)
                if err:
                    console.print(f"[error]{err}[/]")
                else:
                    console.print(f"[success]You equip the {item.name}.[/]")
                return

        console.print("[error]You don't have that.[/]")

    def _cmd_unequip(self, cmd: ParsedCommand) -> None:
        target = cmd.arg_text if cmd.args else ""
        if target in ("weapon", "armor"):
            err = self.ctx.player.unequip(target)
            if err:
                console.print(f"[error]{err}[/]")
            else:
                console.print(f"[success]You unequip your {target}.[/]")
        else:
            console.print("[info]Specify 'weapon' or 'armor' to unequip.[/]")

    def _cmd_use(self, cmd: ParsedCommand) -> None:
        if not cmd.args:
            console.print("[error]Use what?[/]")
            return

        target = cmd.arg_text
        for item_id in self.ctx.state.inventory:
            item = self.ctx.items.get(item_id)
            if item and target in item.name.lower():
                msg = self.ctx.player.use_item(item_id)
                console.print(f"[info]{msg}[/]")
                return

        console.print("[error]You don't have that.[/]")

    # -- info ---------------------------------------------------------------

    def _cmd_stats(self, cmd: ParsedCommand) -> None:
        s = self.ctx.state
        p = self.ctx.player
        separator()
        console.print(f"[hud.label]Name:[/]    [hud.value]{s.player_name}[/]")
        console.print(f"[hud.label]Level:[/]   [hud.value]{s.level}[/]")
        console.print(f"[hud.label]XP:[/]      [hud.value]{s.xp}/{s.xp_to_level}[/]")
        console.print(f"[hud.label]HP:[/]      [hud.value]{s.hp}/{s.max_hp}[/]")
        console.print(f"[hud.label]Attack:[/]  [hud.value]{p.effective_attack}[/]")
        console.print(f"[hud.label]Defense:[/] [hud.value]{p.effective_defense}[/]")
        console.print(f"[gold]Gold: {s.gold}[/]")
        console.print(f"[hud.label]Weapon:[/]  [item.name]{p.weapon_name}[/]")
        separator()

    def _cmd_help(self, cmd: ParsedCommand) -> None:
        console.print()
        console.print("[title]Commands[/]")
        console.print("  [command]look[/]            — Examine your surroundings")
        console.print("  [command]north/south/...[/] — Move in a direction")
        console.print("  [command]take[/] [info]<item>[/]    — Pick up an item")
        console.print("  [command]drop[/] [info]<item>[/]    — Drop an item")
        console.print("  [command]examine[/] [info]<item>[/] — Inspect an item closely")
        console.print("  [command]use[/] [info]<item>[/]     — Use a consumable item")
        console.print("  [command]equip[/] [info]<item>[/]   — Equip a weapon or armor")
        console.print("  [command]unequip[/] [info]weapon/armor[/] — Unequip a slot")
        console.print("  [command]inventory[/]       — View your inventory")
        console.print("  [command]stats[/]           — View your stats")
        console.print("  [command]attack[/]          — Fight an enemy in the room")
        console.print("  [command]talk[/] [info]<npc>[/]     — Talk to someone")
        console.print("  [command]save[/]            — Save your game")
        console.print("  [command]load[/]            — Load your game")
        console.print("  [command]quit[/]            — Exit the game")
        console.print()

    # -- combat -------------------------------------------------------------

    def _cmd_attack(self, cmd: ParsedCommand) -> str | None:
        room = self.ctx.world.get_room(self.ctx.state.current_room)
        if room is None:
            return None

        alive = [
            eid for eid in room.enemies
            if eid not in self.ctx.state.defeated_enemies
        ]
        if not alive:
            console.print("[info]There's nothing to fight here.[/]")
            return None

        self.ctx.pending_enemy_id = alive[0]
        return "combat"

    # -- talk (stub — no NPC system yet) ------------------------------------

    def _cmd_talk(self, cmd: ParsedCommand) -> None:
        room = self.ctx.world.get_room(self.ctx.state.current_room)
        if room and room.npcs:
            target = cmd.arg_text if cmd.args else ""
            for npc in room.npcs:
                if not target or target in npc.lower():
                    console.print(f"[dialogue.npc]{npc}[/] has nothing to say... yet.")
                    return
            console.print("[error]You don't see them here.[/]")
        else:
            console.print("[info]There's no one to talk to here.[/]")

    # -- save / load --------------------------------------------------------

    def _cmd_save(self, cmd: ParsedCommand) -> None:
        path = self.ctx.state.save()
        console.print(f"[success]Game saved.[/]")

    def _cmd_load(self, cmd: ParsedCommand) -> str | None:
        loaded = GameState.load()
        if loaded is None:
            console.print("[error]No save file found.[/]")
            return None
        self.ctx.state = loaded
        self.ctx.player = Player(self.ctx.state, self.ctx.items)
        console.print(f"[success]Game loaded.[/]")
        self._looked = False
        clear_screen()
        self._do_look()
        return None

    # -- quit ---------------------------------------------------------------

    def _cmd_quit(self, cmd: ParsedCommand) -> str:
        return "quit"


# ---------------------------------------------------------------------------
# Combat scene
# ---------------------------------------------------------------------------

class CombatScene:
    """Wraps the Battle system as a scene in the game loop."""

    def __init__(self, ctx: GameContext) -> None:
        self.ctx = ctx

    def enter(self) -> None:
        pass

    def update(self) -> str | None:
        enemy_id = self.ctx.pending_enemy_id
        self.ctx.pending_enemy_id = None

        if enemy_id is None:
            return "explore"

        enemy = self.ctx.enemies.get(enemy_id)
        if enemy is None:
            console.print(f"[error]Unknown enemy: {enemy_id}[/]")
            return "explore"

        battle = Battle(self.ctx.player, enemy)
        result = battle.run()
        console.print()

        if result.victory:
            return "explore"
        elif result.fled:
            console.print("[info]You retreat to safety.[/]")
            return "explore"
        else:
            return "death"


# ---------------------------------------------------------------------------
# Death scene
# ---------------------------------------------------------------------------

class DeathScene:
    """Game over screen."""

    def __init__(self, ctx: GameContext) -> None:
        self.ctx = ctx

    def enter(self) -> None:
        clear_screen()
        console.print()
        typewriter("You have fallen...", style="error")
        console.print()
        render_art("death", style="error", animate=True)
        console.print()

    def update(self) -> str | None:
        choices = ["Load Save", "New Game", "Quit"]
        idx = choice_menu("What would you like to do?", choices)

        if idx == 0:
            loaded = GameState.load()
            if loaded is None:
                console.print("[error]No save file found.[/]")
                return None
            self.ctx.state = loaded
            self.ctx.player = Player(self.ctx.state, self.ctx.items)
            return "explore"
        elif idx == 1:
            return "title"
        elif idx == 2:
            return "quit"
        return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Initialize the game and run the main loop."""
    ctx = GameContext()
    ctx.load_data()

    loop = GameLoop()
    loop.register("title", TitleScene(ctx))
    loop.register("explore", ExploreScene(ctx))
    loop.register("combat", CombatScene(ctx))
    loop.register("death", DeathScene(ctx))

    try:
        loop.run("title")
    except KeyboardInterrupt:
        pass
    finally:
        console.print("\n[subtitle]Thanks for playing Archadium![/]")
