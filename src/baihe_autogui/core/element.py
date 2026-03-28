import time
from typing import TYPE_CHECKING, Optional, Set

from .exceptions import (
    ElementNotFoundError,
    ElementTimeoutError,
    ImageNotFoundError,
    ValidationError,
)
from .gui import gui
from .overlay import HighlightSpec, overlay
from .target import (
    ImageTarget,
    Point,
    Target,
    point_from_region,
    point_from_region_anchor,
)
from .types import LocateInput, OptionalRegion

if TYPE_CHECKING:
    from .auto import Auto

DEFAULT_ANCHOR = "center"
VALID_ANCHORS = {
    "top_left",
    "top",
    "top_right",
    "left",
    "center",
    "right",
    "bottom_left",
    "bottom",
    "bottom_right",
}


class Element:
    def __init__(
        self,
        target: Target,
        auto: Optional["Auto"] = None,
        cached_point: Optional[Point] = None,
        cached_region: OptionalRegion = None,
    ):
        self._target = target
        self._auto = auto
        self._required = True
        self._skipped = False
        self._cached_point = cached_point
        self._cached_region = cached_region
        self._highlight_ids: Set[str] = set()

    def exists(self) -> bool:
        """Return whether the current target exists without changing chain state."""
        return self._cached_point is not None or self._target.exists()

    def _exists(self) -> bool:
        """Backward-compatible internal alias for the public exists() check."""
        return self.exists()

    def _resolve_point(self) -> Point:
        if self._cached_point is not None:
            return self._cached_point
        return self._target.resolve()

    def _validate_anchor(self, anchor: str) -> None:
        if anchor not in VALID_ANCHORS:
            raise ValidationError(
                "anchor must be one of: "
                "top_left, top, top_right, left, center, right, "
                "bottom_left, bottom, bottom_right"
            )

    def _resolve_region(self) -> OptionalRegion:
        if self._cached_region is not None:
            return self._cached_region

        try:
            if isinstance(self._target, ImageTarget):
                region = self._target.resolve_region()
                if region is None:
                    raise ElementNotFoundError("Element does not exist")
                self._cached_region = region
                self._cached_point = point_from_region(region)
                return region

            if not self._target.exists():
                raise ElementNotFoundError("Element does not exist")

            region = self._target.resolve_region()
            if region is not None:
                self._cached_region = region
                self._cached_point = point_from_region(region)
            return region
        except (ElementNotFoundError, ImageNotFoundError, ValueError) as exc:
            if self._required:
                raise ElementNotFoundError("Element does not exist") from exc
            return None

    def _should_skip_chain(self) -> bool:
        if self._required:
            return False
        if self._skipped:
            return True
        if self.exists():
            return False
        self._skipped = True
        return True

    def _resolve_action_point(
        self,
        *,
        anchor: str = DEFAULT_ANCHOR,
        dx: int = 0,
        dy: int = 0,
    ) -> Optional[Point]:
        self._validate_anchor(anchor)

        if not isinstance(dx, int) or isinstance(dx, bool):
            raise ValidationError("dx must be an integer")
        if not isinstance(dy, int) or isinstance(dy, bool):
            raise ValidationError("dy must be an integer")

        if self._cached_point is not None and self._cached_region is None:
            if anchor != DEFAULT_ANCHOR:
                raise ValidationError("point targets only support anchor='center'")
            return Point(self._cached_point.x + dx, self._cached_point.y + dy)

        region = self._resolve_region()
        if region is not None:
            point = point_from_region_anchor(region, anchor)
            return Point(point.x + dx, point.y + dy)

        if self.exists():
            if anchor != DEFAULT_ANCHOR:
                raise ValidationError("point targets only support anchor='center'")
            point = self._resolve_point()
            return Point(point.x + dx, point.y + dy)
        if self._required:
            raise ElementNotFoundError("Element does not exist")
        return None

    def _resolve_highlight_spec(self) -> Optional[HighlightSpec]:
        if self._cached_region is not None:
            self._cached_point = point_from_region(self._cached_region)
            return HighlightSpec(
                kind="region",
                region=self._cached_region,
                color="red",
                thickness=2,
            )

        if self._cached_point is not None:
            return HighlightSpec(
                kind="point",
                point=self._cached_point,
                color="red",
                thickness=2,
            )

        try:
            if isinstance(self._target, ImageTarget):
                region = self._target.resolve_region()
                if region is None:
                    raise ElementNotFoundError("Element does not exist")
                self._cached_region = region
                self._cached_point = point_from_region(region)
                return HighlightSpec(
                    kind="region",
                    region=region,
                    color="red",
                    thickness=2,
                )

            if not self._target.exists():
                raise ElementNotFoundError("Element does not exist")

            region = self._target.resolve_region()
            if region is not None:
                self._cached_region = region
                self._cached_point = point_from_region(region)
                return HighlightSpec(
                    kind="region",
                    region=region,
                    color="red",
                    thickness=2,
                )

            point = self._target.resolve()
            self._cached_point = point
            return HighlightSpec(
                kind="point",
                point=point,
                color="red",
                thickness=2,
            )
        except (ElementNotFoundError, ImageNotFoundError, ValueError) as exc:
            if self._required:
                raise ElementNotFoundError("Element does not exist") from exc
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

    def _get_auto(self) -> "Auto":
        if self._auto is None:
            from .auto import Auto

            self._auto = Auto()
        return self._auto

    def if_exists(self) -> "Element":
        """Skip the remaining chain when the target does not exist."""
        self._required = False
        return self

    def wait_until_exists(self, timeout: float = 10) -> "Element":
        """Wait for the target to appear. `timeout=0` checks once."""
        if self._should_skip_chain():
            return self

        if timeout <= 0:
            if self.exists():
                return self
            if self._required:
                raise ElementTimeoutError(f"Element not found (timeout={timeout}s)")
            return self

        start = time.monotonic()
        while not self.exists():
            if time.monotonic() - start > timeout:
                if self._required:
                    raise ElementTimeoutError(f"Element not found within {timeout}s")
                return self
            time.sleep(0.1)
        return self

    def assert_exists(self) -> "Element":
        """Require the target to exist before continuing."""
        if self._should_skip_chain():
            return self
        if not self.exists():
            raise ElementNotFoundError("Element does not exist")
        return self

    def hover(
        self,
        *,
        anchor: str = DEFAULT_ANCHOR,
        dx: int = 0,
        dy: int = 0,
    ) -> "Element":
        if self._should_skip_chain():
            return self
        point = self._resolve_action_point(anchor=anchor, dx=dx, dy=dy)
        if point is None:
            return self
        gui.move_to(point.x, point.y)
        return self

    def click(
        self,
        *,
        anchor: str = DEFAULT_ANCHOR,
        dx: int = 0,
        dy: int = 0,
    ) -> "Element":
        if self._should_skip_chain():
            return self
        point = self._resolve_action_point(anchor=anchor, dx=dx, dy=dy)
        if point is None:
            return self
        gui.click(point.x, point.y)
        return self

    def right_click(
        self,
        *,
        anchor: str = DEFAULT_ANCHOR,
        dx: int = 0,
        dy: int = 0,
    ) -> "Element":
        if self._should_skip_chain():
            return self
        point = self._resolve_action_point(anchor=anchor, dx=dx, dy=dy)
        if point is None:
            return self
        gui.right_click(point.x, point.y)
        return self

    def double_click(
        self,
        *,
        anchor: str = DEFAULT_ANCHOR,
        dx: int = 0,
        dy: int = 0,
    ) -> "Element":
        if self._should_skip_chain():
            return self
        point = self._resolve_action_point(anchor=anchor, dx=dx, dy=dy)
        if point is None:
            return self
        gui.double_click(point.x, point.y)
        return self

    def wait(self, seconds: float) -> "Element":
        if self._should_skip_chain():
            return self
        time.sleep(seconds)
        return self

    def highlight(
        self,
        timeout: Optional[float] = 0.8,
        color: str = "red",
        thickness: int = 2,
    ) -> "Element":
        if self._should_skip_chain():
            return self
        if timeout is not None and timeout < 0:
            raise ValidationError(
                "highlight timeout must be greater than or equal to 0"
            )
        if thickness <= 0:
            raise ValidationError("highlight thickness must be greater than 0")

        spec = self._resolve_highlight_spec()
        if spec is None:
            return self

        self.clear_highlight()
        highlight_id = overlay.add(
            HighlightSpec(
                kind=spec.kind,
                point=spec.point,
                region=spec.region,
                color=color,
                thickness=thickness,
            ),
            timeout=timeout,
        )
        self._highlight_ids = {highlight_id}
        return self

    def clear_highlight(self) -> "Element":
        overlay.remove_many(set(self._highlight_ids))
        self._highlight_ids.clear()
        return self

    def write(self, text: str) -> "Element":
        """Type text with the active keyboard focus."""
        if self._should_skip_chain():
            return self
        gui.typewrite(text)
        return self

    def press(self, key: str) -> "Element":
        if self._should_skip_chain():
            return self
        gui.press(key)
        return self

    def hotkey(self, *keys: str) -> "Element":
        if self._should_skip_chain():
            return self
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
        if self._should_skip_chain():
            return self
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
        if self._should_skip_chain():
            return []
        region = self._resolve_scope_region()
        return self._get_auto().locate_all(
            target,
            region=region,
            confidence=confidence,
            timeout=timeout,
            retry=retry,
        )
