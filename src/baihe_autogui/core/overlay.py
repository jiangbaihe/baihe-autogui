from __future__ import annotations

import atexit
import queue
import sys
import threading
import time
from dataclasses import dataclass

from .exceptions import OverlayUnavailableError
from .target import Point

Color = str


@dataclass(frozen=True)
class HighlightSpec:
    kind: str
    color: Color
    thickness: int
    point: Point | None = None
    region: tuple[int, int, int, int] | None = None


if sys.platform == "win32":
    import win32api
    import win32con
    import win32gui


_NAMED_COLORS = {
    "red": "#f87171",
    "lime": "#84cc16",
    "green": "#4ade80",
    "blue": "#60a5fa",
    "yellow": "#facc15",
    "cyan": "#67e8f9",
    "white": "#f8fafc",
    "orange": "#fb923c",
}


def _rgb(red: int, green: int, blue: int) -> int:
    if sys.platform == "win32":
        return int(win32api.RGB(red, green, blue))
    return red | (green << 8) | (blue << 16)


def _parse_color(color: Color) -> int:
    normalized = color.strip().lower()
    if normalized in _NAMED_COLORS:
        normalized = _NAMED_COLORS[normalized]
    if normalized.startswith("#") and len(normalized) == 7:
        return _rgb(
            int(normalized[1:3], 16),
            int(normalized[3:5], 16),
            int(normalized[5:7], 16),
        )
    raise ValueError("highlight color must be a known name or #RRGGBB")


class _OverlayApp:
    _TRANSPARENT_COLOR = _rgb(255, 0, 255)

    def __init__(self):
        self._queue: queue.Queue[tuple[str, tuple[object, ...]]] = queue.Queue()
        self._ready = threading.Event()
        self._error: BaseException | None = None
        self._class_name = "BaiheAutoGuiOverlayWindow"
        self._windows: dict[str, int] = {}
        self._specs_by_hwnd: dict[int, HighlightSpec] = {}
        self._thread = threading.Thread(
            target=self._run, name="baihe-overlay", daemon=True
        )
        self._thread.start()
        self._ready.wait()
        if self._error is not None:
            raise OverlayUnavailableError(
                "highlight overlay is unavailable in the current environment"
            ) from self._error

    def add(self, highlight_id: str, spec: HighlightSpec) -> None:
        self._queue.put(("add", (highlight_id, spec)))

    def remove(self, highlight_id: str) -> None:
        self._queue.put(("remove", (highlight_id,)))

    def clear(self) -> None:
        self._queue.put(("clear", ()))

    def _run(self) -> None:
        if sys.platform != "win32":
            self._error = RuntimeError(
                "highlight overlay currently requires Windows with Win32 support"
            )
            self._ready.set()
            return

        try:
            self._register_window_class()
            self._ready.set()
            self._message_loop()
        except Exception as exc:
            self._error = exc
            self._ready.set()

    def _register_window_class(self) -> None:
        instance = win32api.GetModuleHandle(None)
        window_class = win32gui.WNDCLASS()
        window_class.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        window_class.lpfnWndProc = self._window_proc
        window_class.cbClsExtra = 0
        window_class.cbWndExtra = 0
        window_class.hInstance = instance
        window_class.hIcon = 0
        window_class.hCursor = 0
        window_class.hbrBackground = 0
        window_class.lpszMenuName = None
        window_class.lpszClassName = self._class_name

        try:
            win32gui.RegisterClass(window_class)
        except win32gui.error as exc:
            if exc.winerror != 1410:
                raise

    def _message_loop(self) -> None:
        while True:
            self._process_queue()
            win32gui.PumpWaitingMessages()
            time.sleep(0.01)

    def _process_queue(self) -> None:
        while True:
            try:
                action, payload = self._queue.get_nowait()
            except queue.Empty:
                return
            if action == "add":
                highlight_id, spec = payload
                self._destroy_highlight(str(highlight_id))
                self._windows[str(highlight_id)] = self._create_window(spec)  # type: ignore[arg-type]
            elif action == "remove":
                self._destroy_highlight(str(payload[0]))
            elif action == "clear":
                for highlight_id in list(self._windows):
                    self._destroy_highlight(highlight_id)

    def _create_window(self, spec: HighlightSpec) -> int:
        x, y, width, height = self._window_bounds(spec)
        hwnd = win32gui.CreateWindowEx(
            win32con.WS_EX_LAYERED
            | win32con.WS_EX_TOPMOST
            | win32con.WS_EX_TOOLWINDOW
            | win32con.WS_EX_TRANSPARENT
            | win32con.WS_EX_NOACTIVATE,
            self._class_name,
            "",
            win32con.WS_POPUP,
            x,
            y,
            width,
            height,
            0,
            0,
            win32api.GetModuleHandle(None),
            None,
        )
        win32gui.SetLayeredWindowAttributes(
            hwnd,
            self._TRANSPARENT_COLOR,
            0,
            win32con.LWA_COLORKEY,
        )
        self._specs_by_hwnd[hwnd] = spec
        win32gui.ShowWindow(hwnd, win32con.SW_SHOWNOACTIVATE)
        win32gui.InvalidateRect(hwnd, None, True)
        win32gui.UpdateWindow(hwnd)
        return int(hwnd)

    def _destroy_highlight(self, highlight_id: str) -> None:
        hwnd = self._windows.pop(highlight_id, None)
        if hwnd is None:
            return
        self._specs_by_hwnd.pop(hwnd, None)
        win32gui.DestroyWindow(hwnd)

    def _window_proc(self, hwnd, message, w_param, l_param):
        if message == win32con.WM_NCHITTEST:
            return win32con.HTTRANSPARENT
        if message == win32con.WM_ERASEBKGND:
            return 1
        if message == win32con.WM_PAINT:
            self._paint_window(hwnd)
            return 0
        if message == win32con.WM_DESTROY:
            self._specs_by_hwnd.pop(hwnd, None)
            return 0
        return win32gui.DefWindowProc(hwnd, message, w_param, l_param)

    def _paint_window(self, hwnd: int) -> None:
        spec = self._specs_by_hwnd.get(hwnd)
        if spec is None:
            return

        hdc, paint_struct = win32gui.BeginPaint(hwnd)
        try:
            background = win32gui.CreateSolidBrush(self._TRANSPARENT_COLOR)
            try:
                win32gui.FillRect(hdc, win32gui.GetClientRect(hwnd), background)
            finally:
                win32gui.DeleteObject(background)

            pen = win32gui.CreatePen(
                win32con.PS_SOLID, spec.thickness, _parse_color(spec.color)
            )
            old_pen = win32gui.SelectObject(hdc, pen)
            old_brush = win32gui.SelectObject(
                hdc, win32gui.GetStockObject(win32con.NULL_BRUSH)
            )
            win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
            try:
                if spec.kind == "region":
                    self._draw_region_frame(hdc, spec)
                else:
                    self._draw_point_cross(hdc, spec)
            finally:
                win32gui.SelectObject(hdc, old_pen)
                win32gui.SelectObject(hdc, old_brush)
                win32gui.DeleteObject(pen)
        finally:
            win32gui.EndPaint(hwnd, paint_struct)

    def _draw_region_frame(self, hdc: int, spec: HighlightSpec) -> None:
        assert spec.region is not None
        _, _, width, height = spec.region
        padding = max(spec.thickness, 2)
        left = padding
        top = padding
        right = padding + width
        bottom = padding + height
        win32gui.Rectangle(hdc, left, top, right, bottom)

    def _draw_point_cross(self, hdc: int, spec: HighlightSpec) -> None:
        assert spec.point is not None
        arm = max(10, spec.thickness * 6)
        center = arm
        win32gui.MoveToEx(hdc, center - arm, center)
        win32gui.LineTo(hdc, center + arm + 1, center)
        win32gui.MoveToEx(hdc, center, center - arm)
        win32gui.LineTo(hdc, center, center + arm + 1)

    def _window_bounds(self, spec: HighlightSpec) -> tuple[int, int, int, int]:
        if spec.kind == "region":
            assert spec.region is not None
            x, y, width, height = spec.region
            padding = max(spec.thickness, 2)
            return (
                x - padding,
                y - padding,
                width + padding * 2 + 1,
                height + padding * 2 + 1,
            )

        assert spec.point is not None
        arm = max(10, spec.thickness * 6)
        size = arm * 2 + 1
        return (spec.point.x - arm, spec.point.y - arm, size, size)


