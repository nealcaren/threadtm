#!/usr/bin/env bash
# Verify the vendored reference source still matches a topica checkout, so the
# snapshot in reference_implementation/ is provably the code the package runs.
# Compares body bytes only (the provenance header is stripped before diffing).
#
# Usage: scripts/check_reference.sh [path-to-topica-checkout] [git-ref]
#   defaults: ../topica  and  the ref recorded in reference_implementation/PROVENANCE.md
set -euo pipefail

TOPICA="${1:-../topica}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HERE/reference_implementation"

if [ ! -d "$TOPICA/.git" ]; then
  echo "error: '$TOPICA' is not a git checkout of topica" >&2
  exit 1
fi

# Default ref: the tag matching the EXACT version pinned in pyproject.toml, so
# this check verifies the snapshot against the code the package actually installs.
REF="${2:-}"
if [ -z "$REF" ]; then
  REF="v$("$HERE/scripts/pinned_topica.sh")"
fi
SHA="$(git -C "$TOPICA" rev-parse "$REF")"

declare -a FILES=(
  "src/thread_tm.rs:thread_tm.rs"
  "src/python/thread_tm.rs:thread_tm_bindings.rs"
  "src/tree_field.rs:tree_field.rs"
)

# Body of a vendored file = everything after the header's trailing blank line.
strip_header() { awk 'seen{print} /^$/ && !seen{seen=1}' "$1"; }

status=0
for pair in "${FILES[@]}"; do
  srcpath="${pair%%:*}"; dstname="${pair##*:}"
  if diff -q <(strip_header "$DEST/$dstname") <(git -C "$TOPICA" show "$SHA:$srcpath") >/dev/null; then
    echo "ok    $dstname == $srcpath @ ${SHA:0:12}"
  else
    echo "DRIFT $dstname != $srcpath @ ${SHA:0:12}  (re-run scripts/vendor_reference.sh)"
    status=1
  fi
done
exit $status
