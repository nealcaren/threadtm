#!/usr/bin/env bash
# Echo the exact topica version this package pins, read from pyproject.toml.
# Single source of truth for the runtime dependency, the reference snapshot, and
# CI. Everything that needs "which topica version" gets it from here.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
# Match:  dependencies = ["topica==0.58.0"]   -> 0.58.0
grep -oE 'topica==[0-9]+\.[0-9]+\.[0-9]+' "$HERE/pyproject.toml" | head -1 | cut -d= -f3
