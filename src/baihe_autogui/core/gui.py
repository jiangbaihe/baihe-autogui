from typing import Any, Iterable, Optional, Tuple, Type, cast


class PyAutoGuiUnavailableError(RuntimeError):
    """Raised when pyautogui cannot be imported in the current environment."""


class _ImageNotFoundFallbackError(Exception):
    """Fallback exception type used when pyautogui is unavailable during tests."""


class PyAutoGuiAdapter:
    def _pyautogui(self) -> Any:
        try:
            import pyautogui
        except Exception as exc:  # pragma: no cover - depends on runtime environment
            raise PyAutoGuiUnavailableError(
                "pyautogui is unavailable in the current environment"
            ) from exc
        return pyautogui

    def size(self) -> Tuple[int, int]:
        width, height = cast(Tuple[int, int], self._pyautogui().size())
        return (width, height)

    def move_to(self, x: int, y: int) -> None:
        self._pyautogui().moveTo(x, y)

    def move_by(self, dx: int, dy: int) -> None:
        self._pyautogui().moveRel(dx, dy)

    def click(self, x: int, y: int) -> None:
        self._pyautogui().click(x, y)

    def right_click(self, x: int, y: int) -> None:
        self._pyautogui().rightClick(x, y)

    def double_click(self, x: int, y: int) -> None:
        self._pyautogui().doubleClick(x, y)

    def typewrite(self, text: str) -> None:
        self._pyautogui().typewrite(text)

    def press(self, key: str) -> None:
        self._pyautogui().press(key)

    def hotkey(self, *keys: str) -> None:
        self._pyautogui().hotkey(*keys)

    def locate_center_on_screen(
        self,
        image,
        *,
        confidence: float,
        region: Optional[Tuple[int, int, int, int]],
    ):
        return self._pyautogui().locateCenterOnScreen(
            image,
            confidence=confidence,
            region=region,
        )

    def locate_on_screen(
        self,
        image,
        *,
        confidence: float,
        region: Optional[Tuple[int, int, int, int]],
    ):
        return self._pyautogui().locateOnScreen(
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
        return cast(
            Iterable[object],
            self._pyautogui().locateAllOnScreen(
                image,
                confidence=confidence,
                region=region,
            ),
        )

    @property
    def image_not_found_exception(self) -> Type[Exception]:
        try:
            return cast(Type[Exception], self._pyautogui().ImageNotFoundException)
        except PyAutoGuiUnavailableError:
            return _ImageNotFoundFallbackError


gui = PyAutoGuiAdapter()
