"""WorldMap: loads all rooms from YAML and provides lookup."""

from __future__ import annotations

from pathlib import Path

import yaml

from archadium.world.room import Room

DATA_DIR = Path(__file__).parent.parent / "data" / "rooms"


class WorldMap:
    """Registry of all rooms in the game, loaded from YAML files."""

    def __init__(self) -> None:
        self._rooms: dict[str, Room] = {}

    def load(self) -> None:
        """Load all room YAML files from the data directory."""
        if not DATA_DIR.exists():
            return
        for path in sorted(DATA_DIR.glob("*.yaml")):
            data = yaml.safe_load(path.read_text())
            if isinstance(data, list):
                for room_data in data:
                    room = Room.from_dict(room_data)
                    self._rooms[room.room_id] = room
            elif isinstance(data, dict):
                if "rooms" in data:
                    for room_data in data["rooms"]:
                        room = Room.from_dict(room_data)
                        self._rooms[room.room_id] = room
                else:
                    room = Room.from_dict(data)
                    self._rooms[room.room_id] = room

    def get_room(self, room_id: str) -> Room | None:
        return self._rooms.get(room_id)

    def all_rooms(self) -> list[Room]:
        return list(self._rooms.values())

    @property
    def room_count(self) -> int:
        return len(self._rooms)
