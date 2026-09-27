from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import math
import os
import random
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError

import joblib
import numpy as np
import pandas as pd
from scipy.stats import binomtest
from sklearn.metrics import confusion_matrix


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[2]
DATA = ROOT / "data" / "all_tickets_processed_improved_v3.csv"
SPLIT = ROOT / "artifacts" / "split_ids.json"
MODEL = ROOT / "artifacts" / "model-v1.0.0.joblib"
OUT = ROOT / "outputs" / "jev_evaluation"
SEED = 20260922
API_URL = "https://ai-gateway.vercel.sh/v1/evaluate"
JEV_INPUT_USD_PER_MILLION = 0.04
CLASSES = ["Access", "Administrative rights", "HR Support", "Hardware",
           "Internal Project", "Miscellaneous", "Purchase", "Storage"]

CRITERIA = {
    "Access": "Requests or problems involving access to an account, system, application, folder, group, VPN or service, including account creation, login/password and adding users when the core need is access.",
    "Administrative rights": "Requests for elevated, administrator or installation permissions on a device or application; choose this over Access only when privilege elevation is the core need.",
    "HR Support": "Human-resources processes and employee administration, including leave, time sheets, payroll, benefits, onboarding or offboarding workflow questions.",
    "Hardware": "Physical devices, peripherals, phones, laptops, monitors, printers, device performance or a technical malfunction not better covered by another specific class.",
    "Internal Project": "Work explicitly about an internal project, project setup, project administration, project resources or delivery coordination rather than an individual support incident.",
    "Miscellaneous": "A meaningful support request that does not fit the other seven classes, or text with too little information to assign a specific class. Do not infer missing facts.",
    "Purchase": "Buying, ordering, approving, quoting or procuring equipment, software, licenses or services.",
    "Storage": "File storage capacity, disk space, shared drives, folders, backup, retention, archiving or recovery where storage is the core issue.",
}
INSTRUCTIONS = (
    "Classify this internal IT/support ticket into exactly one class. Use only evidence in the "
    "ticket. If the text is uninformative or no specific class is supported, choose Miscellaneous."
)


