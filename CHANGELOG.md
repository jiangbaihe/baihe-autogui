# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Thin `gui` adapter layer for all `pyautogui` interactions
- New `Element` actions: `move_to()`, `right_click()`, `double_click()`, `press()`, and `hotkey()`
- Public exception types: `AutoGuiError`, `ValidationError`, `ElementNotFoundError`, `ElementTimeoutError`, and `ImageNotFoundError`
- Public `__version__` export at package root
- Example scripts under `examples/`
- Public API regression tests
- GitHub Actions workflow for tests, linting, and package builds
- Contributor guide in `CONTRIBUTING.md`
- Declared `dev` dependency group for local testing and linting
- Tag-driven release workflow for PyPI publishing
- Short release checklist in `RELEASING.md`

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
- Image-not-found handling is consistent for both single and multiple image searches

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
