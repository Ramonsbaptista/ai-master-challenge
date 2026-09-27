from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "all_tickets_processed_improved_v3.csv"
SPLIT = ROOT / "artifacts" / "split_ids.json"
MODEL = ROOT / "artifacts" / "model-v1.0.0.joblib"
OUT = ROOT / "outputs" / "jev_evaluation"
SAMPLE = OUT / "sample_bilingual.csv"
RESULTS = OUT / "jev_results.jsonl"
AUDIT_JSON = OUT / "audit_jev_data.json"
AUDIT_MD = OUT / "audit_jev_data.md"
SEED = 20260922
CLASSES = ["Access", "Administrative rights", "HR Support", "Hardware",
           "Internal Project", "Miscellaneous", "Purchase", "Storage"]


def record_ids(frame: pd.DataFrame) -> pd.Series:
    return pd.Series([
        hashlib.sha256(f"{i}\x1f{text}\x1f{label}".encode()).hexdigest()
        for i, (text, label) in enumerate(zip(frame.Document, frame.Topic_group, strict=True))
    ], index=frame.index)


def intended_sample(frame: pd.DataFrame, ids: list[str], seed: int) -> pd.DataFrame:
    subset = frame[frame.record_id.isin(set(ids))]
    pieces = []
    for i, label in enumerate(CLASSES):
        pieces.append(subset[subset.Topic_group == label].sample(n=100, random_state=seed + i))
    return pd.concat(pieces)


def metrics(y_true: list[str], y_pred: list[str]) -> dict:
    cm = confusion_matrix(y_true, y_pred, labels=CLASSES)
    total = int(cm.sum())
    rows = []
    for i, label in enumerate(CLASSES):
        vp = int(cm[i, i]); fn = int(cm[i].sum() - vp)
        fp = int(cm[:, i].sum() - vp); vn = total - vp - fn - fp
        p = vp / (vp + fp) if vp + fp else 0.0
        r = vp / (vp + fn) if vp + fn else 0.0
        f1 = 2 * p * r / (p + r) if p + r else 0.0
        rows.append({"class": label, "n": vp + fn, "VP": vp, "FP": fp, "FN": fn, "VN": vn,
                     "precision": p, "recall": r, "f1": f1})
    return {"n": total, "confusion_matrix": cm.tolist(), "per_class": rows,
            "accuracy": float(np.trace(cm) / total),
            "macro_f1": float(np.mean([r["f1"] for r in rows])),
            "weighted_f1": float(sum(r["f1"] * r["n"] for r in rows) / total),
            "row_sums": cm.sum(axis=1).astype(int).tolist(),
            "column_sums": cm.sum(axis=0).astype(int).tolist()}


def text_profile(series: pd.Series) -> dict:
    texts = series.astype(str)
    wc = texts.str.split().str.len().to_numpy()
    punctuation = texts.str.contains(r"[.,!?;:]", regex=True)
    short_share = []
    adjacent_dup = []
    header_noise = []
    for text in texts:
        tok = text.lower().split()
        short_share.append(sum(len(t) <= 2 for t in tok) / max(len(tok), 1))
        adjacent_dup.append(any(a == b for a, b in zip(tok, tok[1:])))
        header_noise.append(bool(set(tok) & {"pm", "am", "sent", "monday", "tuesday", "wednesday",
                                             "thursday", "friday", "january", "february", "march",
                                             "april", "may", "june", "july", "august", "september",
                                             "october", "november", "december"}))
    return {"n": len(texts), "word_count_mean": float(wc.mean()), "word_count_median": float(np.median(wc)),
            "word_count_p10": float(np.quantile(wc, .1)), "word_count_p90": float(np.quantile(wc, .9)),
            "punctuation_present_n": int(punctuation.sum()),
            "punctuation_present_rate": float(punctuation.mean()),
            "mean_share_tokens_len_le_2": float(np.mean(short_share)),
            "adjacent_duplicate_n": int(sum(adjacent_dup)),
            "header_or_date_noise_n": int(sum(header_noise))}