def load_key() -> str:
    key = os.environ.get("AI_GATEWAY_API_KEY", "").strip()
    if key:
        return key
    env_path = PROJECT / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("AI_GATEWAY_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("AI_GATEWAY_API_KEY ausente do ambiente e do .env.")


def record_ids(frame: pd.DataFrame) -> pd.Series:
    return pd.Series([
        hashlib.sha256(f"{i}\x1f{text}\x1f{label}".encode()).hexdigest()
        for i, (text, label) in enumerate(zip(frame.Document, frame.Topic_group, strict=True))
    ], index=frame.index)


def load_frame() -> tuple[pd.DataFrame, dict]:
    frame = pd.read_csv(DATA)
    frame["record_id"] = record_ids(frame)
    split = json.loads(SPLIT.read_text(encoding="utf-8"))
    return frame, split


def stratified_sample(frame: pd.DataFrame, ids: list[str], n_class: int, seed: int) -> pd.DataFrame:
    subset = frame[frame.record_id.isin(set(ids))]
    pieces = []
    for i, label in enumerate(CLASSES):
        group = subset[subset.Topic_group == label]
        if len(group) < n_class:
            raise RuntimeError(f"{label}: apenas {len(group)} registros; solicitados {n_class}.")
        pieces.append(group.sample(n=n_class, random_state=seed + i))
    return pd.concat(pieces).sort_values("record_id").reset_index(drop=True)


def http_json(url: str, payload: dict | None = None, headers: dict | None = None,
              timeout: int = 90) -> tuple[dict, float]:
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(url, data=data, headers=headers or {}, method="GET" if data is None else "POST")
    start = time.perf_counter()
    with urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8"))
    return body, time.perf_counter() - start


def translate_one(text: str) -> str:
    # Argos Translate 1.11.0 + pacote en_pt 1.9, executado localmente; não usa o rótulo.
    import argostranslate.translate
    return argostranslate.translate.translate(str(text), "en", "pt").strip()


def initialize_translation_engine() -> None:
    """Inicializa e armazena o pipeline Argos/Stanza antes de abrir threads."""
    warmup = translate_one("translation engine warmup")
    if not warmup:
        raise RuntimeError("Falha ao inicializar o motor de traducao.")


def translate_batch(items: list[tuple[str, str]]) -> dict[str, str]:
    import argostranslate.translate
    markers = [f"ZXQSEP{i:04d}ZXQ" for i in range(1, len(items))]
    combined = str(items[0][1])
    for marker, (_, text) in zip(markers, items[1:], strict=True):
        combined += f". {marker} " + str(text)
    output = argostranslate.translate.translate(combined, "en", "pt")
    pieces = [output]
    for marker in markers:
        tail = pieces.pop()
        split = tail.split(marker, 1)
        if len(split) != 2:
            raise RuntimeError(f"Marcador de lote perdido na tradução: {marker}")
        pieces.extend(split)
    if len(pieces) != len(items):
        raise RuntimeError("Quantidade de traduções diverge do lote.")
    return {h: piece.strip(" .") for (h, _), piece in zip(items, pieces, strict=True)}


def jev_one(text: str, key: str, attempt_limit: int = 4) -> dict:
    payload = {"model": "typesafe-ai/jev", "state": text,
               "questions": {"topic": {"type": "choice", "instructions": INSTRUCTIONS,
                                          "criteria": CRITERIA}}}
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    last = None
    for attempt in range(attempt_limit):
        try:
            body, latency = http_json(API_URL, payload, headers)
            answer = body["answers"]["topic"]
            probs = answer["probabilities"]
            if answer["choice"] not in CLASSES or set(probs) != set(CLASSES):
                raise ValueError("Resposta contém classes inesperadas.")
            if not math.isclose(sum(float(v) for v in probs.values()), 1.0, abs_tol=1e-5):
                raise ValueError("Probabilidades não somam 1.")
            usage = body.get("usage", {})
            return {"prediction": answer["choice"], "confidence": float(answer["confidence"]),
                    "probabilities": {k: float(probs[k]) for k in CLASSES},
                    "input_tokens": int(usage.get("inputTokens", 0)),
                    "output_tokens": int(usage.get("outputTokens", 0)),
                    "latency_s": latency, "attempts": attempt + 1}
        except Exception as exc:  # retry controlado; mensagem não inclui chave nem corpo
            last = f"{type(exc).__name__}: {exc}"
            time.sleep(0.5 * (2 ** attempt))
    raise RuntimeError(last)


def parallel_map(fn, items: list, workers: int, label: str) -> list:
    results = [None] * len(items)
    done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(fn, item): i for i, item in enumerate(items)}
        for future in concurrent.futures.as_completed(futures):
            idx = futures[future]
            results[idx] = future.result()
            done += 1
            if done % 100 == 0 or done == len(items):
                print(f"{label}: {done}/{len(items)}", flush=True)
    return results


def save_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def append_jsonl(path: Path, row: dict) -> None:
    """Persiste uma chamada concluida antes de agendar/aguardar a proxima."""
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def call_key(row: dict) -> tuple[str, str, str]:
    return str(row["record_id"]), str(row["partition"]), str(row["language"])


