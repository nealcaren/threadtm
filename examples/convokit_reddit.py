"""ThreadTM on real Reddit threads: reply persistence differs by subreddit.

Fits ThreadTM to two subreddits from ConvoKit's reddit-corpus-small and compares
their reply persistence -- how strongly a reply's topic mix tracks the comment
it answers. A focused technical Q&A (r/askscience) holds its thread topic much
more tightly than an open-prompt sub (r/AskReddit), and ThreadTM measures the
gap. That reply-structure signal is exactly what a flat topic model discards.

Needs ConvoKit for the data loader:  pip install convokit
(ConvoKit is only needed to fetch/parse the corpus; ThreadTM itself does not
depend on it.) The corpus downloads once to ~/.convokit on first run.
"""
import re
from collections import defaultdict, deque
from convokit import Corpus, download
import threadtm

SUBREDDITS = ["askscience", "AskReddit"]
K = 15
DEAD = {"", "[deleted]", "[removed]"}
URL = re.compile(r"https?://\S+|www\.\S+")
# Reddit markup + contraction remnants that survive apostrophe-splitting.
EXTRA_STOP = {"amp", "gt", "lt", "don", "isn", "doesn", "didn", "wasn", "aren",
              "wouldn", "couldn", "shouldn", "won", "ve", "ll", "re",
              "http", "https", "www", "com"}
STOP = set(threadtm.ENGLISH_STOPWORDS) | EXTRA_STOP

corpus = Corpus(filename=download("reddit-corpus-small"))


def build(subreddit):
    """One subreddit -> (docs, parents). parents[d] is the row index of d's
    parent in the reply tree (-1 for a thread root); a parent always precedes
    its children, and dead-body nodes are reparented to the nearest live one."""
    texts, parents = [], []
    convos = sorted((c for c in corpus.iter_conversations()
                     if c.meta.get("subreddit") == subreddit), key=lambda c: c.id)
    for convo in convos:
        utts = {u.id: u for u in convo.iter_utterances()}
        kids = defaultdict(list)
        root = None
        for u in utts.values():
            if u.reply_to is None or u.reply_to not in utts:
                root = u.id
            else:
                kids[u.reply_to].append(u.id)
        if root is None:
            continue

        order, q = [], deque([root])          # BFS: parent before its children
        while q:
            cur = q.popleft(); order.append(cur); q.extend(kids[cur])

        alive_row = {}
        raw_parent = {u.id: (u.reply_to if u.reply_to in utts else None)
                      for u in utts.values()}

        def alive(uid):
            return (utts[uid].text or "").strip().lower() not in DEAD

        def nearest_alive(uid):
            p = raw_parent[uid]
            while p is not None and p not in alive_row:
                p = raw_parent[p]
            return alive_row.get(p, -1)

        for uid in order:
            if not (alive(uid) or raw_parent[uid] is None):
                continue
            texts.append(utts[uid].text or "")
            parents.append(nearest_alive(uid))
            alive_row[uid] = len(texts) - 1

    docs = [threadtm.tokenize(URL.sub(" ", t), stopwords=STOP,
                              token_regex=r"[a-zA-Z]+", min_length=3)
            for t in texts]
    return docs, parents


for subreddit in SUBREDDITS:
    docs, parents = build(subreddit)
    roots = sum(1 for p in parents if p == -1)

    model = threadtm.ThreadTM(num_topics=K, em_iters=100, seed=13)
    model.fit(docs, parents=parents, min_count=5)

    p = model.persistence(bootstrap=200)
    print(f"\nr/{subreddit}: {len(docs)} docs, {roots} threads, K={K}")
    print(f"  reply persistence: {p['observed_persistence']:.3f} "
          f"(95% CI {p['observed_ci'][0]:.3f}-{p['observed_ci'][1]:.3f})")
    print("  sample topics:")
    for k in range(5):
        print(f"    {k}: " + " ".join(model.top_words(8, topic=k)))
