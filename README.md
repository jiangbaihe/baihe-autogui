# baihe-autogui

A small GUI automation wrapper around `pyautogui` with a simple `Auto -> Element -> Target` flow.

## Installation

```bash
uv sync
```

## Quick Start

```python
from baihe_autogui import Auto

auto = Auto()

# Locate by point
auto.locate((100, 200)).click()

# Locate by region (clicks center point)
auto.locate((100, 200, 80, 30)).click()

# Locate by image
auto.locate('button.png').click().wait(0.5).write('hello')

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
- `click()` / `wait()` / `write()` - Chainable actions
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
- `timeout`: Seconds between retries
- `retry`: Number of retries (0 = no retry)
- Point and region tuples must contain integers
- Region width and height must be greater than 0

### Element Actions

```python
element.click()           # Click at target location
element.wait(seconds)     # Wait
element.write(text)       # Type text
element.if_exists()      # Skip if element doesn't exist
element.wait_until_exists(timeout=10)  # Wait until appears
element.assert_exists()  # Assert element must exist
```

## Architecture

- `locate()` resolves lazily, only when an action needs the position
- `locate_all()` snapshots matched image positions and reuses cached points
- Targets must be fully within the search region
