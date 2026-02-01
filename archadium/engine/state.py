"""GameState dataclass with save/load functionality."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

SAVE_DIR = Path(__file__).parent.parent / "saves"


@dataclass
class GameState:
    """Central game state tracking the player's progress."""

    player_name: str = "Hero"
    current_room: str = "village_square"
    hp: int = 100
    max_hp: int = 100
    attack: int = 10
    defense: int = 5
    level: int = 1
    xp: int = 0
    xp_to_level: int = 100
    gold: int = 0
    inventory: list[str] = field(default_factory=list)
    equipped_weapon: str | None = None
    equipped_armor: str | None = None
    flags: dict[str, bool] = field(default_factory=dict)
    defeated_enemies: list[str] = field(default_factory=list)

    def set_flag(self, flag: str, value: bool = True) -> None:
        self.flags[flag] = value

    def has_flag(self, flag: str) -> bool:
        return self.flags.get(flag, False)

    def add_xp(self, amount: int) -> bool:
        """Add XP and return True if the player leveled up."""
        self.xp += amount
        if self.xp >= self.xp_to_level:
            self.xp -= self.xp_to_level
            self.level += 1
            self.xp_to_level = int(self.xp_to_level * 1.5)
            self.max_hp += 10
            self.hp = self.max_hp
            self.attack += 2
            self.defense += 1
            return True
        return False

    def heal(self, amount: int) -> int:
        """Heal the player and return the actual amount healed."""
        before = self.hp
        self.hp = min(self.hp + amount, self.max_hp)
        return self.hp - before

    def take_damage(self, amount: int) -> int:
        """Apply damage after defense and return actual damage taken."""
        actual = max(1, amount - self.defense)
        self.hp = max(0, self.hp - actual)
        return actual

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def to_dict(self) -> dict:
        return {
            "player_name": self.player_name,
            "current_room": self.current_room,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "attack": self.attack,
            "defense": self.defense,
            "level": self.level,
            "xp": self.xp,
            "xp_to_level": self.xp_to_level,
            "gold": self.gold,
            "inventory": self.inventory,
            "equipped_weapon": self.equipped_weapon,
            "equipped_armor": self.equipped_armor,
            "flags": self.flags,
            "defeated_enemies": self.defeated_enemies,
        }

    @classmethod
    def from_dict(cls, data: dict) -> GameState:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def save(self, slot: str = "save1") -> Path:
        """Save game state to a JSON file."""
        SAVE_DIR.mkdir(parents=True, exist_ok=True)
        path = SAVE_DIR / f"{slot}.json"
        path.write_text(json.dumps(self.to_dict(), indent=2))
        return path

    @classmethod
    def load(cls, slot: str = "save1") -> GameState | None:
        """Load game state from a JSON file. Returns None if not found."""
        path = SAVE_DIR / f"{slot}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        return cls.from_dict(data)
