from .core.auto import Auto
from .core.element import Element
from .core.exceptions import (
    AutoGuiError,
    ElementNotFoundError,
    ElementTimeoutError,
    ImageNotFoundError,
    ValidationError,
)
from .core.target import (
    ImageTarget,
    Point,
    PointTarget,
    RegionTarget,
    Target,
)

__all__ = [
    "Auto",
    "AutoGuiError",
    "Element",
    "ElementNotFoundError",
    "ElementTimeoutError",
    "ValidationError",
    "Point",
    "Target",
    "PointTarget",
    "RegionTarget",
    "ImageTarget",
    "ImageNotFoundError",
]


def main() -> None:
    print("baihe-autogui provides a Python API. Use: from baihe_autogui import Auto")