def class_tokens(sample: pd.DataFrame) -> dict:
    stop = {"the", "to", "and", "a", "of", "for", "in", "on", "is", "it", "please", "hi", "hello",
            "thanks", "thank", "dear", "with", "we", "you", "be", "this", "that", "from", "pm", "am"}
    token_sets = {c: Counter() for c in CLASSES}
    totals = Counter()
    for row in sample.itertuples(index=False):
        tokens = [t for t in re.findall(r"[a-z]+", str(row.Document).lower()) if len(t) > 2 and t not in stop]
        token_sets[row.Topic_group].update(tokens)
        totals.update(tokens)
    out = {}
    for c in CLASSES:
        # Razao suavizada classe/restante: descritiva, nao inferencial.
        scored = []
        class_total = sum(token_sets[c].values())
        other_total = sum(totals.values()) - class_total
        vocab = len(totals)
        for token, count in token_sets[c].items():
            if count < 3:
                continue
            other = totals[token] - count
            score = math.log((count + 1) / (class_total + vocab)) - math.log((other + 1) / (other_total + vocab))
            scored.append((score, count, token))
        out[c] = [{"token": t, "count_in_class": n, "log_ratio_smoothed": s}
                  for s, n, t in sorted(scored, reverse=True)[:15]]
    return out


def confusion_examples(joined: pd.DataFrame, partition: str, language: str) -> list[dict]:
    x = joined[(joined.partition == partition) & (joined.language == language)].copy()
    bad = x[x.Topic_group != x.prediction]
    pairs = (bad.groupby(["Topic_group", "prediction"]).size().reset_index(name="n")
             .sort_values(["n", "Topic_group", "prediction"], ascending=[False, True, True]))
    result = []
    for pair in pairs.head(12).itertuples(index=False):
        candidates = bad[(bad.Topic_group == pair.Topic_group) & (bad.prediction == pair.prediction)]
        row = candidates.sort_values("confidence", ascending=False).iloc[0]
        col = "Document" if language == "en" else "Document_pt"
        result.append({"true": pair.Topic_group, "pred": pair.prediction, "n": int(pair.n),
                       "example_confidence": float(row.confidence), "example": str(row[col])[:500]})
    return result


