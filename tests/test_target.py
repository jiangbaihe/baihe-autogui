from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from baihe_autogui.core.exceptions import ImageNotFoundError
from baihe_autogui.core.gui import gui
from baihe_autogui.core.target import (
    ImageTarget,
    Point,
    PointTarget,
    RegionTarget,
)


class TestPoint:
    def test_point_creation(self):
        point = Point(100, 200)
        assert point.x == 100
        assert point.y == 200

    def test_point_equality(self):
        assert Point(100, 200) == Point(100, 200)


class TestPointTarget:
    @patch("baihe_autogui.core.target.gui.size")
    def test_point_target_exists_in_screen(self, mock_size):
        mock_size.return_value = (1920, 1080)
        assert PointTarget(100, 200).exists() is True

    @patch("baihe_autogui.core.target.gui.size")
    def test_point_target_out_of_screen(self, mock_size):
        mock_size.return_value = (1920, 1080)
        assert PointTarget(3000, 3000).exists() is False

    @patch("baihe_autogui.core.target.gui.size")
    def test_point_target_in_region(self, mock_size):
        mock_size.return_value = (1920, 1080)
        assert PointTarget(100, 200, search_region=(0, 0, 800, 600)).exists() is True

    @patch("baihe_autogui.core.target.gui.size")
    def test_point_target_out_of_region(self, mock_size):
        mock_size.return_value = (1920, 1080)
        assert PointTarget(1000, 1000, search_region=(0, 0, 800, 600)).exists() is False

    @patch("baihe_autogui.core.target.gui.size")
    def test_point_target_resolve(self, mock_size):
        mock_size.return_value = (1920, 1080)
        assert PointTarget(100, 200).resolve() == Point(100, 200)

    @patch("baihe_autogui.core.target.gui.size")
    def test_point_target_resolve_raises_when_not_exists(self, mock_size):
        mock_size.return_value = (1920, 1080)
        with pytest.raises(ValueError):
            PointTarget(3000, 3000).resolve()


