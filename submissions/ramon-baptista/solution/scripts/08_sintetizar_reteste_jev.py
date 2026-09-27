from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest
from sklearn.metrics import confusion_matrix


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "jev_evaluation"
CLASSES = ["Access", "Administrative rights", "HR Support", "Hardware",
           "Internal Project", "Miscellaneous", "Purchase", "Storage"]
SEED = 20260924


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x]


def macro_f1(y: np.ndarray, p: np.ndarray) -> float:
    cm = confusion_matrix(y, p, labels=CLASSES); vals = []
    for i in range(len(CLASSES)):
        vp = cm[i, i]; fp = cm[:, i].sum() - vp; fn = cm[i].sum() - vp
        precision = vp / (vp + fp) if vp + fp else 0.0
        recall = vp / (vp + fn) if vp + fn else 0.0
        vals.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return float(np.mean(vals))


def main() -> None:
    new = sorted(read_jsonl(OUT / "retest_structured_criteria_validation.jsonl"), key=lambda r: r["record_id"])
    ids = {r["record_id"] for r in new}
    old = {r["record_id"]: r for r in read_jsonl(OUT / "jev_results.jsonl")
           if r["partition"] == "validation" and r["language"] == "en" and r["record_id"] in ids}
    baseline = [old[r["record_id"]] for r in new]
    y = np.array([r["true_label"] for r in new]); a = np.array([r["prediction"] for r in baseline])
    b = np.array([r["prediction"] for r in new]); ac = a == y; bc = b == y
    rng = np.random.default_rng(SEED); diffs_f1 = []; diffs_acc = []
    by_class = [np.flatnonzero(y == c) for c in CLASSES]
    for _ in range(5000):
        idx = np.concatenate([rng.choice(ix, size=len(ix), replace=True) for ix in by_class])
        diffs_f1.append(macro_f1(y[idx], b[idx]) - macro_f1(y[idx], a[idx]))
        diffs_acc.append(float(np.mean(bc[idx]) - np.mean(ac[idx])))
    a_only = int(sum(ac & ~bc)); b_only = int(sum(~ac & bc)); discordant = a_only + b_only
    high = np.array([r["confidence"] >= .9 for r in new])
    uninformative = read_jsonl(OUT / "uninformative_results.jsonl")
    result = {
        "retest_inference": {"n": len(y),
            "method": "paired class-stratified percentile bootstrap, 5000 resamples; preserves 10 cases per class",
            "macro_f1_difference": macro_f1(y, b) - macro_f1(y, a),
            "macro_f1_difference_ci95": [float(np.quantile(diffs_f1, .025)), float(np.quantile(diffs_f1, .975))],
            "accuracy_difference": float(np.mean(bc) - np.mean(ac)),
            "accuracy_difference_ci95": [float(np.quantile(diffs_acc, .025)), float(np.quantile(diffs_acc, .975))],
            "mcnemar_exact": {"baseline_only_correct": a_only, "structured_only_correct": b_only,
                              "discordant_n": discordant,
                              "two_sided_exact_binomial_p": float(binomtest(min(a_only, b_only), discordant, .5).pvalue)}},
        "structured_confidence": {"n": len(new), "mean": float(np.mean([r["confidence"] for r in new])),
            "ge_0_9_n": int(sum(high)), "ge_0_9_accuracy": float(np.mean(bc[high]))},
        "uninformative_design": {"calls_n": len(uninformative),
            "unique_texts_n": len({r["text"] for r in uninformative}),
            "method": "exact count of distinct input strings in saved JSONL; repeated calls are not independent texts"}}
    (OUT / "retest_structured_criteria_validation_statistics.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