def main() -> None:
    frame = pd.read_csv(DATA)
    frame["record_id"] = record_ids(frame)
    split = json.loads(SPLIT.read_text(encoding="utf-8"))
    sample = pd.read_csv(SAMPLE)
    rows = [json.loads(line) for line in RESULTS.read_text(encoding="utf-8").splitlines() if line]
    results = pd.DataFrame(rows)
    joined = results.merge(sample, left_on=["record_id", "true_label", "partition"],
                           right_on=["record_id", "Topic_group", "partition"], how="left", validate="many_to_one")

    model = joblib.load(MODEL)
    metric_sets = {}
    for partition in ("validation", "test"):
        base = sample[sample.partition == partition]
        for lang, col in (("en", "Document"), ("pt", "Document_pt")):
            jev = results[(results.partition == partition) & (results.language == lang)]
            metric_sets[f"jev_{partition}_{lang}"] = metrics(jev.true_label.tolist(), jev.prediction.tolist())
            metric_sets[f"tfidf_{partition}_{lang}"] = metrics(base.Topic_group.tolist(), model.predict(base[col]).tolist())

    membership = {}
    id_to_partition = {rid: p for p in ("train", "validation", "test") for rid in split[p]}
    for partition in ("validation", "test"):
        s = sample[sample.partition == partition]
        membership[partition] = {
            "n": len(s), "ids_in_declared_partition_n": int(sum(id_to_partition.get(x) == partition for x in s.record_id)),
            "class_counts": s.Topic_group.value_counts().sort_index().to_dict(),
            "unique_ids_n": int(s.record_id.nunique())}
    membership["sha256_en_match_n"] = int(sum(
        hashlib.sha256(str(t).encode()).hexdigest() == h for t, h in zip(sample.Document, sample.sha256_en, strict=True)))

    overlaps = {}
    for partition, seed in (("validation", SEED + 100), ("test", SEED + 200)):
        intended = intended_sample(frame, split[partition], seed)
        observed = sample[sample.partition == partition]
        overlaps[partition] = {"n_each": 800,
            "overlap_n": len(set(intended.record_id) & set(observed.record_id)),
            "overlap_by_class": {c: len(set(intended[intended.Topic_group == c].record_id) &
                                             set(observed[observed.Topic_group == c].record_id)) for c in CLASSES}}

    top_confusions = {}
    examples = {}
    for partition in ("validation", "test"):
        for lang in ("en", "pt"):
            key = f"{partition}_{lang}"
            examples[key] = confusion_examples(joined, partition, lang)
            m = metric_sets[f"jev_{partition}_{lang}"]
            cm = np.array(m["confusion_matrix"]); np.fill_diagonal(cm, 0)
            pairs = []
            for i, j in np.argwhere(cm > 0):
                pairs.append({"true": CLASSES[i], "pred": CLASSES[j], "n": int(cm[i, j])})
            top_confusions[key] = sorted(pairs, key=lambda z: (-z["n"], z["true"], z["pred"]))[:15]

    confidence = {}
    for partition in ("validation", "test"):
        for lang in ("en", "pt"):
            x = results[(results.partition == partition) & (results.language == lang)]
            confidence[f"{partition}_{lang}"] = {
                "n": len(x), "confidence_mean": float(x.confidence.mean()),
                "confidence_eq_1_n": int((x.confidence == 1).sum()),
                "confidence_ge_0_9_n": int((x.confidence >= .9).sum()),
                "accuracy_at_ge_0_9": float((x[x.confidence >= .9].prediction == x[x.confidence >= .9].true_label).mean()),
                "n_at_ge_0_9": int((x.confidence >= .9).sum())}

    paired_test = results[results.partition == "test"].pivot(index="record_id", columns="language", values="prediction")
    language_agreement = {"n": len(paired_test), "same_prediction_n": int((paired_test.en == paired_test.pt).sum()),
                          "same_prediction_rate": float((paired_test.en == paired_test.pt).mean())}

    audit = {
        "provenance": {"script": str(Path(__file__).resolve()), "inputs": [str(SAMPLE), str(RESULTS), str(DATA), str(SPLIT), str(MODEL)]},
        "membership_and_integrity": membership,
        "external_sampling_vs_04_intended": overlaps,
        "metrics": metric_sets,
        "top_confusions": top_confusions,
        "representative_high_confidence_errors": examples,
        "confidence": confidence,
        "language_prediction_agreement_test": language_agreement,
        "text_profile": {"en": text_profile(sample.Document), "pt": text_profile(sample.Document_pt)},
        "class_specific_tokens_sample_en": class_tokens(sample),
    }
    AUDIT_JSON.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = ["# Auditoria quantitativa dos dados do experimento Jev", "",
             "Método: reconstrução direta a partir de `jev_results.jsonl`; matriz com linhas=classe real e colunas=predição, ordem " + ", ".join(CLASSES) + ".",
             "Premissa: `sample_bilingual.csv` é a amostra efetivamente enviada; a associação foi conferida por record_id, partição e rótulo.", ""]
    for key, m in metric_sets.items():
        lines += [f"## {key} (n={m['n']})", "",
                  f"Acurácia = soma da diagonal / n = {sum(m['confusion_matrix'][i][i] for i in range(8))}/{m['n']} = {m['accuracy']:.6f}.",
                  f"Macro-F1 = média simples dos oito F1 = {m['macro_f1']:.6f}; F1 ponderado por suporte = {m['weighted_f1']:.6f}.",
                  f"Checagem: somas das linhas={m['row_sums']}; soma total={sum(m['row_sums'])}.", ""]
        for r in m["per_class"]:
            lines.append(f"- {r['class']} (n={r['n']}): VP={r['VP']}, FP={r['FP']}, FN={r['FN']}, VN={r['VN']}; "
                         f"precisão = {r['VP']}/({r['VP']}+{r['FP']}) = {r['precision']:.6f}; "
                         f"recall = {r['VP']}/({r['VP']}+{r['FN']}) = {r['recall']:.6f}; "
                         f"F1 = 2×{r['precision']:.6f}×{r['recall']:.6f}/({r['precision']:.6f}+{r['recall']:.6f}) = {r['f1']:.6f}.")
        lines.append("")
    AUDIT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"audit_json": str(AUDIT_JSON), "audit_md": str(AUDIT_MD),
                      "overlap": overlaps, "test_metrics": {k: {"n": v["n"], "accuracy": v["accuracy"], "macro_f1": v["macro_f1"]}
                                                            for k, v in metric_sets.items() if "_test_" in k}},
                      ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
