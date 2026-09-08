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

## Worked example: reply persistence differs by subreddit

ThreadTM's headline diagnostic is **reply persistence**: how strongly a reply's
topic mix tracks the comment it answers. This example fits ThreadTM to two
subreddits from
[ConvoKit's `reddit-corpus-small`](https://convokit.cornell.edu/documentation/reddit-small.html)
and shows that persistence is not a constant of the model but a measurable
property of a community's discourse. The full script is
[`examples/convokit_reddit.py`](examples/convokit_reddit.py); it downloads the
corpus once and turns each conversation's reply tree into `(docs, parents)`. The
core of it:

```python
import threadtm

# docs: list of token lists.  parents[d]: row index of d's parent (-1 = root),
# built from each subreddit's reply trees (see the full script).
model = threadtm.ThreadTM(num_topics=15, em_iters=100, seed=13)
model.fit(docs, parents=parents, min_count=5)

print(model.persistence(bootstrap=200))   # how strongly replies track parents
```

Running it (`pip install convokit`, then `python examples/convokit_reddit.py`)
produces, verbatim:

```
r/askscience: 3161 docs, 73 threads, K=15
  reply persistence: 0.567 (95% CI 0.528-0.600)
  sample topics:
    0: matter fish water chlorine like pool bucket one
    1: ground air lightning earth water force moving going
    2: light see years away universe black speed space
    3: time infinite one value point like sum finite
    4: aircraft missile pilot radar plane pilots target system

r/AskReddit: 4525 docs, 94 threads, K=15
  reply persistence: 0.418 (95% CI 0.371-0.455)
  sample topics:
    0: god people jesus old one like bible think
    1: people love why like god mean free make
    2: one fire town photos people see mine like
    3: like really people sorry something one thank still
    4: school time never love years one got high
```

Both subreddits yield recognizable topics at K=15 (physics, cosmology, and math
in r/askscience; religion, life stories, and photos in r/AskReddit), so the
model is not starved at this size. The **persistence gap is the point**: in
r/askscience, a focused technical Q&A, answers stay tightly on the question that
prompted them (**0.567**); in r/AskReddit, an open-prompt sub of anecdotes and
tangents, replies drift much further from their parent (**0.418**), and the two
confidence intervals do not overlap. A flat (non-threaded) topic model sees no
difference at all, because it never looks at who replied to whom.

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
