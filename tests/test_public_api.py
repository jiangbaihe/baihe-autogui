from baihe_autogui import (
    Auto,
    AutoGuiError,
    Element,
    ElementNotFoundError,
    ElementTimeoutError,
    ImageNotFoundError,
    ImageTarget,
    OverlayUnavailableError,
    Point,
    PointTarget,
    RegionTarget,
    Target,
    ValidationError,
    __version__,
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
    assert issubclass(OverlayUnavailableError, AutoGuiError)


def test_core_gui_export():
    assert hasattr(gui, "click")
    assert hasattr(gui, "move_to")
    assert hasattr(gui, "move_by")
    assert hasattr(gui, "right_click")


def test_version_export():
    assert isinstance(__version__, str)
    assert __version__


def test_element_exposes_hover_not_move_to():
    element = Element(PointTarget(100, 200))
    assert hasattr(element, "hover")
    assert not hasattr(element, "move_to")
