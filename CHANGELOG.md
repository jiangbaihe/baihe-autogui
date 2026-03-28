# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.15] - 2026-03-29

### Fixed
- Decoupled the main package release workflow from a checked-out inspect workspace so tag-driven releases can build against publishable package metadata instead of local editable sibling state.
- Temporarily narrowed the optional `inspect` / `extra` dependency to the currently published companion line on Python 3.8, which keeps the release chain unblocked while the refreshed inspect package is published separately.

## [0.1.14] - 2026-03-29

### Fixed
- Updated the release workflow to validate against `baihe-autogui-inspect v0.1.3`, matching the current published extension baseline so the tag-driven release can complete before the next inspect patch is published.

## [0.1.13] - 2026-03-29

### Fixed
- Raised the optional `inspect` / `extra` extension dependency floor to `baihe-autogui-inspect>=0.1.3`, which now keeps Python 3.8 on `PySide6==6.1.3` for Win7-oriented compatibility while allowing newer Python versions to resolve newer compatible PySide6 releases.

### Changed
- Refreshed project metadata and contributor guidance so Windows-only scope, Python 3.8 development baseline, and the inspect extension relationship are documented consistently.

## [0.1.12] - 2026-03-29

### Fixed
- Updated GitHub Actions to check out the sibling `baihe-autogui-inspect` repository in the same workspace layout used by local development, so `uv sync --locked --dev` works in CI and release jobs.
- Aligned the lockfile and workflow baseline with `baihe-autogui-inspect v0.1.2`.

## [0.1.11] - 2026-03-28

### Added
- Added optional `inspect` and compatibility `extra` extras that install the `baihe-autogui-inspect` companion tool alongside `baihe-autogui`

### Changed
- Declared `baihe-autogui` as a Windows-only project in package metadata and user-facing documentation
- Documented local workspace wiring so the optional inspect extension resolves from the sibling `baihe-autogui-inspect` project during development
- Added `loguru` and `pywinauto` as direct runtime dependencies so logging and Windows automation helpers are available in installed environments
- Added `mypy` and `pre-commit` to the shared development toolchain and GitHub workflows

## [0.1.10] - 2026-03-28

### Fixed
- Switched GitHub Actions test/build jobs from Ubuntu to Windows so GUI-related tests run in the project's intended platform environment
- Updated workflow smoke tests to resolve the built wheel path explicitly in PowerShell instead of relying on shell glob expansion

## [0.1.9] - 2026-03-28

### Added
- Added public `Element.exists()` for boolean existence checks without changing chain behavior
- Added `Auto.move_to(x, y)` and `Auto.move_by(dx, dy)` for explicit absolute and relative mouse movement

### Changed
- Relaxed the published runtime requirement to `Python >=3.8` while keeping local development and release validation pinned to Python 3.8 for Win7-oriented compatibility checks
- `if_exists()` now skips the entire remaining chain once the target is missing, including waits, keyboard actions, and nested `locate()` calls
- Renamed element-level mouse movement from `move_to()` to `hover()` so only `Auto` keeps the global `move_to()` / `move_by()` coordinate APIs
- `Element.hover()`, `click()`, `right_click()`, and `double_click()` now accept optional nine-grid `anchor` and post-anchor `dx` / `dy` offsets for region and image targets
- Consolidated developer documentation into `CONTRIBUTING.md` so the repository keeps one developer manual instead of separate `CLAUDE.md` and `RELEASING.md`

## [0.1.8] - 2026-03-27

### Added
- Added `Element.highlight()` to draw temporary debug overlays around point, region, and image targets without changing existing locate semantics
- Added `Element.clear_highlight()` and `Auto.clear_highlights()` so scripts can clear one element's overlay or all active overlays explicitly

### Changed
- `highlight()` now snapshots and reuses the resolved point or region so the visible overlay stays aligned with follow-up element actions
- Replaced the temporary `tkinter` highlight backend with a native Win32 overlay so region and image highlights render as red frames and point highlights render as red crosshairs

