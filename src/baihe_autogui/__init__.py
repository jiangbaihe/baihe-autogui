from importlib.metadata import PackageNotFoundError, version

from .core.auto import Auto
from .core.element import Element
from .core.exceptions import (
    AutoGuiError,
    ElementNotFoundError,
    ElementTimeoutError,
    ImageNotFoundError,
    OverlayUnavailableError,
    ValidationError,
)
from .core.target import (
    ImageTarget,
    Point,
    PointTarget,
    RegionTarget,
    Target,
)

try:
    __version__ = version("baihe-autogui")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "Auto",
    "AutoGuiError",
    "Element",
    "ElementNotFoundError",
    "ElementTimeoutError",
    "ImageTarget",
    "ImageNotFoundError",
    "OverlayUnavailableError",
    "Point",
    "PointTarget",
    "RegionTarget",
    "Target",
    "ValidationError",
    "__version__",
]


def main() -> None:
    print("baihe-autogui provides a Python API. Use: from baihe_autogui import Auto")
