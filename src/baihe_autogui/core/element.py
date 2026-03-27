import time
from typing import Any, Optional

from .exceptions import ElementNotFoundError, ElementTimeoutError, ValidationError
from .gui import gui
from .target import Point, Target
from .types import LocateInput, OptionalRegion


class Element:
    def __init__(
        self,
        target: Target,
        auto: Any = None,
        cached_point: Optional[Point] = None,
        cached_region: OptionalRegion = None,
    ):
        self._target = target
        self._auto = auto
        self._required = True
        self._cached_point = cached_point
        self._cached_region = cached_region

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

    def _resolve_scope_region(self) -> OptionalRegion:
        if self._cached_region is not None:
            return self._cached_region

        region = self._target.resolve_region()
        if region is None:
            raise ValidationError(
                "nested locate requires an image or region target as the outer scope"
            )
        return region

    def _get_auto(self):
        if self._auto is None:
            from .auto import Auto

            self._auto = Auto()
        return self._auto

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

    def locate(
        self,
        target: LocateInput,
        *,
        confidence: float = 0.8,
        timeout: float = 0,
        retry: int = 0,
    ) -> "Element":
        region = self._resolve_scope_region()
        return self._get_auto().locate(
            target,
            region=region,
            confidence=confidence,
            timeout=timeout,
            retry=retry,
        )

    def locate_all(
        self,
        target: LocateInput,
        *,
        confidence: float = 0.8,
        timeout: float = 0,
        retry: int = 0,
    ):
        region = self._resolve_scope_region()
        return self._get_auto().locate_all(
            target,
            region=region,
            confidence=confidence,
            timeout=timeout,
            retry=retry,
        )
