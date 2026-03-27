# baihe-autogui

A small GUI automation wrapper around `pyautogui` with a simple `Auto -> Element -> Target` flow.

## Installation

```bash
uv sync
```

## Examples

- [quick_start.py](examples/quick_start.py) shows the common mouse and keyboard flow.
- [conditional_flow.py](examples/conditional_flow.py) shows optional actions and exception handling.

## Quick Start

```python
from baihe_autogui import Auto

auto = Auto()

# Locate by point
auto.locate((100, 200)).click()

# Locate by region (clicks center point)
auto.locate((100, 200, 80, 30)).click()

# Locate by image
auto.locate('button.png').move_to().click().wait(0.5).write('hello')
auto.locate('button.png').right_click()
auto.locate('button.png').double_click().press('enter')
auto.locate('button.png').hotkey('ctrl', 'a').write('replacement')

# Conditional execution
auto.locate('button.png').if_exists().click()
auto.locate('button.png').wait_until_exists(timeout=5).click()
auto.locate('button.png').assert_exists().click()

# Get all matches
for e in auto.locate_all('button.png'):
    e.click()
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
- `move_to()` / `click()` / `right_click()` / `double_click()` - Mouse actions
- `wait()` / `write()` - General actions
- `press()` / `hotkey()` - Keyboard actions
- `if_exists()` / `wait_until_exists()` / `assert_exists()` - Conditional methods

### Auto

Main entry point. `locate()` returns one `Element`; `locate_all()` returns a list and yields `[]` when an image is not found.

## API Reference

### locate()

```python
auto.locate(target, *, region=None, confidence=0.8, timeout=0, retry=0)
```

- `target`: Point `(x, y)`, Region `(x, y, w, h)`, or image path
- `region`: Search region `(x, y, w, h)`, defaults to full screen
- `confidence`: Image match confidence (0.0-1.0)
- `timeout`: Seconds between retry attempts
- `retry`: Number of retries (0 = no retry)
- Point and region tuples must contain integers
- Region width and height must be greater than 0

### Element Actions

```python
element.move_to()         # Move the cursor to the target
element.click()           # Click at target location
element.right_click()     # Right-click at target location
element.double_click()    # Double-click at target location
element.wait(seconds)     # Wait
element.write(text)       # Type text
element.press("enter")    # Press a single key
element.hotkey("ctrl", "c")  # Press a key combination
element.if_exists()      # Skip if element doesn't exist
element.wait_until_exists(timeout=10)  # Wait until appears
element.assert_exists()  # Assert element must exist
```

### Exceptions

- `ValidationError` - Invalid input such as malformed tuples or bad retry settings
- `ElementNotFoundError` - A required element was missing for an immediate action
- `ElementTimeoutError` - Waiting for a required element timed out
- `ImageNotFoundError` - An image target could not be matched

## Development

```bash
uv sync --dev
uv run pytest -q
uv run ruff check .
uv build
```

GitHub Actions runs the same checks on pushes and pull requests with Python 3.8.
Contribution notes live in [CONTRIBUTING.md](CONTRIBUTING.md).

## Architecture

- `locate()` resolves lazily, only when an action needs the position
- `locate_all()` snapshots matched image positions and reuses cached points
- Targets must be fully within the search region
