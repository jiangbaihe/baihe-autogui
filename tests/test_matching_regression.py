from pathlib import Path

import pyscreeze
import pytest
from PIL import Image

from baihe_autogui.core.auto import Auto

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
NORMAL_CLOSE_TAB = FIXTURE_DIR / "btn_close_tab.png"
FOCUS_CLOSE_TAB = FIXTURE_DIR / "btn_close_tab_focus.png"


def _build_tab_strip_haystack() -> Image.Image:
    haystack = Image.new("RGBA", (500, 80), (240, 240, 240, 255))
    with Image.open(NORMAL_CLOSE_TAB).convert("RGBA") as normal:
        haystack.alpha_composite(normal, (120, 20))
    with Image.open(FOCUS_CLOSE_TAB).convert("RGBA") as focus:
        haystack.alpha_composite(focus, (320, 20))
    return haystack


def _import_pyautogui_or_skip():
    try:
        import pyautogui
    except Exception as exc:  # pragma: no cover - depends on test environment
        pytest.skip(f"pyautogui import unavailable in this environment: {exc}")
    return pyautogui


def test_fixture_focus_icon_produces_duplicate_raw_matches():
    haystack = _build_tab_strip_haystack()
    with Image.open(FOCUS_CLOSE_TAB).convert("RGBA") as needle:
        matches = list(pyscreeze.locateAll(needle, haystack, confidence=0.8))
    assert len(matches) > 1


def test_pyautogui_raw_locate_all_for_normal_close_tab_fixture():
    pyautogui = _import_pyautogui_or_skip()
    haystack = _build_tab_strip_haystack()
    with Image.open(NORMAL_CLOSE_TAB).convert("RGBA") as needle:
        matches = list(pyautogui.locateAll(needle, haystack, confidence=0.8))

    assert len(matches) == 1
    assert (matches[0].left, matches[0].top, matches[0].width, matches[0].height) == (
        120,
        20,
        13,
        13,
    )


def test_pyautogui_raw_locate_all_for_focus_close_tab_fixture_with_confidence():
    pyautogui = _import_pyautogui_or_skip()
    haystack = _build_tab_strip_haystack()
    with Image.open(FOCUS_CLOSE_TAB).convert("RGBA") as needle:
        matches = list(pyautogui.locateAll(needle, haystack, confidence=0.8))

    assert len(matches) == 6
    assert [
        (match.left, match.top, match.width, match.height)
        for match in matches
    ] == [
        (319, 20, 13, 13),
        (320, 20, 13, 13),
        (321, 20, 13, 13),
        (319, 21, 13, 13),
        (320, 21, 13, 13),
        (321, 21, 13, 13),
    ]


def test_locate_all_dedupes_real_close_tab_icons(monkeypatch):
    haystack = _build_tab_strip_haystack()

    def locate_all_on_screen(image, *, confidence, region):
        del region
        return pyscreeze.locateAll(image, haystack, confidence=confidence)

    monkeypatch.setattr(
        "baihe_autogui.core.target.gui.locate_all_on_screen",
        locate_all_on_screen,
    )

    auto = Auto()
    elements = auto.locate_all([NORMAL_CLOSE_TAB, FOCUS_CLOSE_TAB], confidence=0.8)

    assert len(elements) == 2
    assert [element._cached_region for element in elements] == [
        (120, 20, 13, 13),
        (319, 20, 13, 13),
    ]