def prepare(n_class: int, workers: int) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    frame, split = load_frame()
    val = stratified_sample(frame, split["validation"], n_class, SEED + 100)
    test = stratified_sample(frame, split["test"], n_class, SEED + 200)
    selected = pd.concat([val.assign(partition="validation"), test.assign(partition="test")])
    texts = selected.Document.tolist()
    cache_path = OUT / "translation_cache.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    pairs = [(hashlib.sha256(text.encode()).hexdigest(), text) for text in texts]
    missing = [(h, text) for h, text in pairs if h not in cache]
    completed = len(pairs) - len(missing)
    if missing:
        # A primeira chamada constroi o pipeline Stanza e pode escrever/ler recursos.
        # Ela deve ocorrer uma unica vez na thread principal; depois o objeto em cache
        # pode ser reutilizado pelas threads que processam os lotes.
        initialize_translation_engine()
        batches = [missing[i:i + 20] for i in range(0, len(missing), 20)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(translate_batch, batch): batch for batch in batches}
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                cache.update(result)
                completed += len(result)
                cache_path.write_text(json.dumps(cache, ensure_ascii=False) + "\n", encoding="utf-8")
                print(f"tradução: {completed}/{len(pairs)} (cache={len(cache)})", flush=True)
    translated = [cache[h] for h, _ in pairs]
    cache_path.write_text(json.dumps(cache, ensure_ascii=False) + "\n", encoding="utf-8")
    selected["Document_pt"] = translated
    selected.to_csv(OUT / "sample_bilingual.csv", index=False, lineterminator="\n")
    meta = {"seed": SEED, "n_per_class_per_partition": n_class,
            "n_total_source": len(selected), "translation_engine": "Argos Translate 1.11.0, en_pt 1.9, local",
            "translation_target": "pt-PT", "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "translation_limitation": (
                "Tradução automática para português europeu; não representa texto originalmente "
                "escrito por clientes brasileiros e não mede diretamente desempenho em pt-BR."
            ),
            "test_ids_sha256": hashlib.sha256(("\n".join(test.record_id) + "\n").encode()).hexdigest(),
            "criteria": CRITERIA, "instructions": INSTRUCTIONS}
    (OUT / "protocol.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "prepared", "n": len(selected)}, ensure_ascii=False))


def run_calls(workers: int, pilot: bool = False) -> None:
    key = load_key()
    sample = pd.read_csv(OUT / "sample_bilingual.csv")
    if pilot:
        sample = sample[sample.partition == "validation"].groupby("Topic_group", sort=True).head(1)
    tasks = []
    for row in sample.itertuples(index=False):
        for language, text in (("en", row.Document), ("pt", row.Document_pt)):
            tasks.append({"record_id": row.record_id, "partition": row.partition,
                          "true_label": row.Topic_group, "language": language, "text": text})
    def call(task):
        result = jev_one(task["text"], key)
        return {k: v for k, v in task.items() if k != "text"} | result
    path = OUT / ("pilot_results.jsonl" if pilot else "jev_results.jsonl")
    existing = read_jsonl(path) if path.exists() else []
    if len({call_key(r) for r in existing}) != len(existing):
        raise RuntimeError(f"Checkpoint com chaves duplicadas: {path}")
    completed = {call_key(r) for r in existing}
    pending = [task for task in tasks if call_key(task) not in completed]
    rows = list(existing)
    label = "Jev piloto" if pilot else "Jev"
    print(f"{label}: retomando {len(existing)} concluida(s); {len(pending)} pendente(s)", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(call, task): task for task in pending}
        for future in concurrent.futures.as_completed(futures):
            row = future.result()
            append_jsonl(path, row)
            rows.append(row)
            done = len(rows)
            if done % 25 == 0 or done == len(tasks):
                print(f"{label}: {done}/{len(tasks)} persistidas", flush=True)
    if len(rows) != len(tasks):
        raise RuntimeError(f"Resultado incompleto: {len(rows)}/{len(tasks)}")
    print(json.dumps({"status": "ok", "calls": len(rows),
                      "input_tokens": sum(r["input_tokens"] for r in rows),
                      "output_tokens": sum(r["output_tokens"] for r in rows)}, ensure_ascii=False))


def per_class(y_true, y_pred) -> tuple[np.ndarray, list[dict], dict]:
    cm = confusion_matrix(y_true, y_pred, labels=CLASSES)
    total = int(cm.sum())
    rows = []
    for i, label in enumerate(CLASSES):
        vp = int(cm[i, i]); fn = int(cm[i, :].sum() - vp)
        fp = int(cm[:, i].sum() - vp); vn = total - vp - fn - fp
        precision = vp / (vp + fp) if vp + fp else 0.0
        recall = vp / (vp + fn) if vp + fn else 0.0
        specificity = vn / (vn + fp) if vn + fp else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        rows.append({"class": label, "n": vp + fn, "VP": vp, "FP": fp, "FN": fn, "VN": vn,
                     "precision": precision, "recall": recall, "specificity": specificity, "f1": f1})
    assert total == len(y_true) and all(r["n"] == 100 for r in rows)
    aggregate = {"n": total, "accuracy": float(np.trace(cm) / total),
                 "macro_f1": float(np.mean([r["f1"] for r in rows])),
                 "weighted_f1": float(sum(r["f1"] * r["n"] for r in rows) / total)}
    return cm, rows, aggregate


def calibration(rows: list[dict]) -> dict:
    y = np.array([CLASSES.index(r["true_label"]) for r in rows])
    p = np.array([[r["probabilities"][c] for c in CLASSES] for r in rows], dtype=float)
    p = np.clip(p, 1e-15, 1)
    onehot = np.eye(len(CLASSES))[y]
    confidence = p.max(axis=1); correct = (p.argmax(axis=1) == y).astype(float)
    bins = np.linspace(0, 1, 11); ece = 0.0; details = []
    for lo, hi in zip(bins[:-1], bins[1:]):
        mask = (confidence >= lo) & (confidence < hi if hi < 1 else confidence <= hi)
        n = int(mask.sum())
        if n:
            acc = float(correct[mask].mean()); conf = float(confidence[mask].mean())
            ece += n / len(rows) * abs(acc - conf)
            details.append({"from": lo, "to": hi, "n": n, "accuracy": acc, "mean_confidence": conf})
    return {"n": len(rows), "log_loss": float(-np.log(p[np.arange(len(y)), y]).mean()),
            "brier_multiclass": float(np.mean(np.sum((p - onehot) ** 2, axis=1))),
            "ece_10_equal_width": float(ece), "bins": details}


def choose_threshold(rows: list[dict], target_accuracy: float = .90) -> dict:
    candidates = sorted({float(r["confidence"]) for r in rows})
    feasible = []
    for threshold in candidates:
        accepted = [r for r in rows if r["confidence"] >= threshold]
        if len(accepted) >= 100:
            accuracy = np.mean([r["prediction"] == r["true_label"] for r in accepted])
            if accuracy >= target_accuracy:
                feasible.append((len(accepted), -threshold, accuracy, threshold))
    if not feasible:
        return {"threshold": None, "validation_n": len(rows), "accepted_n": 0,
                "target_accuracy": target_accuracy}
    n, _, accuracy, threshold = max(feasible)
    return {"threshold": threshold, "validation_n": len(rows), "accepted_n": n,
            "coverage": n / len(rows), "accuracy": float(accuracy), "target_accuracy": target_accuracy}


def selective(rows: list[dict], threshold: float | None) -> dict:
    if threshold is None:
        return {"n": len(rows), "accepted_n": 0, "coverage": 0.0, "accuracy": None, "errors": 0}
    accepted = [r for r in rows if r["confidence"] >= threshold]
    correct = sum(r["prediction"] == r["true_label"] for r in accepted)
    return {"n": len(rows), "accepted_n": len(accepted), "coverage": len(accepted) / len(rows),
            "accuracy": correct / len(accepted) if accepted else None, "errors": len(accepted) - correct}


def mcnemar(a_correct: np.ndarray, b_correct: np.ndarray) -> dict:
    a_only = int(np.sum(a_correct & ~b_correct)); b_only = int(np.sum(~a_correct & b_correct))
    discordant = a_only + b_only
    p = float(binomtest(min(a_only, b_only), discordant, .5).pvalue) if discordant else 1.0
    return {"n": len(a_correct), "a_only_correct": a_only, "b_only_correct": b_only,
            "discordant_n": discordant, "exact_binomial_p": p}


def bootstrap_difference(y: list[str], a: list[str], b: list[str], reps: int = 5000) -> dict:
    rng = np.random.default_rng(SEED); y = np.asarray(y); a = np.asarray(a); b = np.asarray(b)
    diffs = np.empty(reps)
    for i in range(reps):
        idx = rng.integers(0, len(y), len(y))
        diffs[i] = np.mean(a[idx] == y[idx]) - np.mean(b[idx] == y[idx])
    observed = float(np.mean(a == y) - np.mean(b == y))
    return {"n": len(y), "method": "paired percentile bootstrap, 5000 resamples",
            "difference_accuracy": observed, "ci95": [float(np.quantile(diffs, .025)), float(np.quantile(diffs, .975))]}


def macro_f1_value(y: np.ndarray, pred: np.ndarray) -> float:
    cm = confusion_matrix(y, pred, labels=CLASSES)
    values = []
    for i in range(len(CLASSES)):
        vp = cm[i, i]; fp = cm[:, i].sum() - vp; fn = cm[i, :].sum() - vp
        precision = vp / (vp + fp) if vp + fp else 0.0
        recall = vp / (vp + fn) if vp + fn else 0.0
        values.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return float(np.mean(values))


def bootstrap_macro_f1_difference(y: list[str], a: list[str], b: list[str], reps: int = 5000) -> dict:
    rng = np.random.default_rng(SEED + 1); y = np.asarray(y); a = np.asarray(a); b = np.asarray(b)
    diffs = np.empty(reps)
    for i in range(reps):
        idx = rng.integers(0, len(y), len(y))
        diffs[i] = macro_f1_value(y[idx], a[idx]) - macro_f1_value(y[idx], b[idx])
    observed = macro_f1_value(y, a) - macro_f1_value(y, b)
    return {"n": len(y), "method": "paired percentile bootstrap, 5000 resamples",
            "difference_macro_f1": observed,
            "ci95": [float(np.quantile(diffs, .025)), float(np.quantile(diffs, .975))]}


def stability_and_ood(workers: int) -> None:
    key = load_key(); sample = pd.read_csv(OUT / "sample_bilingual.csv")
    # 50 tickets x 3 repeticoes = 150 chamadas, balanceadas tanto quanto 50/8 permite.
    base = sample[sample.partition == "test"].groupby("Topic_group", sort=True).head(7).head(50)
    tasks = [(str(r.record_id), str(r.Document), rep) for r in base.itertuples() for rep in range(3)]
    def stable(task):
        rid, text, rep = task; result = jev_one(text, key)
        return {"record_id": rid, "rep": rep} | result
    stable_rows = parallel_map(stable, tasks, workers, "estabilidade")
    ood_texts = (["", "hello", "thank you", "ok", "please help", "urgent", "test", "n/a",
                  "bom dia", "obrigado", "ok", "por favor ajude", "urgente", "teste", "sem detalhes", "."] * 5)
    ood_rows = parallel_map(lambda text: {"text": text} | jev_one(text, key), ood_texts, workers, "não informativos")
    save_jsonl(OUT / "stability_results.jsonl", stable_rows)
    save_jsonl(OUT / "uninformative_results.jsonl", ood_rows)


def report() -> None:
    sample = pd.read_csv(OUT / "sample_bilingual.csv")
    results = read_jsonl(OUT / "jev_results.jsonl")
    model = joblib.load(MODEL)
    test_sample = sample[sample.partition == "test"].copy()
    current = {}
    for lang, col in (("en", "Document"), ("pt", "Document_pt")):
        current[lang] = dict(zip(test_sample.record_id, model.predict(test_sample[col])))
    full = {}
    for r in results:
        full[(r["record_id"], r["language"], r["partition"])] = r
    analysis = {"method": {"seed": SEED, "classes": CLASSES,
                            "test_sampling": "100 per class from frozen test; no tuning",
                            "validation_sampling": "100 per class; threshold only",
                            "threshold_rule": "maximum coverage with validation accuracy >= 90% and accepted n>=100"}}
    metrics_rows = []
    thresholds = {}
    for lang in ("en", "pt"):
        val_rows = [r for r in results if r["partition"] == "validation" and r["language"] == lang]
        test_rows = [r for r in results if r["partition"] == "test" and r["language"] == lang]
        thresholds[lang] = choose_threshold(val_rows)
        for system in ("jev", "current"):
            y = [r["true_label"] for r in test_rows]
            pred = [r["prediction"] for r in test_rows] if system == "jev" else [current[lang][r["record_id"]] for r in test_rows]
            cm, pc, agg = per_class(y, pred)
            analysis[f"{system}_{lang}"] = {"confusion_matrix": cm.tolist(), "per_class": pc, "aggregate": agg}
            metrics_rows += [{"system": system, "language": lang, **row} for row in pc]
        analysis[f"calibration_jev_{lang}"] = calibration(test_rows)
        analysis[f"routing_jev_{lang}"] = {"validation": thresholds[lang],
                                             "test": selective(test_rows, thresholds[lang]["threshold"])}
        y = np.array([r["true_label"] for r in test_rows])
        jev = np.array([r["prediction"] for r in test_rows])
        cur = np.array([current[lang][r["record_id"]] for r in test_rows])
        analysis[f"jev_vs_current_{lang}"] = {"mcnemar": mcnemar(jev == y, cur == y),
                                                "bootstrap_accuracy": bootstrap_difference(y.tolist(), jev.tolist(), cur.tolist()),
                                                "bootstrap_macro_f1": bootstrap_macro_f1_difference(y.tolist(), jev.tolist(), cur.tolist())}
    en = [r for r in results if r["partition"] == "test" and r["language"] == "en"]
    pt_by_id = {r["record_id"]: r for r in results if r["partition"] == "test" and r["language"] == "pt"}
    pt = [pt_by_id[r["record_id"]] for r in en]
    y = np.array([r["true_label"] for r in en]); ep = np.array([r["prediction"] for r in en]); pp = np.array([r["prediction"] for r in pt])
    analysis["jev_language_effect"] = {"mcnemar": mcnemar(ep == y, pp == y),
                                        "bootstrap_accuracy": bootstrap_difference(y.tolist(), ep.tolist(), pp.tolist()),
                                        "bootstrap_macro_f1": bootstrap_macro_f1_difference(y.tolist(), ep.tolist(), pp.tolist())}
    cen = np.array([current["en"][r["record_id"]] for r in en])
    cpt = np.array([current["pt"][r["record_id"]] for r in en])
    analysis["current_language_effect"] = {"mcnemar": mcnemar(cen == y, cpt == y),
        "bootstrap_accuracy": bootstrap_difference(y.tolist(), cen.tolist(), cpt.tolist()),
        "bootstrap_macro_f1": bootstrap_macro_f1_difference(y.tolist(), cen.tolist(), cpt.tolist())}
    lat = [r["latency_s"] for r in results]
    analysis["usage_primary"] = {"calls": len(results), "input_tokens": sum(r["input_tokens"] for r in results),
                                  "output_tokens": sum(r["output_tokens"] for r in results),
                                  "price_assumption": "US$ 0.04 por 1 milhão de tokens de entrada; saída sem preço publicado",
                                  "estimated_cost_usd": sum(r["input_tokens"] for r in results) / 1_000_000 * JEV_INPUT_USD_PER_MILLION,
                                  "retries": sum(r["attempts"] - 1 for r in results),
                                  "latency_s": {"n": len(lat), "mean": statistics.mean(lat),
                                                "p50": float(np.quantile(lat, .5)), "p95": float(np.quantile(lat, .95)),
                                                "p99": float(np.quantile(lat, .99))}}
    if (OUT / "stability_results.jsonl").exists():
        sr = read_jsonl(OUT / "stability_results.jsonl"); ur = read_jsonl(OUT / "uninformative_results.jsonl")
        groups = {}
        for r in sr: groups.setdefault(r["record_id"], []).append(r)
        stable_all = sum(len({x["prediction"] for x in rows}) == 1 for rows in groups.values())
        ranges = [max(x["confidence"] for x in rows) - min(x["confidence"] for x in rows) for rows in groups.values()]
        analysis["stability"] = {"n_unique": len(groups), "calls": len(sr), "all_three_same_n": stable_all,
                                  "all_three_same_rate": stable_all / len(groups),
                                  "confidence_range_mean": statistics.mean(ranges), "confidence_range_max": max(ranges)}
        analysis["uninformative"] = {"n": len(ur), "miscellaneous_n": sum(r["prediction"] == "Miscellaneous" for r in ur),
                                      "miscellaneous_rate": np.mean([r["prediction"] == "Miscellaneous" for r in ur]),
                                      "confidence_mean": statistics.mean(r["confidence"] for r in ur),
                                      "confidence_ge_0_9_n": sum(r["confidence"] >= .9 for r in ur)}
        analysis["usage_auxiliary"] = {"calls": len(sr) + len(ur),
            "input_tokens": sum(r["input_tokens"] for r in sr + ur), "output_tokens": sum(r["output_tokens"] for r in sr + ur)}
    (OUT / "analysis.json").write_text(json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pd.DataFrame(metrics_rows).to_csv(OUT / "per_class_metrics.csv", index=False, lineterminator="\n")
    print(json.dumps({k: analysis[k]["aggregate"] for k in ("jev_en", "current_en", "jev_pt", "current_pt")}, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "pilot", "run", "aux", "report"])
    parser.add_argument("--n-class", type=int, default=100)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    if args.action == "prepare": prepare(args.n_class, args.workers)
    elif args.action == "pilot": run_calls(args.workers, pilot=True)
    elif args.action == "run": run_calls(args.workers)
    elif args.action == "aux": stability_and_ood(args.workers)
    else: report()


if __name__ == "__main__":
    main()
