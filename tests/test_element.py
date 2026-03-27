from unittest.mock import MagicMock, patch

import pytest

from baihe_autogui.core.element import Element
from baihe_autogui.core.exceptions import (
    ElementNotFoundError,
    ElementTimeoutError,
    ValidationError,
)
from baihe_autogui.core.target import Point, PointTarget


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

    def test_assert_exists_raises_when_not_exists(self):
        target = PointTarget(3000, 3000)
        element = Element(target, MockAuto())
        with pytest.raises(ElementNotFoundError):
            element.assert_exists()

    @patch("baihe_autogui.core.element.gui.move_to")
    @patch("baihe_autogui.core.target.gui.size")
    def test_move_to_success(self, mock_size, mock_move_to):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(100, 200), MockAuto())
        element.move_to()
        mock_move_to.assert_called_once_with(100, 200)

    @patch("baihe_autogui.core.element.gui.click")
    @patch("baihe_autogui.core.target.gui.size")
    def test_click_success(self, mock_size, mock_click):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(100, 200), MockAuto())
        element.click()
        mock_click.assert_called_once_with(100, 200)

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
    @patch("baihe_autogui.core.target.gui.size")
    def test_double_click_skips_when_not_required(self, mock_size, mock_double_click):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(3000, 3000), MockAuto()).if_exists()
        element.double_click()
        mock_double_click.assert_not_called()

    def test_wait_returns_self(self):
        element = Element(PointTarget(100, 200), MockAuto())
        assert element.wait(0.001) is element

    @patch("baihe_autogui.core.element.gui.typewrite")
    @patch("baihe_autogui.core.target.gui.size")
    def test_write_calls_typewrite(self, mock_size, mock_typewrite):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(100, 200), MockAuto())
        element.write("hello")
        mock_typewrite.assert_called_once_with("hello")

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

    def test_wait_until_exists_returns_self(self):
        element = Element(PointTarget(100, 200), MockAuto())
        assert element.wait_until_exists(timeout=0.1) is element

    @patch("baihe_autogui.core.target.gui.size")
    def test_wait_until_exists_timeout(self, mock_size):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(3000, 3000), MockAuto()).if_exists()
        assert element.wait_until_exists(timeout=0.1) is element

    @patch("baihe_autogui.core.target.gui.size")
    def test_wait_until_exists_timeout_raises(self, mock_size):
        mock_size.return_value = (1920, 1080)
        element = Element(PointTarget(3000, 3000), MockAuto())
        with pytest.raises(ElementTimeoutError):
            element.wait_until_exists(timeout=0.1)

    def test_wait_until_exists_zero_timeout_exists(self):
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

