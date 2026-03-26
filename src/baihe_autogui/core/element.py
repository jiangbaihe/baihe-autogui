import time
from typing import TYPE_CHECKING

import pyautogui

from .target import Point, Target

if TYPE_CHECKING:
    from .auto import Auto


class Element:
    def __init__(self, target: Target, auto: "Auto", cached_point: "Point" = None):
        self._target = target
        self._auto = auto
        self._required = True
        self._cached_point = cached_point

    def if_exists(self) -> "Element":
        """设置元素不存在时跳过后续操作"""
        self._required = False
        return self

    def wait_until_exists(self, timeout: float = 10) -> "Element":
        """等待元素出现，timeout=0 表示立即返回"""
        if timeout <= 0:
            if self._target.exists():
                return self
            if self._required:
                raise TimeoutError(f"Element not found (timeout={timeout}s)")
            return self

        start = time.time()
        while not self._target.exists():
            if time.time() - start > timeout:
                if self._required:
                    raise TimeoutError(f"Element not found within {timeout}s")
                return self
            time.sleep(0.1)
        return self

    def assert_exists(self) -> "Element":
        """断言元素必须存在，否则抛异常"""
        if not self._target.exists():
            raise AssertionError("Element does not exist")
        return self

    def click(self) -> "Element":
        if not self._target.exists():
            if self._required:
                raise AssertionError("Element does not exist")
            return self
        if self._cached_point is not None:
            point = self._cached_point
        else:
            point = self._target.resolve()
        pyautogui.click(point.x, point.y)
        return self

    def wait(self, seconds: float) -> "Element":
        time.sleep(seconds)
        return self

    def write(self, text: str) -> "Element":
        """输入文本"""
        pyautogui.typewrite(text)
        return self
