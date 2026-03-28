import atexit
import ctypes
import queue
import sys
import threading
import time
from ctypes import wintypes
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .exceptions import OverlayUnavailableError
from .target import Point

Color = str


@dataclass(frozen=True)
class HighlightSpec:
    kind: str
    color: Color
    thickness: int
    point: Optional[Point] = None
    region: Optional[Tuple[int, int, int, int]] = None


if sys.platform == "win32":
    LRESULT = ctypes.c_ssize_t
    HANDLE = wintypes.HANDLE
    HBRUSH = HANDLE
    HGDIOBJ = HANDLE
    WM_DESTROY = 0x0002
    WM_PAINT = 0x000F
    WM_ERASEBKGND = 0x0014
    WM_NCHITTEST = 0x0084
    HTTRANSPARENT = -1
    CS_HREDRAW = 0x0002
    CS_VREDRAW = 0x0001
    WS_POPUP = 0x80000000
    WS_EX_LAYERED = 0x00080000
    WS_EX_TOPMOST = 0x00000008
    WS_EX_TOOLWINDOW = 0x00000080
    WS_EX_TRANSPARENT = 0x00000020
    WS_EX_NOACTIVATE = 0x08000000
    LWA_COLORKEY = 0x00000001
    PM_REMOVE = 0x0001
    SW_SHOWNOACTIVATE = 4
    PS_SOLID = 0
    HOLLOW_BRUSH = 5
    TRANSPARENT = 1

    class PAINTSTRUCT(ctypes.Structure):
        _fields_ = [
            ("hdc", wintypes.HDC),
            ("fErase", wintypes.BOOL),
            ("rcPaint", wintypes.RECT),
            ("fRestore", wintypes.BOOL),
            ("fIncUpdate", wintypes.BOOL),
            ("rgbReserved", ctypes.c_ubyte * 32),
        ]

    WNDPROC = ctypes.WINFUNCTYPE(
        LRESULT,
        wintypes.HWND,
        wintypes.UINT,
        wintypes.WPARAM,
        wintypes.LPARAM,
    )

    class WNDCLASSW(ctypes.Structure):
        _fields_ = [
            ("style", wintypes.UINT),
            ("lpfnWndProc", WNDPROC),
            ("cbClsExtra", ctypes.c_int),
            ("cbWndExtra", ctypes.c_int),
            ("hInstance", wintypes.HINSTANCE),
            ("hIcon", HANDLE),
            ("hCursor", HANDLE),
            ("hbrBackground", HBRUSH),
            ("lpszMenuName", wintypes.LPCWSTR),
            ("lpszClassName", wintypes.LPCWSTR),
        ]

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
    kernel32.GetModuleHandleW.restype = wintypes.HINSTANCE

    user32.RegisterClassW.argtypes = [ctypes.POINTER(WNDCLASSW)]
    user32.RegisterClassW.restype = ctypes.c_ushort
    user32.CreateWindowExW.argtypes = [
        wintypes.DWORD,
        wintypes.LPCWSTR,
        wintypes.LPCWSTR,
        wintypes.DWORD,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.HWND,
        wintypes.HMENU,
        wintypes.HINSTANCE,
        wintypes.LPVOID,
    ]
    user32.CreateWindowExW.restype = wintypes.HWND
    user32.DefWindowProcW.argtypes = [
        wintypes.HWND,
        wintypes.UINT,
        wintypes.WPARAM,
        wintypes.LPARAM,
    ]
    user32.DefWindowProcW.restype = LRESULT
    user32.DestroyWindow.argtypes = [wintypes.HWND]
    user32.DestroyWindow.restype = wintypes.BOOL
    user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.ShowWindow.restype = wintypes.BOOL
    user32.UpdateWindow.argtypes = [wintypes.HWND]
    user32.UpdateWindow.restype = wintypes.BOOL
    user32.SetLayeredWindowAttributes.argtypes = [
        wintypes.HWND,
        wintypes.DWORD,
        ctypes.c_ubyte,
        wintypes.DWORD,
    ]
    user32.SetLayeredWindowAttributes.restype = wintypes.BOOL
    user32.BeginPaint.argtypes = [wintypes.HWND, ctypes.POINTER(PAINTSTRUCT)]
    user32.BeginPaint.restype = wintypes.HDC
    user32.EndPaint.argtypes = [wintypes.HWND, ctypes.POINTER(PAINTSTRUCT)]
    user32.EndPaint.restype = wintypes.BOOL
    user32.FillRect.argtypes = [
        wintypes.HDC,
        ctypes.POINTER(wintypes.RECT),
        HBRUSH,
    ]
    user32.FillRect.restype = ctypes.c_int
    user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user32.GetClientRect.restype = wintypes.BOOL
    user32.PeekMessageW.argtypes = [
        ctypes.POINTER(wintypes.MSG),
        wintypes.HWND,
        wintypes.UINT,
        wintypes.UINT,
        wintypes.UINT,
    ]
    user32.PeekMessageW.restype = wintypes.BOOL
    user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
    user32.TranslateMessage.restype = wintypes.BOOL
    user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
    user32.DispatchMessageW.restype = LRESULT
    user32.InvalidateRect.argtypes = [
        wintypes.HWND,
        ctypes.POINTER(wintypes.RECT),
        wintypes.BOOL,
    ]
    user32.InvalidateRect.restype = wintypes.BOOL

    gdi32.CreateSolidBrush.argtypes = [wintypes.DWORD]
    gdi32.CreateSolidBrush.restype = HBRUSH
    gdi32.DeleteObject.argtypes = [HGDIOBJ]
    gdi32.DeleteObject.restype = wintypes.BOOL
    gdi32.CreatePen.argtypes = [ctypes.c_int, ctypes.c_int, wintypes.DWORD]
    gdi32.CreatePen.restype = HGDIOBJ
    gdi32.SelectObject.argtypes = [wintypes.HDC, HGDIOBJ]
    gdi32.SelectObject.restype = HGDIOBJ
    gdi32.Rectangle.argtypes = [
        wintypes.HDC,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
    ]
    gdi32.Rectangle.restype = wintypes.BOOL
    gdi32.MoveToEx.argtypes = [
        wintypes.HDC,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.POINTER(wintypes.POINT),
    ]
    gdi32.MoveToEx.restype = wintypes.BOOL
    gdi32.LineTo.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
    gdi32.LineTo.restype = wintypes.BOOL
    gdi32.GetStockObject.argtypes = [ctypes.c_int]
    gdi32.GetStockObject.restype = HGDIOBJ
    gdi32.SetBkMode.argtypes = [wintypes.HDC, ctypes.c_int]
    gdi32.SetBkMode.restype = ctypes.c_int


