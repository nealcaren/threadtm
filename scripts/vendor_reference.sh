#!/usr/bin/env bash
# Snapshot ThreadTM's reference source from a topica checkout into
# reference_implementation/, for READING by reviewers. The canonical, tested,
# and installed code is the pinned topica release (see pyproject.toml); these
# files are an attributed copy, kept in sync by scripts/check_reference.sh.
#
# Usage: scripts/vendor_reference.sh [path-to-topica-checkout] [git-ref]
#   defaults: ../topica  and  the ref currently checked out there
set -euo pipefail

TOPICA="${1:-../topica}"
REF="${2:-}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HERE/reference_implementation"

if [ ! -d "$TOPICA/.git" ]; then
  echo "error: '$TOPICA' is not a git checkout of topica" >&2
  exit 1
fi

# Resolve the ref to snapshot (default: whatever topica has checked out).
if [ -z "$REF" ]; then REF="$(git -C "$TOPICA" rev-parse HEAD)"; fi
SHA="$(git -C "$TOPICA" rev-parse "$REF")"
DESC="$(git -C "$TOPICA" describe --tags "$SHA" 2>/dev/null || echo "$SHA")"

# (source in topica) -> (name in reference_implementation)
declare -a FILES=(
  "src/thread_tm.rs:thread_tm.rs"
  "src/python/thread_tm.rs:thread_tm_bindings.rs"
  "src/tree_field.rs:tree_field.rs"
)

mkdir -p "$DEST"
for pair in "${FILES[@]}"; do
  srcpath="${pair%%:*}"; dstname="${pair##*:}"
  header="// ThreadTM reference source — SNAPSHOT for reading, not the build input.
// Canonical, tested source: topica $DESC ($SHA)
//   $srcpath
// This project installs and runs the pinned topica release (see pyproject.toml);
// scripts/check_reference.sh verifies this snapshot still matches that release.
// Do not edit here — change it in topica, then re-run scripts/vendor_reference.sh.

"
  { printf '%s' "$header"; git -C "$TOPICA" show "$SHA:$srcpath"; } > "$DEST/$dstname"
  echo "vendored $srcpath -> reference_implementation/$dstname"
done

cat > "$DEST/PROVENANCE.md" <<EOF
# Reference implementation provenance

The files in this directory are an **attributed snapshot** of ThreadTM's source,
copied here so reviewers can read the model as a focused three-file surface
instead of navigating topica's full model set. They are **not** what this package
builds or runs: \`threadtm\` installs and executes the pinned topica release named
in \`pyproject.toml\`.

| File | topica source |
|------|---------------|
| \`thread_tm.rs\`          | \`src/thread_tm.rs\` (the model: variational EM, logistic-normal per-doc bound) |
| \`thread_tm_bindings.rs\` | \`src/python/thread_tm.rs\` (the PyO3 Python bindings) |
| \`tree_field.rs\`         | \`src/tree_field.rs\` (the Gaussian tree-field prior over the reply tree) |

Snapshot taken from topica **$DESC**

    commit $SHA

\`scripts/check_reference.sh\` re-derives these files from the pinned topica tag and
fails if they have drifted, so the snapshot is provably the code that runs.
EOF
echo "wrote reference_implementation/PROVENANCE.md ($DESC)"
