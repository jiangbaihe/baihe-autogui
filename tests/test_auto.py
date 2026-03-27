from unittest.mock import MagicMock, patch

import pytest

from baihe_autogui.core.auto import Auto
from baihe_autogui.core.exceptions import ValidationError
from baihe_autogui.core.gui import gui
from baihe_autogui.core.target import ImageTarget, Point, PointTarget, RegionTarget


class TestAuto:
    def test_auto_creation(self):
        auto = Auto()
        assert isinstance(auto, Auto)

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

    @patch("baihe_autogui.core.target.gui.locate_all_on_screen")
    def test_locate_all_image(self, mock_all):
        mock_all.return_value = [
            MagicMock(left=80, top=180, width=40, height=40),
            MagicMock(left=260, top=360, width=80, height=80),
            MagicMock(left=475, top=575, width=50, height=50),
        ]
        auto = Auto()
        elements = auto.locate_all("btn.png")
        assert len(elements) == 3
        # Each should have cached point on Element
        assert elements[0]._cached_point == Point(100, 200)
        assert elements[1]._cached_point == Point(300, 400)
        assert elements[2]._cached_point == Point(500, 600)
        assert elements[0]._cached_region == (80, 180, 40, 40)
        assert elements[1]._cached_region == (260, 360, 80, 80)
        assert elements[2]._cached_region == (475, 575, 50, 50)

    @patch("baihe_autogui.core.target.gui.locate_all_on_screen")
    def test_locate_all_image_not_found_returns_empty_list(self, mock_all):
        mock_all.side_effect = gui.image_not_found_exception()
        auto = Auto()
        elements = auto.locate_all("btn.png")
        assert elements == []

    def test_locate_unsupported_type_raises(self):
        auto = Auto()
        with pytest.raises(ValidationError):
            auto.locate(12345)  # Not a valid input type

    def test_locate_invalid_point_target_raises(self):
        auto = Auto()
        with pytest.raises(ValidationError, match="point target"):
            auto.locate((100, "200"))

    def test_locate_invalid_region_target_raises(self):
        auto = Auto()
        with pytest.raises(ValidationError, match="region target"):
            auto.locate((100, 200, 0, 30))

    def test_locate_invalid_search_region_raises(self):
        auto = Auto()
        with pytest.raises(ValidationError, match="region width and height"):
            auto.locate((100, 200), region=(0, 0, 0, 600))

    @pytest.mark.parametrize("confidence", [-0.1, 1.1])
    def test_locate_invalid_confidence_raises(self, confidence):
        auto = Auto()
        with pytest.raises(ValidationError, match="confidence"):
            auto.locate("btn.png", confidence=confidence)

    @pytest.mark.parametrize(
        ("kwargs", "message"),
        [
            ({"timeout": -0.1}, "timeout"),
            ({"retry": -1}, "retry"),
        ],
    )
    def test_locate_invalid_retry_options_raise(self, kwargs, message):
        auto = Auto()
        with pytest.raises(ValidationError, match=message):
            auto.locate("btn.png", **kwargs)
