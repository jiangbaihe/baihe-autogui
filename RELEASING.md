# Releasing

This project keeps releases intentionally simple.

## Before tagging

1. Update the version in `pyproject.toml`.
2. Refresh `uv.lock` if the project version or dependencies changed, and commit that lockfile update with the release changes.
3. Move the relevant notes from `CHANGELOG.md` under `Unreleased` into a new version section.
4. Run the local checks:

```bash
uv sync --dev
uv run pytest -q
uv run ruff check .
uv build
```

5. Optionally run the wheel smoke check locally:

```bash
uv run --python 3.8 --no-project --with ./dist/*.whl python scripts/smoke_import.py
```

## Publish flow

1. Commit the release changes.
2. Create a version tag like `vX.Y.Z`.
3. Push the branch and tag:

```bash
git push
git push origin vX.Y.Z
```

4. GitHub Actions will run the `Release` workflow.
5. The workflow will also install the built wheel into a clean virtual environment and run a smoke import check.
6. If PyPI trusted publishing is configured for this repository, the workflow will upload `dist/` to PyPI.

## PyPI setup note

The `publish-pypi` job uses GitHub OIDC trusted publishing through the `pypi` environment.
Configure that environment in GitHub and register this repository in the target PyPI project before the first release.