def _rgb(red: int, green: int, blue: int) -> int:
    return red | (green << 8) | (blue << 16)


def _parse_color(color: Color) -> int:
    named_colors = {
        "red": (255, 0, 0),
        "lime": (0, 255, 0),
        "green": (0, 128, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
        "cyan": (0, 255, 255),
        "white": (255, 255, 255),
        "orange": (255, 165, 0),
    }
    normalized = color.strip().lower()
    if normalized in named_colors:
        return _rgb(*named_colors[normalized])
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
        self._queue = queue.Queue()
        self._ready = threading.Event()
        self._error: Optional[BaseException] = None
        self._class_name = "BaiheAutoGuiOverlayWindow"
        self._windows: Dict[str, int] = {}
        self._specs_by_hwnd: Dict[int, HighlightSpec] = {}
        self._wndproc = None
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
        instance = kernel32.GetModuleHandleW(None)
        if not instance:
            raise ctypes.WinError(ctypes.get_last_error())

        self._wndproc = WNDPROC(self._window_proc)
        window_class = WNDCLASSW()
        window_class.style = CS_HREDRAW | CS_VREDRAW
        window_class.lpfnWndProc = self._wndproc
        window_class.cbClsExtra = 0
        window_class.cbWndExtra = 0
        window_class.hInstance = instance
        window_class.hIcon = None
        window_class.hCursor = None
        window_class.hbrBackground = None
        window_class.lpszMenuName = None
        window_class.lpszClassName = self._class_name

        atom = user32.RegisterClassW(ctypes.byref(window_class))
        if atom == 0:
            error_code = ctypes.get_last_error()
            if error_code != 1410:  # class already exists
                raise ctypes.WinError(error_code)

    def _message_loop(self) -> None:
        message = wintypes.MSG()
        while True:
            self._process_queue()
            while user32.PeekMessageW(ctypes.byref(message), None, 0, 0, PM_REMOVE):
                user32.TranslateMessage(ctypes.byref(message))
                user32.DispatchMessageW(ctypes.byref(message))
            time.sleep(0.01)

    def _process_queue(self) -> None:
        while True:
            try:
                action, payload = self._queue.get_nowait()
            except queue.Empty:
                return
            if action == "add":
                highlight_id, spec = payload
                self._destroy_highlight(highlight_id)
                self._windows[highlight_id] = self._create_window(spec)
            elif action == "remove":
                self._destroy_highlight(payload[0])
            elif action == "clear":
                for highlight_id in list(self._windows):
                    self._destroy_highlight(highlight_id)

    def _create_window(self, spec: HighlightSpec) -> int:
        x, y, width, height = self._window_bounds(spec)
        instance = kernel32.GetModuleHandleW(None)
        hwnd = user32.CreateWindowExW(
            WS_EX_LAYERED
            | WS_EX_TOPMOST
            | WS_EX_TOOLWINDOW
            | WS_EX_TRANSPARENT
            | WS_EX_NOACTIVATE,
            self._class_name,
            "",
            WS_POPUP,
            x,
            y,
            width,
            height,
            None,
            None,
            instance,
            None,
        )
        if not hwnd:
            raise ctypes.WinError(ctypes.get_last_error())

        if not user32.SetLayeredWindowAttributes(
            hwnd, self._TRANSPARENT_COLOR, 0, LWA_COLORKEY
        ):
            raise ctypes.WinError(ctypes.get_last_error())

        self._specs_by_hwnd[hwnd] = spec
        user32.ShowWindow(hwnd, SW_SHOWNOACTIVATE)
        user32.InvalidateRect(hwnd, None, True)
        user32.UpdateWindow(hwnd)
        return int(hwnd)

    def _destroy_highlight(self, highlight_id: str) -> None:
        hwnd = self._windows.pop(highlight_id, None)
        if hwnd is None:
            return
        self._specs_by_hwnd.pop(hwnd, None)
        user32.DestroyWindow(hwnd)

    def _window_proc(self, hwnd, message, w_param, l_param):
        if message == WM_NCHITTEST:
            return HTTRANSPARENT
        if message == WM_ERASEBKGND:
            return 1
        if message == WM_PAINT:
            self._paint_window(hwnd)
            return 0
        if message == WM_DESTROY:
            self._specs_by_hwnd.pop(hwnd, None)
            return 0
        return user32.DefWindowProcW(hwnd, message, w_param, l_param)

    def _paint_window(self, hwnd) -> None:
        spec = self._specs_by_hwnd.get(hwnd)
        if spec is None:
            return

        paint = PAINTSTRUCT()
        hdc = user32.BeginPaint(hwnd, ctypes.byref(paint))
        try:
            rect = wintypes.RECT()
            user32.GetClientRect(hwnd, ctypes.byref(rect))
            background = gdi32.CreateSolidBrush(self._TRANSPARENT_COLOR)
            try:
                user32.FillRect(hdc, ctypes.byref(rect), background)
            finally:
                gdi32.DeleteObject(background)

            pen = gdi32.CreatePen(PS_SOLID, spec.thickness, _parse_color(spec.color))
            old_pen = gdi32.SelectObject(hdc, pen)
            old_brush = gdi32.SelectObject(hdc, gdi32.GetStockObject(HOLLOW_BRUSH))
            gdi32.SetBkMode(hdc, TRANSPARENT)
            try:
                if spec.kind == "region":
                    self._draw_region_frame(hdc, spec)
                else:
                    self._draw_point_cross(hdc, spec)
            finally:
                gdi32.SelectObject(hdc, old_pen)
                gdi32.SelectObject(hdc, old_brush)
                gdi32.DeleteObject(pen)
        finally:
            user32.EndPaint(hwnd, ctypes.byref(paint))

    def _draw_region_frame(self, hdc, spec: HighlightSpec) -> None:
        assert spec.region is not None
        _, _, width, height = spec.region
        padding = max(spec.thickness, 2)
        left = padding
        top = padding
        right = padding + width
        bottom = padding + height
        gdi32.Rectangle(hdc, left, top, right, bottom)

    def _draw_point_cross(self, hdc, spec: HighlightSpec) -> None:
        assert spec.point is not None
        arm = max(10, spec.thickness * 6)
        center = arm
        gdi32.MoveToEx(hdc, center - arm, center, None)
        gdi32.LineTo(hdc, center + arm + 1, center)
        gdi32.MoveToEx(hdc, center, center - arm, None)
        gdi32.LineTo(hdc, center, center + arm + 1)

    def _window_bounds(self, spec: HighlightSpec) -> Tuple[int, int, int, int]:
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
        self._app: Optional[_OverlayApp] = None
        self._lock = threading.Lock()
        self._next_id = 0
        self._timers: Dict[str, threading.Timer] = {}

    def add(self, spec: HighlightSpec, *, timeout: Optional[float]) -> str:
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
        self, highlight_id: str, timeout: Optional[float]
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
