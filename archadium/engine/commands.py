"""Input parsing with command aliases and argument extraction."""

from dataclasses import dataclass

ALIASES: dict[str, str] = {
    # Movement
    "n": "north",
    "s": "south",
    "e": "east",
    "w": "west",
    "u": "up",
    "d": "down",
    "go": "move",
    "walk": "move",
    "move": "move",
    # Exploration
    "l": "look",
    "look": "look",
    "examine": "examine",
    "x": "examine",
    "inspect": "examine",
    "search": "examine",
    # Items
    "get": "take",
    "grab": "take",
    "pick": "take",
    "take": "take",
    "drop": "drop",
    "use": "use",
    "drink": "use",
    "eat": "use",
    "equip": "equip",
    "wear": "equip",
    "wield": "equip",
    "unequip": "unequip",
    "remove": "unequip",
    "i": "inventory",
    "inv": "inventory",
    "inventory": "inventory",
    # Interaction
    "talk": "talk",
    "speak": "talk",
    "chat": "talk",
    # Combat
    "attack": "attack",
    "fight": "attack",
    "hit": "attack",
    "flee": "flee",
    "run": "flee",
    "defend": "defend",
    "block": "defend",
    # System
    "help": "help",
    "h": "help",
    "?": "help",
    "quit": "quit",
    "exit": "quit",
    "q": "quit",
    "save": "save",
    "load": "load",
    "stats": "stats",
    "status": "stats",
}

DIRECTIONS: set[str] = {"north", "south", "east", "west", "up", "down"}


@dataclass
class ParsedCommand:
    """A parsed player command with canonical verb and arguments."""

    verb: str
    args: list[str]
    raw: str

    @property
    def arg_text(self) -> str:
        """The arguments joined as a single string."""
        return " ".join(self.args)


def parse_input(raw: str) -> ParsedCommand:
    """Parse a raw input string into a ParsedCommand."""
    raw = raw.strip()
    if not raw:
        return ParsedCommand(verb="", args=[], raw=raw)

    parts = raw.lower().split()
    first = parts[0]
    rest = parts[1:]

    canonical = ALIASES.get(first, first)

    # Directions become move commands
    if canonical in DIRECTIONS:
        return ParsedCommand(verb="move", args=[canonical], raw=raw)

    # "pick up sword" -> "take sword"
    if first == "pick" and rest and rest[0] == "up":
        rest = rest[1:]
        canonical = "take"

    return ParsedCommand(verb=canonical, args=rest, raw=raw)