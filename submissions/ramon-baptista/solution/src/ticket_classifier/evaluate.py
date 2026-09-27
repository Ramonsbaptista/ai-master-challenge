from __future__ import annotations

import json

import numpy as np
import pandas as pd

from .core import (ARTIFACTS, DATA_PATH, aggregate_metrics, assert_consistency, load_data,
                   load_manifest, load_verified_model, per_class_metrics, route,
                   routing_thresholds, sha256_file)
from .language import load_language_guard, should_send_to_human
from .service import MAX_TICKET_LENGTH


def reproduce() -> dict:
    model, manifest = load_verified_model()
    for key in ("data", "split", "frozen_test", "language_guard"):
        info = manifest["files"][key]
        path = DATA_PATH if key == "data" else ARTIFACTS / info["path"]
        if sha256_file(path) != info["sha256"]:
            raise AssertionError(f"Hash divergente: {key}.")
    frame = load_data().set_index("record_id", drop=False)
    frozen = pd.read_csv(ARTIFACTS / manifest["files"]["frozen_test"]["path"])
    if frozen["record_id"].duplicated().any() or not frozen["record_id"].isin(frame.index).all():
        raise AssertionError("IDs congelados duplicados ou ausentes na Base 2.")
    test = frame.loc[frozen["record_id"]]
    if not np.array_equal(test["Topic_group"].to_numpy(), frozen["expected_label"].to_numpy()):
        raise AssertionError("Rótulos reais divergem do conjunto congelado.")
    pred = model.predict(test["Document"])
    scores = np.max(model.predict_proba(test["Document"]), axis=1)
    if not np.array_equal(pred, frozen["expected_prediction"].to_numpy()):
        raise AssertionError("Predições divergem das predições congeladas.")
    if not np.allclose(scores, frozen["expected_score"].to_numpy(), rtol=1e-12, atol=1e-12):
        raise AssertionError("Scores divergem dos scores congelados.")
    low, high = routing_thresholds(manifest)
    bands = route(scores, low, high)
    if not np.array_equal(bands, frozen["expected_band"].to_numpy()):
        raise AssertionError("Faixas divergem das faixas congeladas.")
    classes = manifest["classes"]
    matrix, rows = per_class_metrics(test["Topic_group"], pred, classes)
    assert_consistency(matrix, rows, test["Topic_group"].to_numpy(), classes)
    metrics = aggregate_metrics(rows, matrix)
    if matrix.tolist() != manifest["test"]["confusion_matrix"]:
        raise AssertionError("Matriz reproduzida diverge do manifesto.")
    for key, value in metrics.items():
        if not np.isclose(value, manifest["test"]["metrics"][key]):
            raise AssertionError(f"Métrica {key} diverge do manifesto.")
    high_band = bands == "alta"
    within_size_limit = test["Document"].str.strip().str.len().to_numpy() <= MAX_TICKET_LENGTH
    language_diversion = np.zeros(len(test), dtype=bool)
    guard = load_language_guard()
    for index in np.flatnonzero(high_band & within_size_limit):
        language_diversion[index] = should_send_to_human(
            str(test.iloc[index]["Document"]), model, guard
        )[0]
    automated = high_band & within_size_limit & ~language_diversion
    correct = pred == test["Topic_group"].to_numpy()
    automated_n = int(automated.sum())
    effective_routing = {
        "high_band_n": int(high_band.sum()),
        "high_band_coverage": float(high_band.mean()),
        "blocked_by_size_n": int((high_band & ~within_size_limit).sum()),
        "language_eligible_n": int((high_band & within_size_limit).sum()),
        "blocked_by_language_n": int((high_band & within_size_limit & language_diversion).sum()),
        "automated_n": automated_n,
        "automated_coverage": automated_n / len(test),
        "automated_correct_n": int((automated & correct).sum()),
        "automated_accuracy": float(correct[automated].mean()),
        "human_n": int((~automated).sum()),
        "human_share": float((~automated).mean()),
    }
    return {"status": "ok", "n": len(test), "matrix": matrix.tolist(), "per_class": rows,
            "metrics": metrics, "effective_routing": effective_routing,
            "message": "Avaliação reproduzida sem refazer o split; hashes e expectativas conferem."}


def main() -> None:
    result = reproduce()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
