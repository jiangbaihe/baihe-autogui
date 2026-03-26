from .core.auto import Auto
from .core.element import Element
from .core.target import (
    ImageNotFoundError,
    ImageTarget,
    Point,
    PointTarget,
    RegionTarget,
    Target,
)

__all__ = [
    "Auto",
    "Element",
    "Point",
    "Target",
    "PointTarget",
    "RegionTarget",
    "ImageTarget",
    "ImageNotFoundError",
]


def main() -> None:
    print("Hello from baihe-autogui!")
