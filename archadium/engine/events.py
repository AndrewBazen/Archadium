"""Simple publish/subscribe event bus for decoupling game systems."""

from collections import defaultdict
from typing import Callable, Any

EventHandler = Callable[..., None]


class EventBus:
    """A minimal event bus supporting publish/subscribe pattern."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event: str, handler: EventHandler) -> None:
        """Register a handler for a specific event."""
        self._handlers[event].append(handler)

    def unsubscribe(self, event: str, handler: EventHandler) -> None:
        """Unregister a handler for a specific event."""
        try:
            self._handlers[event].remove(handler)
        except ValueError:
            pass

    def publish(self, event: str, **kwargs: Any) -> None:
        """Fire an event, calling all registered handlers with any provided kwargs."""
        for handler in self._handlers.get(event, []):
            handler(**kwargs)

    def clear(self) -> None:
        """Remove all event handlers."""
        self._handlers.clear()


event_bus = EventBus()