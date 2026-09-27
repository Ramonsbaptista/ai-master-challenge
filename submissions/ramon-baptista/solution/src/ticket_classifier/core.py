from __future__ import annotations

import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix


ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "all_tickets_processed_improved_v3.csv"
ARTIFACTS = ROOT / "artifacts"
OUTPUTS = ROOT / "outputs"


class PrototypeError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record_ids(frame: pd.DataFrame) -> pd.Series:
    return pd.Series(
        [hashlib.sha256(f"{i}\x1f{text}\x1f{label}".encode("utf-8")).hexdigest()
         for i, (text, label) in enumerate(zip(frame["Document"], frame["Topic_group"], strict=True))],
        index=frame.index,
        name="record_id",
    )


def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise PrototypeError(
            f"Causa: base do protótipo ausente em {DATA_PATH.relative_to(ROOT)}.\n"
            "Como corrigir: copie all_tickets_processed_improved_v3.csv para solution/data/.\n"
            "Diagnóstico: o modelo não pode ser executado sem a mesma Base 2 usada no treinamento."
        )
    frame = pd.read_csv(DATA_PATH)
    if list(frame.columns) != ["Document", "Topic_group"]:
        raise PrototypeError(
            "Causa: esquema da Base 2 diferente do esperado.\n"
            "Como corrigir: use o CSV original com colunas Document e Topic_group.\n"
            f"Diagnóstico: colunas encontradas: {list(frame.columns)}."
        )
    if frame.isna().any().any():
        raise PrototypeError(
            "Causa: a Base 2 contém valores nulos.\n"
            "Como corrigir: restaure a cópia íntegra da base.\n"
            "Diagnóstico: a integridade diverge da base usada para congelar o teste."
        )
    frame["record_id"] = record_ids(frame)
    return frame


def load_manifest() -> dict:
    path = ARTIFACTS / "manifest.json"
    if not path.exists():
        raise PrototypeError(
            "Causa: manifesto do modelo ausente.\n"
            "Como corrigir: restaure a pasta artifacts/ ou execute scripts/train_and_freeze.py.\n"
            "Diagnóstico: não há metadados para verificar o artefato."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def load_verified_model():
    manifest = load_manifest()
    model_path = ARTIFACTS / manifest["files"]["model"]["path"]
    actual = sha256_file(model_path)
    expected = manifest["files"]["model"]["sha256"]
    if actual != expected:
        raise PrototypeError(
            "Causa: hash do modelo não confere.\n"
            "Como corrigir: restaure o arquivo model.joblib versionado.\n"
            f"Diagnóstico: esperado {expected}; encontrado {actual}."
        )
    return joblib.load(model_path), manifest


def routing_thresholds(manifest: dict) -> tuple[float, float]:
    """Retorna os cortes cuja fonte unica e o manifesto selecionado na validacao."""
    cuts = manifest["routing_thresholds"]
    return float(cuts["low"]), float(cuts["high"])


def per_class_metrics(y_true, y_pred, classes: list[str]) -> tuple[np.ndarray, list[dict]]:
    matrix = confusion_matrix(y_true, y_pred, labels=classes)
    n = int(matrix.sum())
    rows = []
    for i, label in enumerate(classes):
        vp = int(matrix[i, i])
        fn = int(matrix[i, :].sum() - vp)
        fp = int(matrix[:, i].sum() - vp)
        vn = n - vp - fn - fp
        precision = vp / (vp + fp) if vp + fp else 0.0
        recall = vp / (vp + fn) if vp + fn else 0.0
        specificity = vn / (vn + fp) if vn + fp else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        rows.append({"class": label, "n": vp + fn, "VP": vp, "FP": fp, "FN": fn, "VN": vn,
                     "precision": precision, "recall": recall, "specificity": specificity, "f1": f1})
    return matrix, rows


def aggregate_metrics(rows: list[dict], matrix: np.ndarray) -> dict:
    n = int(matrix.sum())
    return {
        "n": n,
        "macro_f1": float(np.mean([r["f1"] for r in rows])),
        "weighted_f1": float(sum(r["f1"] * r["n"] for r in rows) / n),
        "accuracy": float(np.trace(matrix) / n),
    }


def assert_consistency(matrix: np.ndarray, rows: list[dict], y_true, classes: list[str]) -> None:
    n = len(y_true)
    if int(matrix.sum()) != n:
        raise AssertionError(f"Matriz soma {matrix.sum()}, mas teste tem n={n}.")
    counts = pd.Series(y_true).value_counts()
    for i, label in enumerate(classes):
        expected = int(counts.get(label, 0))
        if int(matrix[i, :].sum()) != expected or rows[i]["n"] != expected:
            raise AssertionError(f"Linha de {label} não bate com n da classe ({expected}).")
        r = rows[i]
        if r["VP"] + r["FN"] != expected or r["VP"] + r["FP"] + r["FN"] + r["VN"] != n:
            raise AssertionError(f"Contagens binárias inconsistentes para {label}.")


def route(scores: np.ndarray, low: float, high: float) -> np.ndarray:
    return np.where(scores >= high, "alta", np.where(scores >= low, "media", "baixa"))
