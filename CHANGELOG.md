# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
