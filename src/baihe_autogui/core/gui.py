from typing import Iterable, Optional, Tuple

import pyautogui


class PyAutoGuiAdapter:
    def size(self) -> Tuple[int, int]:
        return pyautogui.size()

    def move_to(self, x: int, y: int) -> None:
        pyautogui.moveTo(x, y)

    def click(self, x: int, y: int) -> None:
        pyautogui.click(x, y)

    def right_click(self, x: int, y: int) -> None:
        pyautogui.rightClick(x, y)

    def double_click(self, x: int, y: int) -> None:
        pyautogui.doubleClick(x, y)

    def typewrite(self, text: str) -> None:
        pyautogui.typewrite(text)

    def press(self, key: str) -> None:
        pyautogui.press(key)

    def hotkey(self, *keys: str) -> None:
        pyautogui.hotkey(*keys)

    def locate_center_on_screen(
        self,
        image,
        *,
        confidence: float,
        region: Optional[Tuple[int, int, int, int]],
    ):
        return pyautogui.locateCenterOnScreen(
            image,
            confidence=confidence,
            region=region,
        )

    def locate_all_on_screen(
        self,
        image,
        *,
        confidence: float,
        region: Optional[Tuple[int, int, int, int]],
    ) -> Iterable[object]:
        return pyautogui.locateAllOnScreen(
            image,
            confidence=confidence,
            region=region,
        )

    @property
    def image_not_found_exception(self):
        return pyautogui.ImageNotFoundException


gui = PyAutoGuiAdapter()