## [0.1.7] - 2026-03-27

### Fixed
- Tightened `locate_all()` image-match deduplication so small OpenCV matches that drift by 1-2 pixels are still merged into one logical result
- Added additional regression coverage to verify both raw `pyautogui` behavior and the deduplicated `Auto.locate_all()` result

## [0.1.6] - 2026-03-27

### Fixed
- Deduplicated heavily overlapping image matches in `locate_all()` so OpenCV template matching does not return floods of near-identical results
- Deduplicated repeated image hits across locator lists in `locate_all()` when multiple image templates match the same screen element

## [0.1.5] - 2026-03-27

### Fixed
- Normalized `Path` image inputs to strings before passing them to the OpenCV-backed locate APIs, so `locate()` and `locate_all()` work correctly with `Path` objects

## [0.1.4] - 2026-03-27

### Changed
- Added `opencv-python` as a direct runtime dependency so image matching with `confidence=...` works out of the box in consumer environments

## [0.1.3] - 2026-03-27

### Added
- `locate()` and `locate_all()` now accept ordered lists of mixed locators while preserving existing single-locator inputs

## [0.1.2] - 2026-03-27

### Fixed
- Mocked screen-size checks in element tests so the release workflow does not hit real GUI calls in headless CI

## [0.1.1] - 2026-03-27

### Added
- Thin `gui` adapter layer for all `pyautogui` interactions
- New `Element` actions: `move_to()`, `right_click()`, `double_click()`, `press()`, and `hotkey()`
- Nested `Element.locate()` and `Element.locate_all()` for searches scoped to the current image or region
- Public exception types: `AutoGuiError`, `ValidationError`, `ElementNotFoundError`, `ElementTimeoutError`, and `ImageNotFoundError`
- Public `__version__` export at package root
- Example scripts under `examples/`
- Public API regression tests
- GitHub Actions workflow for tests, linting, and package builds
- Contributor guide in `CONTRIBUTING.md`
- Declared `dev` dependency group for local testing and linting
- Tag-driven release workflow for PyPI publishing
- Short release checklist in `RELEASING.md`
- Wheel smoke import check script and workflow coverage

### Changed
- `locate_all()` now snapshots image-match points and reuses cached coordinates
- Validation now raises explicit `ValidationError` instead of generic `ValueError`
- Required-element failures now raise explicit element exceptions instead of generic built-ins
- Project descriptions and documentation now describe the library as a lightweight wrapper rather than a heavy architecture
- README, contributor notes, and CI now use the same `uv sync --dev` workflow
- Package metadata now includes PyPI-facing keywords, classifiers, and project links

### Fixed
- `locate_all()` image matches now use box centers instead of top-left coordinates
- Cached points now bypass unnecessary re-lookup during actions
- `locate_all()` image matches now also retain their matched regions for nested searches
- Image-not-found handling is consistent for both single and multiple image searches
- Deferred `pyautogui` imports so package imports and tests work in headless CI environments

## [0.1.0] - 2026-03-27

### Added
- `Auto` class as main entry point
- `Auto.locate()` method for single target location
- `Auto.locate_all()` method for multiple target location
- `PointTarget` for point coordinate targeting
- `RegionTarget` for region targeting (returns center point)
- `ImageTarget` for image matching targeting
- `Element` class with chainable actions:
  - `click()` - click action
  - `wait()` - wait action
  - `write()` - type text action
- Conditional methods on Element:
  - `if_exists()` - skip if element doesn't exist
  - `wait_until_exists()` - wait until element appears
  - `assert_exists()` - assert element must exist
- `search_region` parameter for all Target types (subset semantics)
- `confidence`, `timeout`, `retry` parameters for ImageTarget
- Code quality tools (ruff) configuration
- Test infrastructure (pytest)

### Architecture
- Target + Element + Auto polymorphic chain architecture
- Immediate lookup with position caching
- Subset semantics for existence checking
- Stateless Element design
