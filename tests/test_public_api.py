from baihe_autogui import (
    Auto,
    AutoGuiError,
    Element,
    ElementNotFoundError,
    ElementTimeoutError,
    ImageNotFoundError,
    ImageTarget,
    Point,
    PointTarget,
    RegionTarget,
    Target,
    ValidationError,
)
from baihe_autogui.core import gui


def test_root_exports():
    assert Auto is not None
    assert Element is not None
    assert Point is not None
    assert Target is not None
    assert PointTarget is not None
    assert RegionTarget is not None
    assert ImageTarget is not None


def test_exception_exports():
    assert issubclass(ValidationError, (ValueError, AutoGuiError))
    assert issubclass(ElementNotFoundError, (AssertionError, AutoGuiError))
    assert issubclass(ElementTimeoutError, (TimeoutError, AutoGuiError))
    assert issubclass(ImageNotFoundError, AutoGuiError)


def test_core_gui_export():
    assert hasattr(gui, "click")
    assert hasattr(gui, "move_to")
    assert hasattr(gui, "right_click")
