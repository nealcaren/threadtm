"""Smoke tests: the package imports, the pin is honored, and ThreadTM fits.

These are deliberately minimal. ThreadTM's numerical correctness is tested in
topica; here we only assert that the standalone surface wires up and that a
tiny reply tree fits end to end against the pinned release.
"""

import threadtm


def test_pins_expected_topica():
    # This package's whole job is reproducibility, so the pin is a contract.
    assert threadtm.__topica_version__.startswith("0.58."), threadtm.__topica_version__


def test_public_surface_present():
    for name in ("ThreadTM", "Corpus", "reply_completion",
                 "prevalence_ci", "group_prevalence_ci"):
        assert hasattr(threadtm, name), name


def test_experimental_gate_is_open_on_import():
    # Importing threadtm should have opened topica's experimental gate for us.
    import topica
    assert topica.experimental_enabled()


def test_fits_a_tiny_reply_tree():
    # A three-node thread: root, and two replies to it.
    docs = [
        ["budget", "deficit", "tax", "spending"],
        ["tax", "spending", "cut", "budget"],
        ["playoff", "quarterback", "touchdown", "budget"],
    ]
    parents = [-1, 0, 0]

    model = threadtm.ThreadTM(num_topics=2, em_iters=15, seed=0)
    model.fit(docs, parents=parents)

    # persistence() is reachable through the fitted model, not a free function.
    assert hasattr(model, "persistence")
    # prevalence_se is a fitted attribute, not an importable function.
    assert hasattr(model, "prevalence_se")
