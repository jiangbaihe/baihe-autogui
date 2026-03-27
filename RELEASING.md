# Releasing

This project keeps releases intentionally simple.

## Before tagging

1. Update the version in `pyproject.toml`.
2. Move the relevant notes from `CHANGELOG.md` under `Unreleased` into a new version section.
3. Run the local checks:

```bash
uv sync --dev
uv run pytest -q
uv run ruff check .
uv build
```

## Publish flow

1. Commit the release changes.
2. Create a version tag like `v0.1.1`.
3. Push the branch and tag:

```bash
git push
git push origin v0.1.1
```

4. GitHub Actions will run the `Release` workflow.
5. If PyPI trusted publishing is configured for this repository, the workflow will upload `dist/` to PyPI.

## PyPI setup note

The `publish-pypi` job uses GitHub OIDC trusted publishing through the `pypi` environment.
Configure that environment in GitHub and register this repository in the target PyPI project before the first release.
