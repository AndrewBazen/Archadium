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

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> int:
        actual = max(1, amount - self.defense)
        self.hp = max(0, self.hp - actual)
        return actual

    def copy(self) -> Enemy:
        """Return a fresh copy for spawning."""
        return Enemy(
            enemy_id=self.enemy_id,
            name=self.name,
            description=self.description,
            hp=self.max_hp,
            max_hp=self.max_hp,
            attack=self.attack,
            defense=self.defense,
            xp_reward=self.xp_reward,
            gold_reward=self.gold_reward,
            ascii_art=self.ascii_art,
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
        template = self._enemies.get(enemy_id)
        if template:
            return template.copy()
        return None

    def find_by_name(self, name: str) -> Enemy | None:
        """Find an enemy by partial name match (case-insensitive)."""
        name_lower = name.lower()
        for enemy in self._enemies.values():
            if name_lower in enemy.name.lower():
                return enemy
        return None

    def all_enemies(self) -> list[Enemy]:
        return list(self._enemies.values())
