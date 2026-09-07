"""ThreadTM quickstart: fit a reply tree, read persistence.

Run with:  python examples/quickstart.py
"""

import threadtm

print(f"threadtm {threadtm.__version__} on topica {threadtm.__topica_version__}")

# A small threaded discussion. `docs` are token lists; `parents[d]` is the
# index of the comment document d replies to (-1 marks a thread root). The two
# arrays are in the same document order.
docs = [
    ["budget", "deficit", "tax", "spending", "policy"],   # 0: root A (fiscal)
    ["tax", "cut", "spending", "budget", "policy"],        # 1: reply to 0
    ["deficit", "budget", "tax", "revenue"],               # 2: reply to 1
    ["playoff", "quarterback", "touchdown", "defense"],    # 3: root B (sports)
    ["quarterback", "injury", "playoff", "roster"],        # 4: reply to 3
]
parents = [-1, 0, 1, -1, 3]

model = threadtm.ThreadTM(num_topics=2, em_iters=50, seed=13)
model.fit(docs, parents=parents)

# Reduced-form persistence: how strongly a reply's topics track its parent's.
persistence = model.persistence(bootstrap=200)
print("persistence:", persistence)
