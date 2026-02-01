"""Game loop state machine with Scene protocol.

The game cycles through scenes (title, exploration, combat) where each scene
handles its own input/rendering and returns the next scene to transition to.
"""

from __future__ import annotations

from typing import Protocol

from archadium.display.console import console


class Scene(Protocol):
    """Protocol for game scenes. Each scene handles one game mode."""

    def enter(self) -> None:
        """Called when transitioning into this scene."""
        ...

    def update(self) -> str | None:
        """Run one tick of the scene.

        Returns:
            A scene name to transition to, or None to stay in this scene.
            Return "quit" to exit the game.
        """
        ...


class GameLoop:
    """Main game loop that dispatches to the active scene."""

    def __init__(self) -> None:
        self._scenes: dict[str, Scene] = {}
        self._current: str = ""

    def register(self, name: str, scene: Scene) -> None:
        self._scenes[name] = scene

    def set_scene(self, name: str) -> None:
        if name not in self._scenes:
            console.print(f"[error]Unknown scene: {name}[/]")
            return
        self._current = name
        self._scenes[name].enter()

    def run(self, start_scene: str) -> None:
        """Run the game loop starting from the given scene."""
        self.set_scene(start_scene)

        while True:
            scene = self._scenes.get(self._current)
            if scene is None:
                break

            try:
                next_scene = scene.update()
            except KeyboardInterrupt:
                console.print("\n[info]Use 'quit' to exit the game.[/]")
                continue
            except EOFError:
                break

            if next_scene == "quit":
                break
            elif next_scene is not None:
                self.set_scene(next_scene)
