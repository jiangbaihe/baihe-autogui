import pytest
from unittest.mock import patch, MagicMock
from baihe_autogui.core.auto import Auto
from baihe_autogui.core.target import PointTarget, RegionTarget, ImageTarget, Point


class TestAuto:
    def test_auto_creation(self):
        auto = Auto()
        assert auto._pause == 0.1
        assert auto._failsafe is True

    def test_locate_point(self):
        auto = Auto()
        element = auto.locate((100, 200))
        assert isinstance(element._target, PointTarget)
        assert element._target.x == 100
        assert element._target.y == 200

    def test_locate_region(self):
        auto = Auto()
        element = auto.locate((100, 200, 300, 400))
        assert isinstance(element._target, RegionTarget)
        assert element._target.x == 100
        assert element._target.y == 200
        assert element._target.width == 300
        assert element._target.height == 400

    def test_locate_image(self):
        auto = Auto()
        element = auto.locate("btn.png")
        assert isinstance(element._target, ImageTarget)
        assert element._target.image == "btn.png"

    def test_locate_with_region(self):
        auto = Auto()
        element = auto.locate((100, 200), region=(0, 0, 800, 600))
        assert isinstance(element._target, PointTarget)
        assert element._target.search_region == (0, 0, 800, 600)

    def test_locate_with_confidence(self):
        auto = Auto()
        element = auto.locate("btn.png", confidence=0.9)
        assert element._target.confidence == 0.9

    def test_locate_with_retry_timeout(self):
        auto = Auto()
        element = auto.locate("btn.png", retry=3, timeout=0.5)
        assert element._target.retry == 3
        assert element._target.timeout == 0.5

    def test_locate_all_point(self):
        auto = Auto()
        elements = auto.locate_all((100, 200))
        assert len(elements) == 1
        assert isinstance(elements[0]._target, PointTarget)

    def test_locate_all_region(self):
        auto = Auto()
        elements = auto.locate_all((100, 200, 300, 400))
        assert len(elements) == 1
        assert isinstance(elements[0]._target, RegionTarget)

    @patch("baihe_autogui.core.target.pyautogui.locateAllOnScreen")
    @patch("baihe_autogui.core.target.pyautogui.locateCenterOnScreen")
    def test_locate_all_image(self, mock_center, mock_all):
        mock_center.return_value = MagicMock(x=100, y=200)
        mock_all.return_value = [
            MagicMock(x=100, y=200),
            MagicMock(x=300, y=400),
            MagicMock(x=500, y=600),
        ]
        auto = Auto()
        elements = auto.locate_all("btn.png")
        assert len(elements) == 3
        # Each should have cached point on Element
        assert elements[0]._cached_point == Point(100, 200)
        assert elements[1]._cached_point == Point(300, 400)
        assert elements[2]._cached_point == Point(500, 600)

    def test_locate_unsupported_type_raises(self):
        auto = Auto()
        with pytest.raises(ValueError):
            auto.locate(12345)  # Not a valid input type
