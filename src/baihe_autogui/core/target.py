import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from .exceptions import ImageNotFoundError
from .gui import gui
from .types import ImageInput, OptionalRegion


@dataclass
class Point:
    x: int
    y: int


def _resolve_search_region(search_region: OptionalRegion) -> Tuple[int, int, int, int]:
    screen_w, screen_h = gui.size()
    return search_region if search_region else (0, 0, screen_w, screen_h)


def _point_from_box(box) -> Point:
    if all(hasattr(box, attr) for attr in ("left", "top", "width", "height")):
        return Point(box.left + box.width // 2, box.top + box.height // 2)
    return Point(box.x, box.y)


def _region_from_box(box) -> Tuple[int, int, int, int]:
    return (box.left, box.top, box.width, box.height)


def _point_from_region(region: Tuple[int, int, int, int]) -> Point:
    x, y, width, height = region
    return Point(x + width // 2, y + height // 2)


class Target(ABC):
    """Base interface for anything that can resolve to a screen point."""

    @abstractmethod
    def resolve(self) -> Point:
        """Resolve the target to a point or raise when it cannot be found."""
        ...

    @abstractmethod
    def exists(self) -> bool:
        """Return whether the target currently exists within the search region."""
        ...

    @abstractmethod
    def resolve_region(self) -> Optional[Tuple[int, int, int, int]]:
        """Resolve the target to a search region when supported."""
        ...


class PointTarget(Target):
    """Static point target."""

    def __init__(self, x: int, y: int, search_region: OptionalRegion = None):
        self.x = x
        self.y = y
        self.search_region = search_region

    def exists(self) -> bool:
        sx, sy, sw, sh = _resolve_search_region(self.search_region)
        return sx <= self.x < sx + sw and sy <= self.y < sy + sh

    def resolve(self) -> Point:
        if not self.exists():
            raise ValueError(
                f"Point ({self.x}, {self.y}) is not within search region"
            )
        return Point(self.x, self.y)

    def resolve_region(self) -> Optional[Tuple[int, int, int, int]]:
        return None


class RegionTarget(Target):
    """Rectangular target that resolves to its center point."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        search_region: OptionalRegion = None,
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.search_region = search_region

    def exists(self) -> bool:
        if self.width <= 0 or self.height <= 0:
            return False

        sx, sy, sw, sh = _resolve_search_region(self.search_region)
        in_x = sx <= self.x and self.x + self.width <= sx + sw
        in_y = sy <= self.y and self.y + self.height <= sy + sh
        return in_x and in_y

    def resolve(self) -> Point:
        if not self.exists():
            raise ValueError(
                f"Region ({self.x}, {self.y}, {self.width}, {self.height}) "
                "is not fully within search region"
            )
        return Point(self.x + self.width // 2, self.y + self.height // 2)

    def resolve_region(self) -> Optional[Tuple[int, int, int, int]]:
        return (self.x, self.y, self.width, self.height)


class ImageTarget(Target):
    """Image-based target resolved through pyautogui matching."""

    def __init__(
        self,
        image: ImageInput,
        search_region: OptionalRegion = None,
        confidence: float = 0.8,
        timeout: float = 0,
        retry: int = 0,
    ):
        self.image = str(image) if isinstance(image, Path) else image
        self.search_region = search_region
        self.confidence = confidence
        self.timeout = timeout
        self.retry = retry

    def _locate_with_retry(self) -> Point:
        """Locate a single image match with retry semantics."""
        return _point_from_region(self._locate_region_with_retry())

    def _locate_region_with_retry(self) -> Tuple[int, int, int, int]:
        """Locate a single image match box with retry semantics."""
        for attempt in range(self.retry + 1):
            try:
                location = gui.locate_on_screen(
                    self.image,
                    confidence=self.confidence,
                    region=self.search_region,
                )
                if location is not None:
                    return _region_from_box(location)
            except gui.image_not_found_exception:
                location = None
            if attempt < self.retry:
                time.sleep(self.timeout)
        raise ImageNotFoundError(f"Image not found: {self.image}")

    def _locate_all_with_retry(self) -> List[Point]:
        """Locate all image matches and return their center points."""
        return [_point_from_region(region) for region in self._locate_all_regions_with_retry()]

    def _locate_all_regions_with_retry(self) -> List[Tuple[int, int, int, int]]:
        """Locate all image matches and return their boxes."""
        for attempt in range(self.retry + 1):
            try:
                locations = list(
                    gui.locate_all_on_screen(
                        self.image,
                        confidence=self.confidence,
                        region=self.search_region,
                    )
                )
                if locations:
                    return [_region_from_box(location) for location in locations]
            except gui.image_not_found_exception:
                locations = []
            if attempt < self.retry:
                time.sleep(self.timeout)
        return []

    def exists(self) -> bool:
        try:
            self._locate_region_with_retry()
            return True
        except ImageNotFoundError:
            return False

    def resolve(self) -> Point:
        return self._locate_with_retry()

    def resolve_region(self) -> Optional[Tuple[int, int, int, int]]:
        return self._locate_region_with_retry()


class MultiTarget(Target):
    """Ordered fallback target that tries multiple target types in sequence."""

    def __init__(self, targets: List[Target]):
        self.targets = targets

    def exists(self) -> bool:
        return any(target.exists() for target in self.targets)

    def resolve(self) -> Point:
        for target in self.targets:
            if not target.exists():
                continue
            try:
                return target.resolve()
            except (ImageNotFoundError, ValueError):
                continue
        raise ImageNotFoundError("No targets matched")

    def resolve_region(self) -> Optional[Tuple[int, int, int, int]]:
        for target in self.targets:
            if not target.exists():
                continue
            try:
                return target.resolve_region()
            except (ImageNotFoundError, ValueError):
                continue
        return None