class OverlayManager:
    def __init__(self):
        self._app: _OverlayApp | None = None
        self._lock = threading.Lock()
        self._next_id = 0
        self._timers: dict[str, threading.Timer] = {}

    def add(self, spec: HighlightSpec, *, timeout: float | None) -> str:
        with self._lock:
            self._next_id += 1
            highlight_id = f"highlight-{self._next_id}"
            self._get_app().add(highlight_id, spec)
            self._schedule_timeout_locked(highlight_id, timeout)
            return highlight_id

    def remove(self, highlight_id: str) -> None:
        with self._lock:
            self._cancel_timer_locked(highlight_id)
            if self._app is not None:
                self._app.remove(highlight_id)

    def remove_many(self, highlight_ids) -> None:
        for highlight_id in list(highlight_ids):
            self.remove(highlight_id)

    def clear(self) -> None:
        with self._lock:
            for timer in self._timers.values():
                timer.cancel()
            self._timers.clear()
            if self._app is not None:
                self._app.clear()

    def _get_app(self) -> _OverlayApp:
        if self._app is None:
            self._app = _OverlayApp()
        return self._app

    def _schedule_timeout_locked(
        self, highlight_id: str, timeout: float | None
    ) -> None:
        if timeout is None:
            return
        timer = threading.Timer(timeout, self.remove, args=(highlight_id,))
        timer.daemon = True
        self._timers[highlight_id] = timer
        timer.start()

    def _cancel_timer_locked(self, highlight_id: str) -> None:
        timer = self._timers.pop(highlight_id, None)
        if timer is not None:
            timer.cancel()


overlay = OverlayManager()
atexit.register(overlay.clear)
