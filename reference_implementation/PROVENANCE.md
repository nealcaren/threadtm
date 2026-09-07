# Reference implementation provenance

The files in this directory are an **attributed snapshot** of ThreadTM's source,
copied here so reviewers can read the model as a focused three-file surface
instead of navigating topica's full model set. They are **not** what this package
builds or runs: `threadtm` installs and executes the pinned topica release named
in `pyproject.toml`.

| File | topica source |
|------|---------------|
| `thread_tm.rs`          | `src/thread_tm.rs` (the model: variational EM, logistic-normal per-doc bound) |
| `thread_tm_bindings.rs` | `src/python/thread_tm.rs` (the PyO3 Python bindings) |
| `tree_field.rs`         | `src/tree_field.rs` (the Gaussian tree-field prior over the reply tree) |

Snapshot taken from topica **v0.58.0**

    commit e03da20dc37a7c87d6d3ddd847747a82ea7ee994

`scripts/check_reference.sh` re-derives these files from the pinned topica tag and
fails if they have drifted, so the snapshot is provably the code that runs.
