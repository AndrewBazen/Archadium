"""Enemy dataclass and loader from YAML."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

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
    xp_reward: int = 10
    gold_reward: int = 5
    ascii_art: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> Enemy:
        hp = data.get("hp", 30)
        return cls(
            enemy_id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            hp=hp,
            max_hp=hp,
            attack=data.get("attack", 8),
            defense=data.get("defense", 2),
            xp_reward=data.get("xp_reward", 10),
            gold_reward=data.get("gold_reward", 5),
            ascii_art=data.get("ascii_art"),
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
                for entry in data:
                    enemy = Enemy.from_dict(entry)
                    self._enemies[enemy.enemy_id] = enemy
            elif isinstance(data, dict) and "enemies" in data:
                for entry in data["enemies"]:
                    enemy = Enemy.from_dict(entry)
                    self._enemies[enemy.enemy_id] = enemy

    def get(self, enemy_id: str) -> Enemy | None:
        template = self._enemies.get(enemy_id)
        if template:
            return template.copy()
        return None
