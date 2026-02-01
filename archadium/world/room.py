"""Room and Exit dataclasses for the world system."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Exit:
    """A connection from one room to another."""

    direction: str
    target_room: str
    description: str = ""
    locked: bool = False
    required_flag: str | None = None
    lock_message: str = "The way is blocked."

    def is_accessible(self, flags: dict[str, bool]) -> bool:
        if not self.locked:
            return True
        if self.required_flag and flags.get(self.required_flag, False):
            return True
        return False


@dataclass
class Room:
    """A single room/location in the game world."""

    room_id: str
    name: str
    description: str
    exits: list[Exit] = field(default_factory=list)
    items: list[str] = field(default_factory=list)
    enemies: list[str] = field(default_factory=list)
    npcs: list[str] = field(default_factory=list)
    ascii_art: str | None = None
    on_enter_flag: str | None = None
    ambient: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> Room:
        exits = [
            Exit(
                direction=e["direction"],
                target_room=e["target"],
                description=e.get("description", ""),
                locked=e.get("locked", False),
                required_flag=e.get("required_flag"),
                lock_message=e.get("lock_message", "The way is blocked."),
            )
            for e in data.get("exits", [])
        ]
        return cls(
            room_id=data["id"],
            name=data["name"],
            description=data["description"],
            exits=exits,
            items=data.get("items", []),
            enemies=data.get("enemies", []),
            npcs=data.get("npcs", []),
            ascii_art=data.get("ascii_art"),
            on_enter_flag=data.get("on_enter_flag"),
            ambient=data.get("ambient", ""),
        )

    def get_exit(self, direction: str) -> Exit | None:
        for ex in self.exits:
            if ex.direction == direction:
                return ex
        return None

    def exit_directions(self) -> list[str]:
        return [ex.direction for ex in self.exits]
