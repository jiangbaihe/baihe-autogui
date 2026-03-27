from unittest.mock import MagicMock, patch

import pyautogui
import pytest

from baihe_autogui.core.target import (
    ImageNotFoundError,
    ImageTarget,
    Point,
    PointTarget,
    RegionTarget,
)


class TestPoint:
    def test_point_creation(self):
        p = Point(100, 200)
        assert p.x == 100
        assert p.y == 200

    def test_point_equality(self):
        p1 = Point(100, 200)
        p2 = Point(100, 200)
        assert p1 == p2


class TestPointTarget:
    @patch("baihe_autogui.core.target.pyautogui.size")
    def test_point_target_exists_in_screen(self, mock_size):
        mock_size.return_value = (1920, 1080)
        target = PointTarget(100, 200)
        assert target.exists() is True

    @patch("baihe_autogui.core.target.pyautogui.size")
    def test_point_target_out_of_screen(self, mock_size):
        mock_size.return_value = (1920, 1080)
        target = PointTarget(3000, 3000)
        assert target.exists() is False

    @patch("baihe_autogui.core.target.pyautogui.size")
    def test_point_target_in_region(self, mock_size):
        mock_size.return_value = (1920, 1080)
        target = PointTarget(100, 200, search_region=(0, 0, 800, 600))
        assert target.exists() is True

    @patch("baihe_autogui.core.target.pyautogui.size")
    def test_point_target_out_of_region(self, mock_size):
        mock_size.return_value = (1920, 1080)
        target = PointTarget(1000, 1000, search_region=(0, 0, 800, 600))
        assert target.exists() is False

    @patch("baihe_autogui.core.target.pyautogui.size")
    def test_point_target_resolve(self, mock_size):
        mock_size.return_value = (1920, 1080)
        target = PointTarget(100, 200)
        point = target.resolve()
        assert point.x == 100
        assert point.y == 200

    @patch("baihe_autogui.core.target.pyautogui.size")
    def test_point_target_resolve_raises_when_not_exists(self, mock_size):
        mock_size.return_value = (1920, 1080)
        target = PointTarget(3000, 3000)
        with pytest.raises(ValueError):
            target.resolve()


class TestRegionTarget:
    @patch("baihe_autogui.core.target.pyautogui.size")
    def test_region_target_exists_in_screen(self, mock_size):
        mock_size.return_value = (1920, 1080)
        target = RegionTarget(100, 200, 300, 400)
        assert target.exists() is True

    @patch("baihe_autogui.core.target.pyautogui.size")
    def test_region_target_fully_out_of_screen(self, mock_size):
        mock_size.return_value = (1920, 1080)
        target = RegionTarget(3000, 3000, 100, 100)
        assert target.exists() is False

    @patch("baihe_autogui.core.target.pyautogui.size")
    def test_region_target_partially_out_of_screen(self, mock_size):
        mock_size.return_value = (1920, 1080)
        # Region starting at 1800, 1000 with width 200, height 200
        # Right edge (2000) exceeds screen width (1920)
        target = RegionTarget(1800, 1000, 200, 200)
        assert target.exists() is False

    @patch("baihe_autogui.core.target.pyautogui.size")
    def test_region_target_in_search_region(self, mock_size):
        mock_size.return_value = (1920, 1080)
        # Region: (100, 200, 300, 400) -> right=400, bottom=600
        # Search region: (0, 0, 800, 600) -> right=800, bottom=600
        # 100>=0, 400<=800, 200>=0, 600<=600 -> within bounds
        target = RegionTarget(100, 200, 300, 400, search_region=(0, 0, 800, 600))
        assert target.exists() is True

    @patch("baihe_autogui.core.target.pyautogui.size")
    def test_region_target_resolve_center(self, mock_size):
        mock_size.return_value = (1920, 1080)
        target = RegionTarget(100, 200, 300, 400)
        point = target.resolve()
        # Center = (100 + 300/2, 200 + 400/2) = (250, 400)
        assert point.x == 250
        assert point.y == 400


class TestImageTarget:
    def test_image_target_creation(self):
        target = ImageTarget("btn.png")
        assert target.image == "btn.png"
        assert target.confidence == 0.8
        assert target.timeout == 0
        assert target.retry == 0

    def test_image_target_with_params(self):
        target = ImageTarget(
            "btn.png",
            search_region=(0, 0, 800, 600),
            confidence=0.9,
            timeout=0.5,
            retry=3,
        )
        assert target.search_region == (0, 0, 800, 600)
        assert target.confidence == 0.9
        assert target.timeout == 0.5
        assert target.retry == 3

    @patch("baihe_autogui.core.target.pyautogui.locateCenterOnScreen")
    def test_image_target_resolve_success(self, mock_locate):
        mock_locate.return_value = MagicMock(x=100, y=200)
        target = ImageTarget("btn.png")
        point = target.resolve()
        assert point.x == 100
        assert point.y == 200

    @patch("baihe_autogui.core.target.pyautogui.locateCenterOnScreen")
    def test_image_target_resolve_not_found(self, mock_locate):
        mock_locate.side_effect = MagicMock(side_effect=pyautogui.ImageNotFoundException())
        target = ImageTarget("btn.png")
        with pytest.raises(ImageNotFoundError):
            target.resolve()

    @patch("baihe_autogui.core.target.pyautogui.locateCenterOnScreen")
    def test_image_target_exists_true(self, mock_locate):
        mock_locate.return_value = MagicMock(x=100, y=200)
        target = ImageTarget("btn.png")
        assert target.exists() is True

    @patch("baihe_autogui.core.target.pyautogui.locateCenterOnScreen")
    def test_image_target_exists_false(self, mock_locate):
        mock_locate.side_effect = MagicMock(side_effect=pyautogui.ImageNotFoundException())
        target = ImageTarget("btn.png")
        assert target.exists() is False

    @patch("baihe_autogui.core.target.pyautogui.locateCenterOnScreen")
    def test_image_target_resolve_none_raises_not_found(self, mock_locate):
        mock_locate.return_value = None
        target = ImageTarget("btn.png")
        with pytest.raises(ImageNotFoundError):
            target.resolve()

    @patch("baihe_autogui.core.target.pyautogui.locateCenterOnScreen")
    def test_image_target_retry(self, mock_locate):
        # First two calls fail, third succeeds
        mock_locate.side_effect = [
            pyautogui.ImageNotFoundException(),
            pyautogui.ImageNotFoundException(),
            MagicMock(x=100, y=200),
        ]
        target = ImageTarget("btn.png", retry=2, timeout=0.01)
        point = target.resolve()
        assert point.x == 100
        assert mock_locate.call_count == 3

    @patch("baihe_autogui.core.target.pyautogui.locateAllOnScreen")
    def test_image_target_locate_all_returns_centers(self, mock_locate_all):
        mock_locate_all.return_value = [
            MagicMock(left=80, top=180, width=40, height=40),
            MagicMock(left=260, top=360, width=80, height=80),
        ]
        target = ImageTarget("btn.png")
        assert target._locate_all_with_retry() == [Point(100, 200), Point(300, 400)]

    @patch("baihe_autogui.core.target.pyautogui.locateAllOnScreen")
    def test_image_target_locate_all_not_found_returns_empty_list(self, mock_locate_all):
        mock_locate_all.side_effect = pyautogui.ImageNotFoundException()
        target = ImageTarget("btn.png")
        assert target._locate_all_with_retry() == []
