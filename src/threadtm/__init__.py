"""ThreadTM: a reply-threaded topic model.

ThreadTM couples each reply's topic prior to the comment it answers, a
persistence-smoothing prior over the reply tree that reverts toward a
covariate-group baseline. It reduces to a plain logistic-normal (CTM/STM-style)
topic model when the reply tree is flat.

This package is the standalone, pinned distribution of ThreadTM. The model's
reference implementation is developed and tested in `topica
<https://github.com/nealcaren/topica>`_; ThreadTM is experimental there, kept
out of the validated roster until its behavior is settled. Here we pin the
validated release, call ``topica.enable_experimental()`` for you, and expose
only the reply-threaded surface so the model reads as a single object rather
than one entry in a large model zoo.

The vendored, attributed source for reading lives in ``reference_implementation/``
at the repository root; the runtime below is a thin re-export of the pinned
topica release, so what you import here is exactly what topica ships and tests.

Public surface
--------------
- :class:`ThreadTM`            the model (fit / transform / persistence)
- :class:`Corpus`              corpus container, for building input
- :func:`tokenize`            turn raw text into a token list
- :data:`ENGLISH_STOPWORDS`   default English stopword set for ``tokenize``
- :func:`reply_completion`     the held-out reply-completion evaluation
- :func:`prevalence_ci`        prevalence confidence intervals
- :func:`group_prevalence_ci`  per-group prevalence confidence intervals

Reduced-form persistence and prevalence standard errors are reached through a
fitted model: ``model.persistence()`` and ``model.prevalence_se``.

This surface is everything an end-to-end reply-threaded workflow needs, so user
code imports ``threadtm`` and never reaches back into topica directly.
"""

from __future__ import annotations

import topica as _topica

# ThreadTM is experimental-gated in topica; opt in at import so that
# `from threadtm import ThreadTM` just works, with no separate setup call.
_topica.enable_experimental()

from topica import (  # noqa: E402  (import after the experimental gate is set)
    ThreadTM,
    Corpus,
    tokenize,
    ENGLISH_STOPWORDS,
    prevalence_ci,
    group_prevalence_ci,
)
from topica.evaluate import reply_completion  # noqa: E402

#: The topica release this package pins and re-exports.
__topica_version__ = _topica.__version__

__version__ = "0.1.0"

__all__ = [
    "ThreadTM",
    "Corpus",
    "tokenize",
    "ENGLISH_STOPWORDS",
    "reply_completion",
    "prevalence_ci",
    "group_prevalence_ci",
    "__version__",
    "__topica_version__",
]
