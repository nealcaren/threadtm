"""ThreadTM on a real ConvoKit corpus (reddit-corpus-small).

Builds (docs, parents) from the reply tree, fits ThreadTM, prints topics and
the reduced-form reply persistence. Kept small enough to run in ~a minute.

Needs ConvoKit for the data loader:  pip install convokit
(ConvoKit is only needed to fetch/parse the corpus; ThreadTM itself does not
depend on it.) The corpus downloads once to ~/.convokit on first run.
"""
import re
from collections import defaultdict, deque
from convokit import Corpus, download
import threadtm

DEAD = {"", "[deleted]", "[removed]"}
MAX_DOCS = 4000
URL = re.compile(r"https?://\S+|www\.\S+")
# Reddit markup + contraction remnants that survive apostrophe-splitting.
EXTRA_STOP = {"amp", "gt", "lt", "don", "isn", "doesn", "didn", "wasn",
              "aren", "wouldn", "couldn", "shouldn", "won", "ve", "ll", "re"}
STOP = set(threadtm.ENGLISH_STOPWORDS) | EXTRA_STOP

corpus = Corpus(filename=download("reddit-corpus-small"))

# Mid-sized threads (real trees, but not a handful of megathreads): 15-150
# utterances, deterministic order, capped at MAX_DOCS.
convos = sorted(
    (c for c in corpus.iter_conversations()
     if 15 <= len(list(c.iter_utterances())) <= 150),
    key=lambda c: c.id,
)

texts, parents = [], []
n = 0
for convo in convos:
    utts = {u.id: u for u in convo.iter_utterances()}
    # children map for BFS from the root
    kids = defaultdict(list)
    root = None
    for u in utts.values():
        if u.reply_to is None or u.reply_to not in utts:
            root = u.id
        else:
            kids[u.reply_to].append(u.id)
    if root is None:
        continue

    # BFS order so a parent is always emitted before its children.
    order, q = [], deque([root])
    while q:
        cur = q.popleft(); order.append(cur); q.extend(kids[cur])

    # Keep alive bodies; reparent an orphan to its nearest alive ancestor.
    alive_row = {}          # utt id -> row index in `texts`
    def alive(uid): return (utts[uid].text or "").strip().lower() not in DEAD
    raw_parent = {u.id: (u.reply_to if u.reply_to in utts else None) for u in utts.values()}

    def nearest_alive(uid):
        p = raw_parent[uid]
        while p is not None and p not in alive_row:
            p = raw_parent[p]
        return alive_row.get(p, -1)

    if n >= MAX_DOCS:
        break
    for uid in order:
        if not (alive(uid) or raw_parent[uid] is None):
            continue
        if n >= MAX_DOCS:
            break
        texts.append(utts[uid].text or "")
        parents.append(nearest_alive(uid))
        alive_row[uid] = n
        n += 1

# Tokenize with English stopwords -> list of token lists.
docs = [threadtm.tokenize(URL.sub(" ", t), stopwords=STOP,
                          token_regex=r"[a-zA-Z]+", min_length=3)
        for t in texts]
roots = sum(1 for p in parents if p == -1)
print(f"{len(docs)} docs, {roots} thread roots, {len(docs)-roots} replies")

model = threadtm.ThreadTM(num_topics=8, em_iters=120, seed=13)
model.fit(docs, parents=parents, min_count=5)

print("\nTopics (top words):")
for k in range(model.num_topics):
    print(f"  {k}: " + " ".join(model.top_words(8, topic=k)))

# Reduced-form reply persistence: how strongly a reply's topics track its
# parent's, corrected for attenuation. (persistence() returns more fields.)
p = model.persistence(bootstrap=300)
print(f"\nReply persistence: {p['observed_persistence']:.3f} "
      f"(95% CI {p['observed_ci'][0]:.3f}-{p['observed_ci'][1]:.3f})")
