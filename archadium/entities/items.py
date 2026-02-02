"""Item dataclass and ItemRegistry for loading items from YAML."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

DATA_DIR = Path(__file__).parent.parent / "data" / "items"


@dataclass
class Item:
    """A game item that can be picked up, equipped, or used."""

    item_id: str
    name: str
    description: str
    item_type: str = "misc"  # weapon, armor, consumable, key, misc
    attack_bonus: int = 0
    defense_bonus: int = 0
    heal_amount: int = 0
    value: int = 0
    attack_type: str | None = None
    stackable: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> Item:
        return cls(
            item_id=data["id"],
            name=data["name"],
            description=data["description"],
            item_type=data.get("type", "misc"),
            attack_bonus=data.get("attack_bonus", 0),
            attack_type=data.get("attack_type"),
            defense_bonus=data.get("defense_bonus", 0),
            heal_amount=data.get("heal_amount", 0),
            value=data.get("value", 0),
            stackable=data.get("stackable", False),
        )

    def to_display_dict(self, quantity: int = 1) -> dict:
        return {
            "name": self.name,
            "item_type": self.item_type,
            "description": self.description,
            "quantity": quantity,
        }


class ItemRegistry:
    """Loads all items from YAML and provides lookup by ID."""

    def __init__(self) -> None:
        self._items: dict[str, Item] = {}

    def load(self) -> None:
        if not DATA_DIR.exists():
            return
        for path in sorted(DATA_DIR.glob("*.yaml")):
            data = yaml.safe_load(path.read_text())
            if isinstance(data, list):
                for item_data in data:
                    item = Item.from_dict(item_data)
                    self._items[item.item_id] = item
            elif isinstance(data, dict) and "items" in data:
                for item_data in data["items"]:
                    item = Item.from_dict(item_data)
                    self._items[item.item_id] = item

    def get(self, item_id: str) -> Item | None:
        return self._items.get(item_id)

    def find_by_name(self, name: str) -> Item | None:
        """Find an item by partial name match (case-insensitive)."""
        name_lower = name.lower()
        for item in self._items.values():
            if name_lower in item.name.lower():
                return item
        return None

    def all_items(self) -> list[Item]:
        return list(self._items.values())
