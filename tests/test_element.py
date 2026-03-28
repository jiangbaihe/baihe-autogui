from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

from baihe_autogui.core.element import Element
from baihe_autogui.core.exceptions import (
    ElementNotFoundError,
    ElementTimeoutError,
    ValidationError,
)
from baihe_autogui.core.overlay import HighlightSpec
from baihe_autogui.core.target import Point, PointTarget, RegionTarget


class MockAuto:
    pass


class TestElement:
    def test_element_creation(self):
        target = PointTarget(100, 200)
        auto = MockAuto()
        element = Element(target, auto)
        assert element._target is target
        assert element._required is True

    def test_if_exists_sets_required_false(self):
        target = PointTarget(100, 200)
        element = Element(target, MockAuto())
        result = element.if_exists()
        assert element._required is False
        assert result is element

    @patch("baihe_autogui.core.target.gui.size")
    def test_exists_returns_true_when_target_exists(self, mock_size):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(100, 200), MockAuto())
        assert element.exists() is True

    @patch("baihe_autogui.core.target.gui.size")
    def test_exists_returns_false_when_target_missing(self, mock_size):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(3000, 3000), MockAuto())
        assert element.exists() is False

    def test_exists_with_cached_point_skips_relookup(self):
        target = MagicMock()
        target.exists.side_effect = AssertionError("cached point should skip relookup")
        element = Element(target, cached_point=Point(300, 400))
        assert element.exists() is True
        target.exists.assert_not_called()

    @patch("baihe_autogui.core.target.gui.size")
    def test_assert_exists_raises_when_not_exists(self, mock_size):
        mock_size.return_value = (1920, 1080)
        target = PointTarget(3000, 3000)
        element = Element(target, MockAuto())
        with pytest.raises(ElementNotFoundError):
            element.assert_exists()

    @patch("baihe_autogui.core.element.gui.move_to")
    @patch("baihe_autogui.core.target.gui.size")
    def test_hover_success(self, mock_size, mock_move_to):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(100, 200), MockAuto())
        element.hover()
        mock_move_to.assert_called_once_with(100, 200)

    @patch("baihe_autogui.core.element.gui.move_to")
    def test_hover_region_anchor(self, mock_move_to):
        element = Element(RegionTarget(10, 20, 100, 80), MockAuto())
        element.hover(anchor="top_right")
        mock_move_to.assert_called_once_with(109, 20)

    @patch("baihe_autogui.core.element.gui.move_to")
    def test_hover_region_anchor_with_offset(self, mock_move_to):
        element = Element(RegionTarget(10, 20, 100, 80), MockAuto())
        element.hover(anchor="bottom_left", dx=5, dy=-3)
        mock_move_to.assert_called_once_with(15, 96)

    @patch("baihe_autogui.core.element.gui.click")
    @patch("baihe_autogui.core.target.gui.size")
    def test_click_point_target_allows_center_offset(self, mock_size, mock_click):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(100, 200), MockAuto())
        element.click(dx=10, dy=-5)
        mock_click.assert_called_once_with(110, 195)

    @patch("baihe_autogui.core.target.gui.size")
    def test_point_target_non_center_anchor_raises(self, mock_size):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(100, 200), MockAuto())
        with pytest.raises(ValidationError, match="point targets only support"):
            element.click(anchor="top_left")

    def test_invalid_anchor_raises(self):
        element = Element(RegionTarget(10, 20, 100, 80), MockAuto())
        with pytest.raises(ValidationError, match="anchor must be one of"):
            element.hover(anchor="invalid")

    def test_invalid_dx_raises(self):
        element = Element(RegionTarget(10, 20, 100, 80), MockAuto())
        with pytest.raises(ValidationError, match="dx must be an integer"):
            element.hover(dx=cast(Any, "1"))

    def test_invalid_dy_raises(self):
        element = Element(RegionTarget(10, 20, 100, 80), MockAuto())
        with pytest.raises(ValidationError, match="dy must be an integer"):
            element.hover(dy=True)

    @patch("baihe_autogui.core.element.gui.click")
    @patch("baihe_autogui.core.target.gui.size")
    def test_click_success(self, mock_size, mock_click):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(100, 200), MockAuto())
        element.click()
        mock_click.assert_called_once_with(100, 200)

    @patch("baihe_autogui.core.element.gui.click")
    def test_click_cached_region_anchor(self, mock_click):
        element = Element(MagicMock(), MockAuto(), cached_region=(50, 60, 70, 80))
        element.click(anchor="right", dx=-2)
        mock_click.assert_called_once_with(117, 100)

    @patch("baihe_autogui.core.element.gui.click")
    @patch("baihe_autogui.core.target.gui.size")
    def test_click_skips_when_not_exists_and_not_required(self, mock_size, mock_click):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(3000, 3000), MockAuto()).if_exists()
        element.click()
        mock_click.assert_not_called()

    @patch("baihe_autogui.core.element.gui.click")
    @patch("baihe_autogui.core.target.gui.size")
    def test_click_raises_when_not_exists_and_required(self, mock_size, mock_click):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(3000, 3000), MockAuto())
        with pytest.raises(ElementNotFoundError):
            element.click()
        mock_click.assert_not_called()

    @patch("baihe_autogui.core.element.gui.right_click")
    @patch("baihe_autogui.core.target.gui.size")
    def test_right_click_success(self, mock_size, mock_right_click):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(100, 200), MockAuto())
        element.right_click()
        mock_right_click.assert_called_once_with(100, 200)

    @patch("baihe_autogui.core.element.gui.right_click")
    def test_right_click_region_bottom_anchor(self, mock_right_click):
        element = Element(RegionTarget(10, 20, 100, 80), MockAuto())
        element.right_click(anchor="bottom")
        mock_right_click.assert_called_once_with(60, 99)

    @patch("baihe_autogui.core.element.gui.right_click")
    @patch("baihe_autogui.core.target.gui.size")
    def test_right_click_skips_when_not_required(self, mock_size, mock_right_click):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(3000, 3000), MockAuto()).if_exists()
        element.right_click()
        mock_right_click.assert_not_called()

    @patch("baihe_autogui.core.element.gui.click")
    @patch("baihe_autogui.core.target.gui.size")
    def test_click_with_cached_point(self, mock_size, mock_click):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(100, 200), MockAuto(), cached_point=Point(300, 400))
        element.click()
        mock_click.assert_called_once_with(300, 400)

    @patch("baihe_autogui.core.element.gui.click")
    def test_click_with_cached_point_skips_relookup(self, mock_click):
        target = MagicMock()
        target.exists.side_effect = AssertionError("cached point should skip relookup")
        element = Element(target, cached_point=Point(300, 400))
        element.click()
        mock_click.assert_called_once_with(300, 400)
        target.exists.assert_not_called()

    @patch("baihe_autogui.core.element.gui.double_click")
    @patch("baihe_autogui.core.target.gui.size")
    def test_double_click_success(self, mock_size, mock_double_click):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(100, 200), MockAuto())
        element.double_click()
        mock_double_click.assert_called_once_with(100, 200)

    @patch("baihe_autogui.core.element.gui.double_click")
    def test_double_click_region_left_anchor(self, mock_double_click):
        element = Element(RegionTarget(10, 20, 100, 80), MockAuto())
        element.double_click(anchor="left", dy=4)
        mock_double_click.assert_called_once_with(10, 64)

    @patch("baihe_autogui.core.element.gui.double_click")
    @patch("baihe_autogui.core.target.gui.size")
    def test_double_click_skips_when_not_required(self, mock_size, mock_double_click):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(3000, 3000), MockAuto()).if_exists()
        element.double_click()
        mock_double_click.assert_not_called()

    def test_wait_returns_self(self):
        element = Element(PointTarget(100, 200), MockAuto())
        assert element.wait(0.001) is element

    @patch("baihe_autogui.core.element.overlay.remove_many")
    @patch("baihe_autogui.core.element.overlay.add")
    @patch("baihe_autogui.core.target.gui.size")
    def test_highlight_region_adds_overlay_and_caches_region(
        self, mock_size, mock_add, mock_remove_many
    ):
        mock_size.return_value = (1920, 1080)
        mock_add.return_value = "highlight-1"
        element = Element(RegionTarget(10, 20, 100, 80), MockAuto())

        result = element.highlight(timeout=1.5, color="lime", thickness=3)

        assert result is element
        mock_remove_many.assert_called_once_with(set())
        mock_add.assert_called_once_with(
            HighlightSpec(
                kind="region",
                region=(10, 20, 100, 80),
                point=None,
                color="lime",
                thickness=3,
            ),
            timeout=1.5,
        )
        assert element._cached_region == (10, 20, 100, 80)
        assert element._cached_point == Point(60, 60)

    @patch("baihe_autogui.core.element.overlay.remove_many")
    @patch("baihe_autogui.core.element.overlay.add")
    def test_highlight_with_cached_point_skips_lookup(self, mock_add, mock_remove_many):
        mock_add.return_value = "highlight-1"
        target = MagicMock()
        target.exists.side_effect = AssertionError("cached point should skip lookup")
        element = Element(target, cached_point=Point(300, 400))

        element.highlight(timeout=2.0)

        mock_remove_many.assert_called_once_with(set())
        mock_add.assert_called_once_with(
            HighlightSpec(
                kind="point",
                point=Point(300, 400),
                region=None,
                color="red",
                thickness=2,
            ),
            timeout=2.0,
        )
        target.exists.assert_not_called()

    @patch("baihe_autogui.core.element.overlay.remove_many")
    @patch("baihe_autogui.core.element.overlay.add")
    def test_highlight_refreshes_existing_element_highlight(
        self, mock_add, mock_remove_many
    ):
        mock_add.side_effect = ["highlight-1", "highlight-2"]
        element = Element(PointTarget(100, 200), MockAuto(), cached_point=Point(100, 200))

        element.highlight(timeout=1.0)
        element.highlight(timeout=2.0)

        assert mock_remove_many.call_args_list[0].args == (set(),)
        assert mock_remove_many.call_args_list[1].args == ({"highlight-1"},)
        assert element._highlight_ids == {"highlight-2"}

    @patch("baihe_autogui.core.element.overlay.remove_many")
    @patch("baihe_autogui.core.element.overlay.add")
    @patch("baihe_autogui.core.target.gui.size")
    def test_highlight_skips_when_not_exists_and_not_required(
        self, mock_size, mock_add, mock_remove_many
    ):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(3000, 3000), MockAuto()).if_exists()

        result = element.highlight(timeout=1.0)

        assert result is element
        mock_add.assert_not_called()
        mock_remove_many.assert_not_called()

    @patch("baihe_autogui.core.element.overlay.remove_many")
    @patch("baihe_autogui.core.target.gui.size")
    def test_highlight_raises_when_not_exists_and_required(
        self, mock_size, mock_remove_many
    ):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(3000, 3000), MockAuto())

        with pytest.raises(ElementNotFoundError):
            element.highlight(timeout=1.0)

        mock_remove_many.assert_not_called()

    @patch("baihe_autogui.core.element.gui.click")
    @patch("baihe_autogui.core.element.overlay.remove_many")
    @patch("baihe_autogui.core.element.overlay.add")
    def test_highlight_caches_resolved_region_for_follow_up_click(
        self, mock_add, mock_remove_many, mock_click
    ):
        mock_add.return_value = "highlight-1"
        target = MagicMock()
        target.exists.return_value = True
        target.resolve_region.return_value = (80, 180, 40, 40)
        target.resolve.side_effect = AssertionError("highlight should cache click point")
        element = Element(target, auto=MockAuto())

        element.highlight(timeout=1.0).click()

        mock_remove_many.assert_called_once_with(set())
        mock_click.assert_called_once_with(100, 200)
        target.resolve.assert_not_called()

    @patch("baihe_autogui.core.element.overlay.remove_many")
    def test_clear_highlight_removes_only_owned_ids(self, mock_remove_many):
        element = Element(PointTarget(100, 200), MockAuto(), cached_point=Point(100, 200))
        element._highlight_ids = {"highlight-1", "highlight-2"}

        result = element.clear_highlight()

        assert result is element
        mock_remove_many.assert_called_once_with({"highlight-1", "highlight-2"})
        assert element._highlight_ids == set()

    def test_highlight_invalid_timeout_raises(self):
        element = Element(PointTarget(100, 200), MockAuto())
        with pytest.raises(ValidationError, match="highlight timeout"):
            element.highlight(timeout=-0.1)

    def test_highlight_invalid_thickness_raises(self):
        element = Element(PointTarget(100, 200), MockAuto())
        with pytest.raises(ValidationError, match="highlight thickness"):
            element.highlight(thickness=0)

    @patch("baihe_autogui.core.element.gui.typewrite")
    @patch("baihe_autogui.core.target.gui.size")
    def test_write_calls_typewrite(self, mock_size, mock_typewrite):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(100, 200), MockAuto())
        element.write("hello")
        mock_typewrite.assert_called_once_with("hello")

    @patch("baihe_autogui.core.element.time.sleep")
    @patch("baihe_autogui.core.element.gui.hotkey")
    @patch("baihe_autogui.core.element.gui.press")
    @patch("baihe_autogui.core.element.gui.typewrite")
    @patch("baihe_autogui.core.element.gui.click")
    @patch("baihe_autogui.core.target.gui.size")
    def test_if_exists_skips_remaining_chain_actions_when_missing(
        self,
        mock_size,
        mock_click,
        mock_typewrite,
        mock_press,
        mock_hotkey,
        mock_sleep,
    ):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(3000, 3000), MockAuto()).if_exists()

        result = (
            element.click()
            .wait(0.5)
            .write("hello")
            .press("enter")
            .hotkey("ctrl", "a")
        )

        assert result is element
        mock_click.assert_not_called()
        mock_typewrite.assert_not_called()
        mock_press.assert_not_called()
        mock_hotkey.assert_not_called()
        mock_sleep.assert_not_called()

    @patch("baihe_autogui.core.element.gui.press")
    def test_press_calls_press(self, mock_press):
        element = Element(PointTarget(100, 200), MockAuto())
        element.press("enter")
        mock_press.assert_called_once_with("enter")

    @patch("baihe_autogui.core.element.gui.hotkey")
    def test_hotkey_calls_hotkey(self, mock_hotkey):
        element = Element(PointTarget(100, 200), MockAuto())
        element.hotkey("ctrl", "c")
        mock_hotkey.assert_called_once_with("ctrl", "c")

    def test_hotkey_requires_at_least_one_key(self):
        element = Element(PointTarget(100, 200), MockAuto())
        with pytest.raises(ValidationError, match="hotkey"):
            element.hotkey()

    @patch("baihe_autogui.core.target.gui.size")
    def test_wait_until_exists_returns_self(self, mock_size):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(100, 200), MockAuto())
        assert element.wait_until_exists(timeout=0.1) is element

    @patch("baihe_autogui.core.target.gui.size")
    def test_wait_until_exists_timeout(self, mock_size):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(3000, 3000), MockAuto()).if_exists()
        assert element.wait_until_exists(timeout=0.1) is element

    @patch("baihe_autogui.core.element.time.sleep")
    @patch("baihe_autogui.core.target.gui.size")
    def test_if_exists_wait_until_exists_returns_immediately_after_skip(
        self, mock_size, mock_sleep
    ):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(3000, 3000), MockAuto()).if_exists()

        assert element.wait_until_exists(timeout=5) is element
        mock_sleep.assert_not_called()

    @patch("baihe_autogui.core.target.gui.size")
    def test_wait_until_exists_timeout_raises(self, mock_size):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(3000, 3000), MockAuto())
        with pytest.raises(ElementTimeoutError):
            element.wait_until_exists(timeout=0.1)

    @patch("baihe_autogui.core.target.gui.size")
    def test_wait_until_exists_zero_timeout_exists(self, mock_size):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(100, 200), MockAuto())
        assert element.wait_until_exists(timeout=0) is element

    @patch("baihe_autogui.core.target.gui.size")
    def test_wait_until_exists_zero_timeout_not_exists_no_raise(self, mock_size):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(3000, 3000), MockAuto()).if_exists()
        assert element.wait_until_exists(timeout=0) is element

    @patch("baihe_autogui.core.target.gui.size")
    def test_wait_until_exists_zero_timeout_not_exists_raise(self, mock_size):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(3000, 3000), MockAuto())
        with pytest.raises(ElementTimeoutError):
            element.wait_until_exists(timeout=0)

    @patch("baihe_autogui.core.target.gui.size")
    def test_if_exists_assert_exists_does_not_raise_after_skip(self, mock_size):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(3000, 3000), MockAuto()).if_exists()

        assert element.click().assert_exists() is element

    @patch("baihe_autogui.core.element.gui.click")
    @patch("baihe_autogui.core.target.gui.size")
    def test_if_exists_skipped_nested_locate_returns_same_chain(
        self, mock_size, mock_click
    ):
        mock_size.return_value = (1920, 1080)
        auto = MagicMock()
        element = Element(PointTarget(3000, 3000), auto=auto).if_exists()

        nested = element.locate("inner.png")

        assert nested is element
        auto.locate.assert_not_called()
        nested.click()
        mock_click.assert_not_called()

    @patch("baihe_autogui.core.target.gui.size")
    def test_if_exists_skipped_locate_all_returns_empty_list(self, mock_size):
        mock_size.return_value = (1920, 1080)
        auto = MagicMock()
        element = Element(PointTarget(3000, 3000), auto=auto).if_exists()

        assert element.locate_all("inner.png") == []
        auto.locate_all.assert_not_called()

    def test_nested_locate_scopes_to_region_target(self):
        auto = MagicMock()
        nested = object()
        auto.locate.return_value = nested
        element = Element(RegionTarget(10, 20, 100, 80), auto=auto)

        result = element.locate("inner.png", confidence=0.9, timeout=0.2, retry=2)

        assert result is nested
        auto.locate.assert_called_once_with(
            "inner.png",
            region=(10, 20, 100, 80),
            confidence=0.9,
            timeout=0.2,
            retry=2,
        )

    def test_nested_locate_all_scopes_to_cached_region(self):
        auto = MagicMock()
        nested = [object()]
        auto.locate_all.return_value = nested
        element = Element(MagicMock(), auto=auto, cached_region=(50, 60, 70, 80))

        result = element.locate_all("inner.png")

        assert result is nested
        auto.locate_all.assert_called_once_with(
            "inner.png",
            region=(50, 60, 70, 80),
            confidence=0.8,
            timeout=0,
            retry=0,
        )

    def test_nested_locate_raises_for_point_target(self):
        element = Element(PointTarget(100, 200), MockAuto())
        with pytest.raises(ValidationError, match="nested locate"):
            element.locate("inner.png")