class TestRegionTarget:
    @patch("baihe_autogui.core.target.gui.size")
    def test_region_target_exists_in_screen(self, mock_size):
        mock_size.return_value = (1920, 1080)
        assert RegionTarget(100, 200, 300, 400).exists() is True

    @patch("baihe_autogui.core.target.gui.size")
    def test_region_target_fully_out_of_screen(self, mock_size):
        mock_size.return_value = (1920, 1080)
        assert RegionTarget(3000, 3000, 100, 100).exists() is False

    @patch("baihe_autogui.core.target.gui.size")
    def test_region_target_partially_out_of_screen(self, mock_size):
        mock_size.return_value = (1920, 1080)
        assert RegionTarget(1800, 1000, 200, 200).exists() is False

    @patch("baihe_autogui.core.target.gui.size")
    def test_region_target_in_search_region(self, mock_size):
        mock_size.return_value = (1920, 1080)
        target = RegionTarget(100, 200, 300, 400, search_region=(0, 0, 800, 600))
        assert target.exists() is True

    @patch("baihe_autogui.core.target.gui.size")
    def test_region_target_resolve_center(self, mock_size):
        mock_size.return_value = (1920, 1080)
        assert RegionTarget(100, 200, 300, 400).resolve() == Point(250, 400)

    def test_region_target_resolve_region(self):
        assert RegionTarget(100, 200, 300, 400).resolve_region() == (100, 200, 300, 400)


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

    def test_image_target_normalizes_path_to_string(self):
        target = ImageTarget(Path("btn.png"))
        assert target.image == "btn.png"

    @patch("baihe_autogui.core.target.gui.locate_on_screen")
    def test_image_target_resolve_success(self, mock_locate):
        mock_locate.return_value = MagicMock(left=80, top=180, width=40, height=40)
        assert ImageTarget("btn.png").resolve() == Point(100, 200)

    @patch("baihe_autogui.core.target.gui.locate_on_screen")
    def test_image_target_resolve_not_found(self, mock_locate):
        mock_locate.side_effect = gui.image_not_found_exception()
        with pytest.raises(ImageNotFoundError):
            ImageTarget("btn.png").resolve()

    @patch("baihe_autogui.core.target.gui.locate_on_screen")
    def test_image_target_exists_true(self, mock_locate):
        mock_locate.return_value = MagicMock(left=80, top=180, width=40, height=40)
        assert ImageTarget("btn.png").exists() is True

    @patch("baihe_autogui.core.target.gui.locate_on_screen")
    def test_image_target_exists_false(self, mock_locate):
        mock_locate.side_effect = gui.image_not_found_exception()
        assert ImageTarget("btn.png").exists() is False

    @patch("baihe_autogui.core.target.gui.locate_on_screen")
    def test_image_target_resolve_none_raises_not_found(self, mock_locate):
        mock_locate.return_value = None
        with pytest.raises(ImageNotFoundError):
            ImageTarget("btn.png").resolve()

    @patch("baihe_autogui.core.target.gui.locate_on_screen")
    def test_image_target_retry(self, mock_locate):
        mock_locate.side_effect = [
            gui.image_not_found_exception(),
            gui.image_not_found_exception(),
            MagicMock(left=80, top=180, width=40, height=40),
        ]
        target = ImageTarget("btn.png", retry=2, timeout=0.01)
        assert target.resolve() == Point(100, 200)
        assert mock_locate.call_count == 3

    @patch("baihe_autogui.core.target.gui.locate_on_screen")
    def test_image_target_resolve_region_success(self, mock_locate):
        mock_locate.return_value = MagicMock(left=80, top=180, width=40, height=40)
        assert ImageTarget("btn.png").resolve_region() == (80, 180, 40, 40)

    @patch("baihe_autogui.core.target.gui.locate_all_on_screen")
    def test_image_target_locate_all_returns_centers(self, mock_locate_all):
        mock_locate_all.return_value = [
            MagicMock(left=80, top=180, width=40, height=40),
            MagicMock(left=260, top=360, width=80, height=80),
        ]
        assert ImageTarget("btn.png")._locate_all_with_retry() == [
            Point(100, 200),
            Point(300, 400),
        ]

    @patch("baihe_autogui.core.target.gui.locate_all_on_screen")
    def test_image_target_locate_all_not_found_returns_empty_list(self, mock_locate_all):
        mock_locate_all.side_effect = gui.image_not_found_exception()
        assert ImageTarget("btn.png")._locate_all_with_retry() == []

    @patch("baihe_autogui.core.target.gui.locate_all_on_screen")
    def test_image_target_locate_all_dedupes_heavily_overlapping_matches(
        self, mock_locate_all
    ):
        mock_locate_all.return_value = [
            MagicMock(left=80, top=180, width=40, height=40),
            MagicMock(left=82, top=182, width=40, height=40),
            MagicMock(left=260, top=360, width=80, height=80),
        ]
        assert ImageTarget("btn.png")._locate_all_regions_with_retry() == [
            (80, 180, 40, 40),
            (260, 360, 80, 80),
        ]

    @patch("baihe_autogui.core.target.gui.locate_all_on_screen")
    def test_image_target_locate_all_dedupes_transitively_overlapping_matches(
        self, mock_locate_all
    ):
        mock_locate_all.return_value = [
            MagicMock(left=344, top=97, width=13, height=13),
            MagicMock(left=351, top=97, width=13, height=13),
            MagicMock(left=358, top=97, width=13, height=13),
        ]
        assert ImageTarget("btn.png")._locate_all_regions_with_retry() == [
            (344, 97, 13, 13),
        ]

    @patch("baihe_autogui.core.target.gui.locate_all_on_screen")
    def test_image_target_locate_all_accepts_path_input(self, mock_locate_all):
        mock_locate_all.return_value = []
        ImageTarget(Path("btn.png"))._locate_all_with_retry()
        mock_locate_all.assert_called_once_with(
            "btn.png",
            confidence=0.8,
            region=None,
        )
