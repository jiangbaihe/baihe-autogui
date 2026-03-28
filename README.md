# baihe-autogui

A small GUI automation wrapper around `pyautogui` with a simple `Auto -> Element -> Target` flow.

## Installation

```bash
uv add baihe-autogui
```

or

```bash
pip install baihe-autogui
```

To install the inspect companion tool together with the main package:

```bash
uv add "baihe-autogui[inspect]"
```

or

```bash
pip install "baihe-autogui[inspect]"
```

`baihe-autogui[extra]` is kept as a compatibility alias for the same extension set.

`opencv-python` is installed as a package dependency, so image matching with `confidence=...` works without extra manual setup.
Windows only.
Supports `Python >=3.8`.

## Examples

- [quick_start.py](examples/quick_start.py) shows the common mouse and keyboard flow.
- [conditional_flow.py](examples/conditional_flow.py) shows optional actions and exception handling.

## Quick Start

```python
from baihe_autogui import Auto

auto = Auto()

# Global mouse movement
auto.move_to(100, 200)
auto.move_by(20, -10)

# Locate by point
auto.locate((100, 200)).click()

# Locate by region (clicks center point)
auto.locate((100, 200, 80, 30)).click()
auto.locate((100, 200, 80, 30)).hover(anchor="top_right")
auto.locate((100, 200, 80, 30)).click(anchor="bottom", dy=-2)

# Locate by image
auto.locate('button.png').hover().click().wait(0.5).write('hello')
auto.locate('button.png').right_click()
auto.locate('button.png').double_click().press('enter')
auto.locate('button.png').hotkey('ctrl', 'a').write('replacement')
auto.locate('button.png').highlight(timeout=1.5).click()

# Conditional execution
auto.locate('button.png').if_exists().click()
auto.locate('button.png').wait_until_exists(timeout=5).click()
auto.locate('button.png').assert_exists().click()
if auto.locate('button.png').exists():
    auto.locate('button.png').click()

# Nested search inside a matched region
auto.locate('dialog.png').locate('confirm.png').click()

# Try multiple locator types in order
auto.locate([
    'primary_button.png',
    'fallback_button.png',
    (100, 200),
]).click()

# Get all matches
for e in auto.locate_all('button.png'):
    e.click()

# Gather results from multiple locators
for e in auto.locate_all(['button.png', 'secondary_button.png', (100, 200)]):
    e.click()

# Highlight and clear overlays
submit = auto.locate('submit.png')
submit.highlight(timeout=5)
submit.clear_highlight()
auto.clear_highlights()
```

## Core Concepts

### Target

Abstraction for locating targets on screen:
- `PointTarget` - Point coordinate targeting
- `RegionTarget` - Region targeting (returns center point)
- `ImageTarget` - Image matching targeting

All targets support `search_region`, and a target only counts as existing when it is fully inside that region.

### Element

Chainable action wrapper created by `Auto.locate()`:
- `hover()` / `click()` / `right_click()` / `double_click()` - Element mouse actions with optional `anchor`, `dx`, and `dy`
- `wait()` / `write()` - General actions
- `press()` / `hotkey()` - Keyboard actions
- `highlight()` / `clear_highlight()` - Debug overlay actions
- `locate()` / `locate_all()` - Scope a follow-up search to the current image or region
- `exists()` - Boolean existence check
- `if_exists()` / `wait_until_exists()` / `assert_exists()` - Conditional methods

### Auto

Main entry point. `move_to(x, y)` moves to an absolute screen coordinate, `move_by(dx, dy)` applies a relative mouse move, `locate()` returns one `Element`, and `locate_all()` returns a list that yields `[]` when an image is not found. `clear_highlights()` clears every active debug overlay.

## API Reference

### locate()

```python
auto.locate(target, *, region=None, confidence=0.8, timeout=0, retry=0)
```

- `target`: Point `(x, y)`, Region `(x, y, w, h)`, image path, or a list mixing those locator types
- `region`: Search region `(x, y, w, h)`, defaults to full screen
- `confidence`: Image match confidence (0.0-1.0)
- `timeout`: Seconds between retry attempts
- `retry`: Number of retries (0 = no retry)
- Point and region tuples must contain integers
- Region width and height must be greater than 0
- Non-empty locator lists are tried in order for `locate()`
- `locate_all()` flattens the results from each locator in input order
- `locate_all()` deduplicates heavily overlapping image matches before returning `Element` objects

### Element Actions

```python
auto.move_to(100, 200)   # Move to an absolute screen coordinate
auto.move_by(20, -10)    # Move relative to the current cursor position
element.hover(anchor="center", dx=0, dy=0)  # Move to the target anchor
element.click(anchor="center", dx=0, dy=0)  # Click at the target anchor
element.right_click(anchor="center", dx=0, dy=0)  # Right-click at the target anchor
element.double_click(anchor="center", dx=0, dy=0)  # Double-click at the target anchor
element.wait(seconds)     # Wait
element.write(text)       # Type text
element.press("enter")    # Press a single key
element.hotkey("ctrl", "c")  # Press a key combination
element.highlight(timeout=1.5, color="red", thickness=2)  # Draw a temporary overlay
element.clear_highlight()  # Clear this element's overlay
element.locate("inner.png")  # Search inside the current image or region
element.locate_all("item.png")  # Search all matches inside the current image or region
element.exists()         # Return True/False without changing chain behavior
element.if_exists()      # Skip if element doesn't exist
element.wait_until_exists(timeout=10)  # Wait until appears
element.assert_exists()  # Assert element must exist
auto.clear_highlights()  # Clear every active overlay
```

Nested locate uses the current image match box or region tuple as the next `region=...`.
Point targets do not define an area, so they cannot be used as an outer scope.
`exists()` only checks the current target and returns `True` or `False`.
Once `if_exists()` encounters a missing target, the rest of that chain is skipped, including `wait()`, keyboard actions, and nested `locate()` calls. In that skipped state, `locate()` keeps returning the same skipped `Element`, while `locate_all()` returns `[]`.
`anchor` supports `top_left`, `top`, `top_right`, `left`, `center`, `right`, `bottom_left`, `bottom`, and `bottom_right`.
`dx` and `dy` are always applied as screen-space offsets after the anchor point is resolved.
Point targets only support `anchor="center"` because a single point does not define a nine-grid area.
`highlight()` reuses cached points or regions when available so the visible overlay matches follow-up actions.
Point highlights are drawn as red crosshairs, while region and image highlights are drawn as red frames.
The current overlay backend is implemented with native Win32 windows.
If the current environment cannot provide the overlay backend, `highlight()` raises `OverlayUnavailableError`.

### Coordinate Semantics

- `region=(x, y, w, h)` limits the search area, but does not switch to a local coordinate system.
- Image matches still resolve to screen-space absolute coordinates.
- Nested `locate()` reuses the outer absolute region for the next search.
- `auto.move_to()`, `element.hover()`, `click()`, and other mouse actions always use absolute screen coordinates.

### Exceptions

- `ValidationError` - Invalid input such as malformed tuples or bad retry settings
- `ElementNotFoundError` - A required element was missing for an immediate action
- `ElementTimeoutError` - Waiting for a required element timed out
- `ImageNotFoundError` - An image target could not be matched
- `OverlayUnavailableError` - A debug highlight overlay could not be created in the current environment
- `__version__` - Installed package version string exposed at the package root

## Notes

- `locate()` resolves lazily, only when an action needs the position.
- `locate_all()` snapshots image matches and reuses cached points.
- Targets must be fully within the search region to count as existing.

For development and release workflows, see [CONTRIBUTING.md](CONTRIBUTING.md).
