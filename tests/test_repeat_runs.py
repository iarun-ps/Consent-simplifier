from src.repeat_runs import jaccard, mean_pairwise_jaccard, summarise_form


def test_jaccard_identical_and_disjoint():
    assert jaccard({"a", "b"}, {"a", "b"}) == 1.0
    assert jaccard({"a"}, {"b"}) == 0.0
    assert jaccard(set(), set()) == 1.0


def test_mean_pairwise_jaccard():
    assert mean_pairwise_jaccard([{"a"}]) == 1.0
    assert mean_pairwise_jaccard([{"a", "b"}, {"a", "b"}, {"a", "b"}]) == 1.0
    assert round(mean_pairwise_jaccard([{"a", "b"}, {"a"}]), 3) == 0.5


def _run(text, grade, flags):
    return {"text": text, "grade_after": grade, "flags": flags, "n_flags": len(flags)}


def test_summarise_form():
    runs = [_run("x", 10.0, {"a", "b"}), _run("y", 12.0, {"a"})]
    s = summarise_form(runs)
    assert s["runs"] == 2
    assert s["distinct_texts"] == 2
    assert s["grade_after_mean"] == 11.0
    assert s["flags_in_every_run"] == 1
    assert s["flags_in_some_runs_only"] == 1
    assert s["flags_min"] == 1 and s["flags_max"] == 2


def test_summarise_form_single_run_has_zero_sd():
    s = summarise_form([_run("x", 10.0, {"a"})])
    assert s["grade_after_sd"] == 0.0
    assert s["flag_agreement_jaccard"] == 1.0
