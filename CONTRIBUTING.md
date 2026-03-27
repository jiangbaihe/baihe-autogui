# Contributing

Thanks for helping improve `baihe-autogui`.

## Setup

```bash
uv sync --dev
```

## Local Checks

Run the same checks we expect in CI:

```bash
uv run --with pytest pytest -q
uv run --with ruff ruff check .
uv build
```

## Guidelines

- Keep the public API small and predictable.
- Prefer thin wrappers over new abstraction layers.
- Add or update tests with every behavior change.
- Update `README.md`, `README_zh.md`, and `CHANGELOG.md` when user-facing behavior changes.

## Pull Requests

- Describe the behavior change clearly.
- Mention any exception or API contract changes.
- Include test coverage for bug fixes and new features.
