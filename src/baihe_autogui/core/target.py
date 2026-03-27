import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple

import pyautogui

from .types import ImageInput, OptionalRegion


@dataclass
class Point:
    x: int
    y: int


def _resolve_search_region(search_region: OptionalRegion) -> Tuple[int, int, int, int]:
    screen_w, screen_h = pyautogui.size()
    return search_region if search_region else (0, 0, screen_w, screen_h)


def _point_from_box(box) -> Point:
    if all(hasattr(box, attr) for attr in ("left", "top", "width", "height")):
        return Point(box.left + box.width // 2, box.top + box.height // 2)
    return Point(box.x, box.y)


class Target(ABC):
    """所有 Target 的基类"""

    @abstractmethod
    def resolve(self) -> Point:
        """解析目标为中心点坐标，目标不存在时抛异常"""
        ...

    @abstractmethod
    def exists(self) -> bool:
        """检查目标是否完全在搜索区域内"""
        ...


class PointTarget(Target):
    """点坐标目标"""

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


class RegionTarget(Target):
    """区域目标 - 返回区域中心点"""

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


class ImageNotFoundError(Exception):
    """图像未找到异常"""


class ImageTarget(Target):
    """图像目标 - 通过图像匹配定位"""

    def __init__(
        self,
        image: ImageInput,
        search_region: OptionalRegion = None,
        confidence: float = 0.8,
        timeout: float = 0,
        retry: int = 0,
    ):
        self.image = image
        self.search_region = search_region
        self.confidence = confidence
        self.timeout = timeout
        self.retry = retry

    def _locate_with_retry(self) -> Point:
        """带重试的图像定位"""
        for attempt in range(self.retry + 1):
            try:
                location = pyautogui.locateCenterOnScreen(
                    self.image,
                    confidence=self.confidence,
                    region=self.search_region,
                )
                if location is not None:
                    return Point(location.x, location.y)
            except pyautogui.ImageNotFoundException:
                location = None
            if attempt < self.retry:
                time.sleep(self.timeout)
        raise ImageNotFoundError(f"Image not found: {self.image}")

    def _locate_all_with_retry(self) -> List[Point]:
        """带重试的图像定位，返回所有匹配"""
        for attempt in range(self.retry + 1):
            try:
                locations = list(
                    pyautogui.locateAllOnScreen(
                        self.image,
                        confidence=self.confidence,
                        region=self.search_region,
                    )
                )
                if locations:
                    return [_point_from_box(location) for location in locations]
            except pyautogui.ImageNotFoundException:
                locations = []
            if attempt < self.retry:
                time.sleep(self.timeout)
        return []

    def exists(self) -> bool:
        try:
            self._locate_with_retry()
            return True
        except ImageNotFoundError:
            return False

    def resolve(self) -> Point:
        return self._locate_with_retry()
