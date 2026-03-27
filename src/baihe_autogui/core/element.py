import time
from typing import Any, Optional

from .exceptions import ElementNotFoundError, ElementTimeoutError, ValidationError
from .gui import gui
from .target import Point, Target


class Element:
    def __init__(
        self,
        target: Target,
        auto: Any = None,
        cached_point: Optional[Point] = None,
    ):
        self._target = target
        self._required = True
        self._cached_point = cached_point

    def _exists(self) -> bool:
        return self._cached_point is not None or self._target.exists()

    def _resolve_point(self) -> Point:
        if self._cached_point is not None:
            return self._cached_point
        return self._target.resolve()

    def _resolve_action_point(self) -> Optional[Point]:
        if self._exists():
            return self._resolve_point()
        if self._required:
            raise ElementNotFoundError("Element does not exist")
        return None

    def if_exists(self) -> "Element":
        """Skip later actions when the target does not exist."""
        self._required = False
        return self

    def wait_until_exists(self, timeout: float = 10) -> "Element":
        """Wait for the target to appear. `timeout=0` checks once."""
        if timeout <= 0:
            if self._exists():
                return self
            if self._required:
                raise ElementTimeoutError(f"Element not found (timeout={timeout}s)")
            return self

        start = time.monotonic()
        while not self._exists():
            if time.monotonic() - start > timeout:
                if self._required:
                    raise ElementTimeoutError(f"Element not found within {timeout}s")
                return self
            time.sleep(0.1)
        return self

    def assert_exists(self) -> "Element":
        """Require the target to exist before continuing."""
        if not self._exists():
            raise ElementNotFoundError("Element does not exist")
        return self

    def move_to(self) -> "Element":
        point = self._resolve_action_point()
        if point is None:
            return self
        gui.move_to(point.x, point.y)
        return self

    def click(self) -> "Element":
        point = self._resolve_action_point()
        if point is None:
            return self
        gui.click(point.x, point.y)
        return self

    def right_click(self) -> "Element":
        point = self._resolve_action_point()
        if point is None:
            return self
        gui.right_click(point.x, point.y)
        return self

    def double_click(self) -> "Element":
        point = self._resolve_action_point()
        if point is None:
            return self
        gui.double_click(point.x, point.y)
        return self

    def wait(self, seconds: float) -> "Element":
        time.sleep(seconds)
        return self

    def write(self, text: str) -> "Element":
        """Type text with the active keyboard focus."""
        gui.typewrite(text)
        return self

    def press(self, key: str) -> "Element":
        gui.press(key)
        return self

    def hotkey(self, *keys: str) -> "Element":
        if not keys:
            raise ValidationError("hotkey requires at least one key")
        gui.hotkey(*keys)
        return self
