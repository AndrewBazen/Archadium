"""Enemy dataclass and EnemyRegistry for loading enemies from YAML."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from archadium.display.ascii_art import load_art

import yaml

DATA_DIR = Path(__file__).parent.parent / "data" / "enemies"



@dataclass
class Enemy:
    """An enemy that can be fought in combat."""

    enemy_id: str
    name: str
    description: str
    hp: int
    max_hp: int
    attack: int
    defense: int
    xp_reward: int
    gold_reward: int
    ascii_art: list[str]

    @classmethod
    def from_dict(cls, data: dict) -> Enemy:
        return cls(
            enemy_id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            hp=data.get("hp", 30),
            max_hp=data.get("hp", 30),
            attack=data.get("attack", 8),
            defense=data.get("defense", 2),
            xp_reward=data.get("xp_reward", 10),
            gold_reward=data.get("gold_reward", 5),
            ascii_art=load_art(data['id']),
        )

    def to_display_dict(self) -> dict:
        return {
            "name": self.name,
            "ascii_art": "\n".join(self.ascii_art),
        }


class EnemyRegistry:
    """Loads all enemies from YAML data files."""

    def __init__(self) -> None:
        self._enemies: dict[str, Enemy] = {}

    def load(self) -> None:
        if not DATA_DIR.exists():
            return
        for path in sorted(DATA_DIR.glob("*.yaml")):
            data = yaml.safe_load(path.read_text())
            if isinstance(data, list):
                for enemy_data in data:
                    enemy = Enemy.from_dict(enemy_data)
                    self._enemies[enemy.enemy_id] = enemy
            elif isinstance(data, dict) and "enemies" in data:
                for enemy_data in data["enemies"]:
                    enemy = Enemy.from_dict(enemy_data)
                    self._enemies[enemy.enemy_id] = enemy

    def get(self, enemy_id: str) -> Enemy | None:
        return self._enemies.get(enemy_id)

    def find_by_name(self, name: str) -> Enemy | None:
        """Find an enemy by partial name match (case-insensitive)."""
        name_lower = name.lower()
        for enemy in self._enemies.values():
            if name_lower in enemy.name.lower():
                return enemy
        return None

    def all_enemies(self) -> list[Enemy]:
        return list(self._enemies.values())