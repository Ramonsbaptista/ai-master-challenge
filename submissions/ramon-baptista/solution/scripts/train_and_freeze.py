from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import date
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
import scipy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ticket_classifier.core import (ARTIFACTS, DATA_PATH, OUTPUTS, aggregate_metrics,
                                    assert_consistency, load_data, per_class_metrics,
                                    route, sha256_file)

SEED = 20260922


def hash_ids(ids) -> str:
    return hashlib.sha256(("\n".join(ids) + "\n").encode("utf-8")).hexdigest()


def select_thresholds(scores: np.ndarray, correct: np.ndarray) -> tuple[float, float, dict]:
    # Busca só na validação. Cada faixa precisa de n>=100. Alta exige >=90%; média >=75%.
    candidates = np.unique(np.quantile(scores, np.linspace(0.05, 0.95, 91)))
    best = None
    for low in candidates:
        for high in candidates[candidates > low]:
            bands = route(scores, float(low), float(high))
            stats = {}
            valid = True
            for band in ("baixa", "media", "alta"):
                mask = bands == band
                count = int(mask.sum())
                acc = float(correct[mask].mean()) if count else 0.0
                stats[band] = {"n": count, "accuracy": acc, "coverage": count / len(scores)}
                valid &= count >= 100
            valid &= stats["alta"]["accuracy"] >= 0.90 and stats["media"]["accuracy"] >= 0.75
            valid &= stats["alta"]["accuracy"] >= stats["media"]["accuracy"] >= stats["baixa"]["accuracy"]
            if valid:
                objective = (stats["alta"]["coverage"], stats["media"]["coverage"], -high, -low)
                if best is None or objective > best[0]:
                    best = (objective, float(low), float(high), stats)
    if best is None:
        raise RuntimeError("Nenhum par de cortes satisfez n>=100 e metas de acerto na validação.")
    return best[1], best[2], best[3]


def main() -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    frame = load_data()
    classes = sorted(frame["Topic_group"].unique().tolist())
    train_val, test = train_test_split(frame, test_size=0.15, random_state=SEED,
                                       stratify=frame["Topic_group"])
    train, validation = train_test_split(train_val, test_size=0.15 / 0.85,
                                         random_state=SEED, stratify=train_val["Topic_group"])

    candidates = []
    for c in (0.5, 1.0, 2.0):
        for ngram in ((1, 1), (1, 2)):
            model = Pipeline([
                ("tfidf", TfidfVectorizer(sublinear_tf=True, min_df=2, max_df=0.98,
                                           ngram_range=ngram, max_features=100_000)),
                ("classifier", LogisticRegression(C=c, max_iter=1000, solver="lbfgs",
                                                   class_weight="balanced", random_state=SEED)),
            ])
            model.fit(train["Document"], train["Topic_group"])
            pred = model.predict(validation["Document"])
            score = f1_score(validation["Topic_group"], pred, labels=classes, average="macro")
            candidates.append({"C": c, "ngram": list(ngram), "validation_macro_f1": float(score),
                               "model": model})
    winner = max(candidates, key=lambda x: (x["validation_macro_f1"], -x["C"], -x["ngram"][1]))
    model = winner.pop("model")
    val_proba = model.predict_proba(validation["Document"])
    val_pred = model.classes_[np.argmax(val_proba, axis=1)]
    val_scores = np.max(val_proba, axis=1)
    low, high, val_routing = select_thresholds(val_scores, val_pred == validation["Topic_group"].to_numpy())

    # Único acesso ao teste para a avaliação final.
    test_pred = model.predict(test["Document"])
    test_scores = np.max(model.predict_proba(test["Document"]), axis=1)
    matrix, rows = per_class_metrics(test["Topic_group"], test_pred, classes)
    assert_consistency(matrix, rows, test["Topic_group"].to_numpy(), classes)
    metrics = aggregate_metrics(rows, matrix)
    majority = train["Topic_group"].value_counts().idxmax()
    baseline_pred = np.repeat(majority, len(test))
    base_matrix, base_rows = per_class_metrics(test["Topic_group"], baseline_pred, classes)
    assert_consistency(base_matrix, base_rows, test["Topic_group"].to_numpy(), classes)
    baseline_metrics = aggregate_metrics(base_rows, base_matrix)
    bands = route(test_scores, low, high)
    routing_test = {}
    for band in ("baixa", "media", "alta"):
        mask = bands == band
        count = int(mask.sum())
        routing_test[band] = {"n": count, "coverage": count / len(test),
                              "accuracy": float((test_pred[mask] == test.loc[mask, "Topic_group"]).mean())}
    if sum(v["n"] for v in routing_test.values()) != len(test):
        raise AssertionError("Volumes das faixas não somam o teste.")

    model_path = ARTIFACTS / "model-v1.0.0.joblib"
    joblib.dump(model, model_path)
    frozen = pd.DataFrame({"record_id": test["record_id"], "expected_label": test["Topic_group"],
                           "expected_prediction": test_pred, "expected_score": test_scores,
                           "expected_band": bands})
    frozen_path = ARTIFACTS / "frozen_test.csv"
    frozen.to_csv(frozen_path, index=False, lineterminator="\n")
    split_path = ARTIFACTS / "split_ids.json"
    split_doc = {"seed": SEED, "train": train["record_id"].tolist(),
                 "validation": validation["record_id"].tolist(), "test": test["record_id"].tolist()}
    split_path.write_text(json.dumps(split_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "model_version": "1.0.0", "created_on": date.today().isoformat(), "seed": SEED,
        "method": {"model": "TF-IDF + regressão logística", "selection_metric": "macro-F1 na validação",
                   "split": {"train": len(train), "validation": len(validation), "test": len(test),
                             "stratified": True}, "selected_hyperparameters": winner,
                   "routing_selection": "Busca em quantis do score na validação; n>=100/faixa; alta>=90%, média>=75%; maximiza cobertura alta e depois média.",
                   "score_name": "score do modelo (máxima probabilidade não calibrada)"},
        "classes": classes, "majority_class": majority,
        "routing_thresholds": {"low": low, "high": high},
        "validation_routing": val_routing, "test_routing": routing_test,
        "test": {"n": len(test), "confusion_matrix": matrix.tolist(), "per_class": rows,
                 "metrics": metrics, "baseline_confusion_matrix": base_matrix.tolist(),
                 "baseline_per_class": base_rows, "baseline_metrics": baseline_metrics},
        "versions": {"python": platform.python_version(), "numpy": np.__version__,
                     "pandas": pd.__version__, "scikit-learn": sklearn.__version__,
                     "scipy": scipy.__version__, "joblib": joblib.__version__},
        "files": {
            "data": {"path": str(DATA_PATH.relative_to(ROOT)), "sha256": sha256_file(DATA_PATH)},
            "split": {"path": str(split_path.relative_to(ARTIFACTS)), "sha256": sha256_file(split_path),
                      "test_ids_sha256": hash_ids(test["record_id"].tolist())},
            "frozen_test": {"path": str(frozen_path.relative_to(ARTIFACTS)), "sha256": sha256_file(frozen_path)},
            "model": {"path": model_path.name, "sha256": sha256_file(model_path)},
        },
    }
    manifest_path = ARTIFACTS / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "manifest": str(manifest_path), "metrics": metrics,
                      "baseline": baseline_metrics, "thresholds": [low, high]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

