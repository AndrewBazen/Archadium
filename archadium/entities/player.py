"""Player class wrapping GameState with equipment and inventory management."""

from __future__ import annotations

from archadium.engine.state import GameState
from archadium.entities.items import Item, ItemRegistry


class Player:
    """High-level player interface over GameState with item operations."""

    def __init__(self, state: GameState, item_registry: ItemRegistry) -> None:
        self.state = state
        self.registry = item_registry

    @property
    def name(self) -> str:
        return self.state.player_name

    @property
    def hp(self) -> int:
        return self.state.hp

    @property
    def max_hp(self) -> int:
        return self.state.max_hp

    @property
    def effective_attack(self) -> int:
        bonus = 0
        if self.state.equipped_weapon:
            weapon = self.registry.get(self.state.equipped_weapon)
            if weapon:
                bonus = weapon.attack_bonus
        return self.state.attack + bonus

    @property
    def effective_defense(self) -> int:
        bonus = 0
        if self.state.equipped_armor:
            armor = self.registry.get(self.state.equipped_armor)
            if armor:
                bonus = armor.defense_bonus
        return self.state.defense + bonus

    @property
    def weapon_name(self) -> str:
        if self.state.equipped_weapon:
            weapon = self.registry.get(self.state.equipped_weapon)
            if weapon:
                return weapon.name
        return "Fists"

    def add_item(self, item_id: str) -> Item | None:
        """Add an item to inventory. Returns the Item or None if not found."""
        item = self.registry.get(item_id)
        if item is None:
            return None
        self.state.inventory.append(item_id)
        return item

    def remove_item(self, item_id: str) -> bool:
        """Remove one instance of an item from inventory."""
        if item_id in self.state.inventory:
            self.state.inventory.remove(item_id)
            return True
        return False

    def has_item(self, item_id: str) -> bool:
        return item_id in self.state.inventory

    def equip(self, item_id: str) -> str | None:
        """Equip an item. Returns an error message or None on success."""
        if item_id not in self.state.inventory:
            return "You don't have that item."
        item = self.registry.get(item_id)
        if item is None:
            return "Unknown item."
        if item.item_type == "weapon":
            self.state.equipped_weapon = item_id
            return None
        elif item.item_type == "armor":
            self.state.equipped_armor = item_id
            return None
        return f"{item.name} can't be equipped."

    def unequip(self, slot: str) -> str | None:
        """Unequip weapon or armor. Returns error message or None."""
        if slot == "weapon":
            if self.state.equipped_weapon is None:
                return "Nothing equipped in weapon slot."
            self.state.equipped_weapon = None
            return None
        elif slot == "armor":
            if self.state.equipped_armor is None:
                return "Nothing equipped in armor slot."
            self.state.equipped_armor = None
            return None
        return "Unknown slot. Use 'weapon' or 'armor'."

    def use_item(self, item_id: str) -> str:
        """Use a consumable item. Returns a result message."""
        if item_id not in self.state.inventory:
            return "You don't have that item."
        item = self.registry.get(item_id)
        if item is None:
            return "Unknown item."
        if item.item_type != "consumable":
            return f"{item.name} can't be used that way."
        self.state.inventory.remove(item_id)
        if item.heal_amount > 0:
            healed = self.state.heal(item.heal_amount)
            return f"You use {item.name} and recover {healed} HP!"
        return f"You use {item.name}."

    def inventory_display(self) -> list[dict]:
        """Build inventory data for display, grouping stackable items."""
        counts: dict[str, int] = {}
        for item_id in self.state.inventory:
            counts[item_id] = counts.get(item_id, 0) + 1

        result = []
        for item_id, qty in counts.items():
            item = self.registry.get(item_id)
            if item:
                entry = item.to_display_dict(qty)
                if item_id == self.state.equipped_weapon:
                    entry["name"] += " [E]"
                if item_id == self.state.equipped_armor:
                    entry["name"] += " [E]"
                result.append(entry)
        return result
