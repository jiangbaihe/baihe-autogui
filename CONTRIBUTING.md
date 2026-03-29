# Contributing

This is the project's single developer manual. It is written to help AI agents take over quickly, but human developers should be able to read it directly as well.

## Project Positioning

`baihe-autogui` is a lightweight GUI automation library built on top of `pyautogui`, centered around a clear `Auto -> Element -> Target` flow.

Project priorities:

- Keep the API small and intuitive
- Prefer clear chain semantics over broad abstraction
- Favor stable semantics over clever compatibility tricks

## Current Core Semantics

- Runtime support is `Python >=3.8`
- Local development, CI, and release validation stay on Python `3.8`
- Python `3.8` remains the development baseline because it is the last Python version that still runs on Windows 7
- Coordinates are always absolute screen coordinates
- `region=(x, y, w, h)` only limits the search area; it does not switch to local coordinates
- Target existence means the target is fully inside the search region, not merely intersecting it
- `locate()` resolves lazily, only when an action needs the position
- `locate_all()` snapshots image matches and caches point / region data
- `locate([...])` tries locators in order; `locate_all([...])` expands all results in order
- Empty locator lists are invalid and should raise `ValidationError`

## Mouse And Element Semantics

- `Auto.move_to(x, y)` moves to an absolute screen coordinate
- `Auto.move_by(dx, dy)` moves relative to the current mouse position
- `Element.hover(anchor="center", dx=0, dy=0)` moves to the element anchor
- `Element.click()` / `right_click()` / `double_click()` share the same `anchor` / `dx` / `dy` semantics as `hover()`
- `Element` no longer keeps a `move_to()` method with a different coordinate frame than `Auto`
- Supported anchors: `top_left`, `top`, `top_right`, `left`, `center`, `right`, `bottom_left`, `bottom`, `bottom_right`
- Point targets only support `anchor="center"`; any other explicit anchor should raise `ValidationError`

## Conditional Chain Semantics

- `exists()` only returns a boolean and does not change chain state
- Once `if_exists()` determines the target is missing, the entire remaining chain is skipped
- On a skipped chain:
  - waits, keyboard actions, and mouse actions are skipped
  - `locate()` keeps returning the same skipped `Element`
  - `locate_all()` returns `[]`

## Debug Highlight Semantics

- `Element.highlight()` draws a temporary debug overlay
- `Element.clear_highlight()` clears only that element's own highlight
- `Auto.clear_highlights()` clears every active highlight
- The current highlight backend uses `pywin32` with Win32 overlay windows
- Region / image targets render as soft red frames; point targets render as soft red crosshairs by default
- Named colors such as `red`, `green`, and `yellow` should stay on the softer palette instead of fully saturated primaries
- This is a current platform-specific capability and should not be treated as a cross-platform guarantee

## Packaging And Extension Semantics

- `baihe-autogui` is the primary package users install
- `baihe-autogui-inspect` is a separate companion package exposed here through the optional `inspect` extra
- Keep `extra` as a compatibility alias for the same extension set
- The inspect extension is responsible for `PySide6` policy; the main package should not grow a direct Qt dependency
- The main package should remain releasable without a checked-out inspect workspace
- The `inspect` / `extra` dependency range should target a compatible inspect release line, not be bumped for every inspect patch by default
- Current compatibility policy is:
  - Python `3.8` installs inspect with `PySide6==6.1.3` for Win7-oriented compatibility
  - Python `3.9+` installs inspect with a newer compatible `PySide6`

## Release Order Policy

- `baihe-autogui` can be released on its own at any time
- Compatible inspect-only patch releases should not force a follow-up main-package release
- If inspect requires a new main-package capability, release `baihe-autogui` first and then release `baihe-autogui-inspect`
- Only bump the main package's `inspect` / `extra` dependency floor when the previous compatible inspect line is no longer acceptable for users

## Repository Landmarks

- `src/baihe_autogui/core/auto.py`: user entry point and target creation
- `src/baihe_autogui/core/element.py`: chain actions, conditional control, nested locate, highlight
- `src/baihe_autogui/core/target.py`: point / region / image / multi-locator semantics
- `src/baihe_autogui/core/overlay.py`: debug highlight overlay lifecycle
- `tests/`: regression coverage
- `README.md` / `README_zh.md`: user-facing docs
- `CHANGELOG.md`: version history

## Collaboration Rules

- When user-visible behavior changes, update `README.md`, `README_zh.md`, and `CHANGELOG.md`
- When API semantics change, add tests for success paths, failure paths, and edge inputs
- Prefer mocking the `gui` adapter instead of relying on a real desktop environment in tests
- Do not commit real business screenshots, real button assets, or real business automation scripts into the public repo

## Common Commands

```bash
uv sync --dev
uv run pytest -q
uv run ruff check .
uv run mypy src tests
uv run pre-commit run --all-files
uv build
```

## Local Constraints

- Local development and release validation stay on Python `3.8`
- Published artifacts support `Python >=3.8`
- For Windows / headless CI issues, prefer solving them by mocking the `gui` adapter
- GitHub Actions test/build jobs run on Windows to match the project's actual automation platform

## Release Checklist

1. Update code, tests, and docs.
2. Update the version in `pyproject.toml`.
3. Refresh `uv.lock` if the version or dependencies changed.
4. Move the relevant notes from `CHANGELOG.md` under `Unreleased` into a new version section.
5. Run local checks:

```bash
git status --short --branch
uv sync --dev
uv run pytest -q
uv run ruff check .
uv run mypy src tests
uv build
```

6. If needed, run the wheel smoke check:

```bash
uv run --python 3.8 --no-project --with ./dist/*.whl python scripts/smoke_import.py
```

## Publish Flow

1. Commit the release changes.
2. Push the branch first.
3. Confirm `HEAD`, then create the `vX.Y.Z` tag.
4. Push the tag to trigger the GitHub Actions `Release` workflow.
5. The workflow builds, tests, runs the smoke check, and publishes through PyPI Trusted Publishing.

## Release Notes

- Do not treat commit and tag creation as parallel steps
- Do not push a tag before confirming it points at the intended `HEAD`
- If a release fails, check the remote tag target first, then inspect workflow and PyPI configuration

## Suggested Read Order

1. `git status --short --branch`
2. `README.md`
3. `README_zh.md`
4. `pyproject.toml`
5. This file
