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

## Worked example: real Reddit threads

This fits ThreadTM to a real threaded corpus,
[ConvoKit's `reddit-corpus-small`](https://convokit.cornell.edu/documentation/reddit-small.html)
(297k comments across 100 subreddits). The full script is
[`examples/convokit_reddit.py`](examples/convokit_reddit.py); it downloads the
corpus once, turns each conversation's reply tree into `(docs, parents)`, and
fits an 8-topic model. The core of it:

```python
import threadtm

# docs: list of token lists.  parents[d]: row index of d's parent (-1 = root),
# built from each ConvoKit conversation's reply tree (see the full script).
model = threadtm.ThreadTM(num_topics=8, em_iters=120, seed=13)
model.fit(docs, parents=parents, min_count=5)

for k in range(model.num_topics):
    print(k, " ".join(model.top_words(8, topic=k)))

print(model.persistence(bootstrap=300))   # how strongly replies track parents
```

Running it (`pip install convokit`, then `python examples/convokit_reddit.py`)
on 4,000 documents from 113 threads produces, verbatim:

```
4000 docs, 113 thread roots, 3887 replies

Topics (top words):
  0: one like police good need nuclear time two
  1: like one think time trump people see know
  2: government like canada insurance free one people need
  3: slavery bible people think like slave one women
  4: people like one think thread religious sub states
  5: like one good great really use know brush
  6: mainstream say cars people god ball think becoming
  7: game like new make people diablo games play

Reply persistence: 0.473 (95% CI 0.415-0.529)
```

The topics are recognizable slices of a general-Reddit sample (politics/Trump,
Canadian health insurance, a religion/slavery debate, gaming/Diablo). The
**reply persistence** of 0.473 is ThreadTM's headline diagnostic: a reply's
topic mix tracks the comment it answers about halfway, well above zero and
tightly estimated. That coupling is exactly what a flat (non-threaded) topic
model throws away.

## Public surface

| Name | What it does |
|------|--------------|
| `ThreadTM`             | the model — `fit`, `transform`, `top_words`, `persistence` |
| `Corpus`               | topica's corpus container, for building input |
| `reply_completion`     | held-out reply-completion evaluation (fits STM / RTM / LDA baselines) |
| `prevalence_ci` / `group_prevalence_ci` | prevalence confidence intervals |

Reduced-form persistence and prevalence standard errors are read off a fitted
model: `model.persistence()` and `model.prevalence_se`.

---

ThreadTM's numerical core is the [topica](https://github.com/nealcaren/topica)
library; this package pins an exact validated release (`topica==0.58.0`) and
re-exports only the reply-threaded surface. What you `import threadtm` and run is
exactly that release; an attributed source snapshot for reading lives in
[`reference_implementation/`](reference_implementation/) and is kept in sync by
`scripts/check_reference.sh` (see [`RELEASING.md`](RELEASING.md)). Apache-2.0;
please cite via [`CITATION.cff`](CITATION.cff).
