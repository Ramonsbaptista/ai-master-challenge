from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "all_tickets_processed_improved_v3.csv"
SPLIT = ROOT / "artifacts" / "split_ids.json"
SAMPLE = ROOT / "outputs" / "jev_evaluation" / "sample_bilingual.csv"
CLASSES = ["Access", "Administrative rights", "HR Support", "Hardware",
           "Internal Project", "Miscellaneous", "Purchase", "Storage"]
SEED = 20260922


def record_ids(frame: pd.DataFrame) -> pd.Series:
    return pd.Series([
        hashlib.sha256(f"{i}\x1f{text}\x1f{label}".encode()).hexdigest()
        for i, (text, label) in enumerate(zip(frame.Document, frame.Topic_group, strict=True))
    ], index=frame.index)


def main() -> None:
    frame = pd.read_csv(DATA)
    frame["record_id"] = record_ids(frame)
    split = json.loads(SPLIT.read_text(encoding="utf-8"))
    sample = pd.read_csv(SAMPLE, keep_default_na=False)

    required = ["record_id", "partition", "Topic_group", "Document", "Document_pt", "sha256_en"]
    checks: dict[str, object] = {}
    checks["columns_exact"] = sample.columns.tolist() == required
    checks["n_total"] = len(sample)
    counts = sample.groupby(["partition", "Topic_group"]).size().sort_index().to_dict()
    checks["counts_partition_class"] = {f"{p} | {c}": int(n) for (p, c), n in counts.items()}
    checks["partitions_exact"] = set(sample.partition) == {"validation", "test"}
    checks["classes_exact"] = set(sample.Topic_group) == set(CLASSES)
    checks["all_cells_nonempty"] = bool((sample[required].astype(str).apply(lambda c: c.str.strip() != "")).all().all())
    checks["record_id_unique"] = bool(sample.record_id.is_unique)
    checks["sha256_en_all_match"] = bool((sample.sha256_en == sample.Document.map(
        lambda x: hashlib.sha256(x.encode("utf-8")).hexdigest())).all())

    source = frame.set_index("record_id")
    checks["all_ids_in_source"] = bool(sample.record_id.isin(source.index).all())
    aligned = source.loc[sample.record_id]
    checks["source_text_all_match"] = bool((aligned.Document.to_numpy() == sample.Document.to_numpy()).all())
    checks["source_label_all_match"] = bool((aligned.Topic_group.to_numpy() == sample.Topic_group.to_numpy()).all())
    for partition in ("validation", "test"):
        ids = set(split[partition])
        part = sample[sample.partition == partition]
        checks[f"{partition}_ids_all_in_frozen_split"] = bool(part.record_id.isin(ids).all())

    expected_parts = []
    for partition in ("validation", "test"):
        subset = frame[frame.record_id.isin(set(split[partition]))]
        for label in sorted(subset.Topic_group.unique()):
            expected_parts.append(subset[subset.Topic_group == label].sample(n=100, random_state=SEED)
                                  .assign(partition=partition))
    expected = pd.concat(expected_parts, ignore_index=True)
    checks["sample_ids_match_declared_sampling_exactly"] = set(sample.record_id) == set(expected.record_id)
    checks["partition_assignments_match_declared_sampling"] = (
        set(zip(sample.record_id, sample.partition, strict=True)) ==
        set(zip(expected.record_id, expected.partition, strict=True))
    )

    count_ok = all(v == 100 for v in checks["counts_partition_class"].values())
    checks["all_16_cells_have_100"] = len(checks["counts_partition_class"]) == 16 and count_ok
    boolean_failures = [k for k, v in checks.items() if isinstance(v, bool) and not v]
    output = {"status": "ok" if not boolean_failures and len(sample) == 1600 else "fail",
              "boolean_failures": boolean_failures, "checks": checks}
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if output["status"] != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
