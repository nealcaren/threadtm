# Releasing / keeping in sync with topica

This package is a thin, pinned distribution of ThreadTM, whose code lives in
[topica](https://github.com/nealcaren/topica). Keeping the two in sync is a
**deliberate, single-PR** operation, never automatic. One value drives
everything: the exact pin in `pyproject.toml` (`topica==X.Y.Z`).

## The single source of truth

`scripts/pinned_topica.sh` reads that pin. The reference-sync check and CI both
call it, so the runtime dependency, the reference snapshot, and the CI gate can
never point at different topica versions without failing the build.

## What can drift, and what catches it

| Thing | Kept honest by |
|-------|----------------|
| Reference snapshot vs. the pinned topica source | `scripts/check_reference.sh` (run in CI on every PR) |
| Pin bumped but snapshot not re-vendored | same check — it derives the tag from the pin, so a bump without re-vendor fails |
| A newer topica exists than we pin | `.github/workflows/topica-staleness.yml` opens a tracking issue weekly |

## Bumping the pinned topica (the sync procedure)

When topica ships a release you want to adopt (e.g. ThreadTM changed):

1. Edit the pin in `pyproject.toml`: `topica==X.Y.Z` (both the base dep and the
   `viz` extra).
2. Re-vendor the reference snapshot from a topica checkout at that tag:
   ```bash
   scripts/vendor_reference.sh ../topica vX.Y.Z
   ```
3. Confirm the snapshot matches the new pin:
   ```bash
   scripts/check_reference.sh          # defaults to the pin; needs ../topica
   ```
4. Run the smoke tests against the new release:
   ```bash
   uv pip install 'topica==X.Y.Z' && pytest -q
   ```
5. Bump this package's own `version` (in `pyproject.toml` and
   `src/threadtm/__init__.py`), commit, and open a PR. CI re-runs the
   reference-sync check; merge when green.

## Cutting a release to PyPI

Tag the merged commit and push the tag:

```bash
git tag v0.1.0 && git push origin v0.1.0
```

`.github/workflows/release.yml` builds the wheel/sdist and publishes to PyPI via
Trusted Publishing (no API token stored). One-time setup: on PyPI, add this
repo as a trusted publisher for the `threadtm` project
(https://docs.pypi.org/trusted-publishers/).
