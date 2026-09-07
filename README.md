# ThreadTM

**A reply-threaded topic model.** ThreadTM couples each reply's topic prior to
the comment it answers, a persistence-smoothing prior over the reply tree that
reverts toward a covariate-group baseline. On flat data it reduces to a plain
logistic-normal (CTM/STM-style) topic model; on threaded discussion it lets a
parent comment's topics inform its replies.

```python
import threadtm

docs = [["budget", "tax", "spending"],
        ["tax", "cut", "budget"],
        ["playoff", "quarterback", "defense"]]
parents = [-1, 0, -1]          # doc 1 replies to doc 0; docs 0 and 2 are roots

model = threadtm.ThreadTM(num_topics=2).fit(docs, parents=parents)
print(model.persistence())     # how strongly replies track their parent
```

## Install

```bash
pip install threadtm
```

## What this package is (and where the code lives)

ThreadTM's numerical core is implemented and tested in
[**topica**](https://github.com/nealcaren/topica), a Rust-backed topic-modeling
library. This package is ThreadTM's **standalone distribution**: it pins the
validated topica release, opens topica's experimental gate for you at import,
and exposes only the reply-threaded surface, so ThreadTM reads as a single model
rather than one entry in a large model set.

We state the dependency plainly because it is a strength: the math ThreadTM runs
on is a maintained, separately tested library, not one-off code bundled with a
paper. What you `import threadtm` and run is exactly the pinned topica release.

For reviewers who want to **read** the model rather than run it,
[`reference_implementation/`](reference_implementation/) holds an attributed,
three-file snapshot of the source:

| File | What it is |
|------|------------|
| `thread_tm.rs`          | the model — variational EM, logistic-normal per-document bound |
| `thread_tm_bindings.rs` | the Python (PyO3) bindings |
| `tree_field.rs`         | the Gaussian tree-field prior over the reply tree |

That snapshot is kept honest by `scripts/check_reference.sh`, which re-derives
the files from the pinned topica tag and fails if they have drifted.

## Public surface

| Name | What it does |
|------|--------------|
| `ThreadTM`             | the model — `fit`, `transform`, `persistence` |
| `Corpus`               | topica's corpus container, for building input |
| `reply_completion`     | held-out reply-completion evaluation (fits STM / RTM / LDA baselines from topica) |
| `prevalence_ci`        | prevalence confidence intervals |
| `group_prevalence_ci`  | per-group prevalence confidence intervals |

Reduced-form persistence and prevalence standard errors are read off a fitted
model: `model.persistence()` and `model.prevalence_se`.

## Reproducibility

The dependency is pinned to `topica==0.58.*`, the release ThreadTM was validated
on. The pin is tight by design and bumped deliberately; results reproduce
against the pinned core.

## Citation

See [`CITATION.cff`](CITATION.cff).

## License

Apache-2.0.
