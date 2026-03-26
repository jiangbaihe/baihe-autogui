import pytest
from unittest.mock import patch, MagicMock
from baihe_autogui.core.element import Element
from baihe_autogui.core.target import PointTarget, Point


class MockAuto:
    pass


class TestElement:
    def test_element_creation(self):
        target = PointTarget(100, 200)
        auto = MockAuto()
        element = Element(target, auto)
        assert element._target is target
        assert element._auto is auto
        assert element._required is True

    def test_if_exists_sets_required_false(self):
        target = PointTarget(100, 200)
        element = Element(target, MockAuto())
        result = element.if_exists()
        assert element._required is False
        assert result is element

    def test_assert_exists_raises_when_not_exists(self):
        target = PointTarget(3000, 3000)  # Out of screen
        element = Element(target, MockAuto())
        with pytest.raises(AssertionError):
            element.assert_exists()

    @patch("baihe_autogui.core.element.pyautogui.click")
    @patch("baihe_autogui.core.target.pyautogui.size")
    def test_click_success(self, mock_size, mock_click):
        mock_size.return_value = (1920, 1080)
        target = PointTarget(100, 200)
        element = Element(target, MockAuto())
        element.click()
        mock_click.assert_called_once_with(100, 200)

    @patch("baihe_autogui.core.element.pyautogui.click")
    @patch("baihe_autogui.core.target.pyautogui.size")
    def test_click_skips_when_not_exists_and_not_required(self, mock_size, mock_click):
        mock_size.return_value = (1920, 1080)
        target = PointTarget(3000, 3000)  # Out of screen
        element = Element(target, MockAuto())
        element._required = False
        element.click()
        mock_click.assert_not_called()

    @patch("baihe_autogui.core.element.pyautogui.click")
    @patch("baihe_autogui.core.target.pyautogui.size")
    def test_click_raises_when_not_exists_and_required(self, mock_size, mock_click):
        mock_size.return_value = (1920, 1080)
        target = PointTarget(3000, 3000)  # Out of screen
        element = Element(target, MockAuto())
        with pytest.raises(AssertionError):
            element.click()

    @patch("baihe_autogui.core.element.pyautogui.click")
    @patch("baihe_autogui.core.target.pyautogui.size")
    def test_click_with_cached_point(self, mock_size, mock_click):
        mock_size.return_value = (1920, 1080)
        target = PointTarget(100, 200)
        cached = Point(300, 400)
        element = Element(target, MockAuto(), cached_point=cached)
        element.click()
        mock_click.assert_called_once_with(300, 400)

    def test_wait_returns_self(self):
        target = PointTarget(100, 200)
        element = Element(target, MockAuto())
        result = element.wait(0.001)
        assert result is element

    @patch("baihe_autogui.core.element.pyautogui.typewrite")
    @patch("baihe_autogui.core.target.pyautogui.size")
    def test_write_calls_typewrite(self, mock_size, mock_typewrite):
        mock_size.return_value = (1920, 1080)
        target = PointTarget(100, 200)
        element = Element(target, MockAuto())
        element.write("hello")
        mock_typewrite.assert_called_once_with("hello")

    def test_wait_until_exists_returns_self(self):
        target = PointTarget(100, 200)
        element = Element(target, MockAuto())
        result = element.wait_until_exists(timeout=0.1)
        assert result is element

    @patch("baihe_autogui.core.target.pyautogui.size")
    def test_wait_until_exists_timeout(self, mock_size):
        mock_size.return_value = (1920, 1080)
        target = PointTarget(3000, 3000)  # Never exists
        element = Element(target, MockAuto())
        element._required = False
        result = element.wait_until_exists(timeout=0.1)
        assert result is element

    @patch("baihe_autogui.core.target.pyautogui.size")
    def test_wait_until_exists_timeout_raises(self, mock_size):
        mock_size.return_value = (1920, 1080)
        target = PointTarget(3000, 3000)  # Never exists
        element = Element(target, MockAuto())
        with pytest.raises(TimeoutError):
            element.wait_until_exists(timeout=0.1)

    def test_wait_until_exists_zero_timeout_exists(self):
        """timeout=0 且元素存在时立即返回"""
        target = PointTarget(100, 200)
        element = Element(target, MockAuto())
        result = element.wait_until_exists(timeout=0)
        assert result is element

    @patch("baihe_autogui.core.target.pyautogui.size")
    def test_wait_until_exists_zero_timeout_not_exists_no_raise(self, mock_size):
        """timeout=0 且元素不存在时返回自身（不抛异常）"""
        mock_size.return_value = (1920, 1080)
        target = PointTarget(3000, 3000)  # Never exists
        element = Element(target, MockAuto())
        element._required = False
        result = element.wait_until_exists(timeout=0)
        assert result is element

    @patch("baihe_autogui.core.target.pyautogui.size")
    def test_wait_until_exists_zero_timeout_not_exists_raise(self, mock_size):
        """timeout=0 且元素不存在时抛异常"""
        mock_size.return_value = (1920, 1080)
        target = PointTarget(3000, 3000)  # Never exists
        element = Element(target, MockAuto())
        with pytest.raises(TimeoutError):
            element.wait_until_exists(timeout=0)

