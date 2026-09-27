from __future__ import annotations

import hashlib
import json
import math
import os
import time
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[2]
OUT = ROOT / "outputs" / "jev_evaluation"
SAMPLE = OUT / "sample_bilingual.csv"
BASELINE = OUT / "jev_results.jsonl"
DEST = OUT / "retest_structured_criteria_validation.jsonl"
ANALYSIS = OUT / "retest_structured_criteria_validation_analysis.json"
API_URL = "https://ai-gateway.vercel.sh/v1/evaluate"
MODEL = "typesafe-ai/jev"  # mantido para isolar o efeito de instrucoes/criterios
SEED = 20260924
PER_CLASS = 10
MAX_HTTP_REQUESTS = 160
MIN_INTERVAL_S = 2.0
NO_SUCCESS_ABORT_S = 180.0
CLASSES = ["Access", "Administrative rights", "HR Support", "Hardware",
           "Internal Project", "Miscellaneous", "Purchase", "Storage"]

INSTRUCTIONS = (
    "Classify this preprocessed internal support ticket into exactly one dataset label. "
    "The text may lack punctuation, function words and names. Match the operational taxonomy below, "
    "including its dataset-specific boundaries; do not classify only by the most generic word such as "
    "access, project or device. Choose Miscellaneous only for its listed support families or when no "
    "other label has positive evidence."
)

CRITERIA = {
    "Access": {
        "what": "Identity or entry to an account, application, repository, VPN, license, badge or system: account creation/unlock, login/password, application role, Git/Confluence access.",
        "not_for": "File, folder, document, shared-drive or mailbox access belongs to Storage. New starter/leaver/intern workflow belongs to HR Support. Windows upgrade/update and workstation software configuration belong to Administrative rights.",
        "examples": ["account locked please unlock", "grant repository access", "create application account", "lost access badge"]
    },
    "Administrative rights": {
        "what": "Endpoint or workstation administration: Windows upgrade/update failures, software or profile installation, administrator permissions, and Outlook/client configuration problems.",
        "not_for": "Ordinary account login or application access is Access; buying a license is Purchase; physical device failure is Hardware.",
        "examples": ["upgrade users to windows", "windows update failure", "install profile on machine", "outlook stuck in outbox"]
    },
    "HR Support": {
        "what": "Employee lifecycle and HR operations: new starters, leavers, interns, recruiter/HR roles, timecards, payroll, benefits, leave and onboarding/offboarding.",
        "not_for": "A generic account request without employee-lifecycle context is Access.",
        "examples": ["new starter form", "create accounts for interns", "cannot submit timecard", "leaver completion"]
    },
    "Hardware": {
        "what": "Physical equipment and workplace infrastructure: laptops, monitors, phones, printers, racks, cables, meeting/conference rooms, peripherals and physical malfunction or relocation.",
        "not_for": "Buying equipment is Purchase; Windows/software administration is Administrative rights; storage capacity is Storage.",
        "examples": ["laptop will not turn on", "replace laptop backpack", "meeting room equipment", "network cables received"]
    },
    "Internal Project": {
        "what": "Dataset-specific internal project administration: project/PAS codes, project setup, pipeline or opportunity configuration, project resources, delivery setup and coordination.",
        "not_for": "An individual support incident merely mentioning a project is not enough; repository access is Access and project folders/files are Storage.",
        "examples": ["create new project code", "PAS project setup", "configure pipeline opportunity", "capacity management internal project"]
    },
    "Miscellaneous": {
        "what": "Support families outside the seven labels, including mailing/distribution-list changes, AD group-membership cleanup, monitoring/polling/alarms, ownership changes, or truly uninformative text.",
        "not_for": "Do not use merely because the wording is damaged. Prefer another label whenever its dataset-specific examples match.",
        "examples": ["add to mailing list", "remove users from AD groups", "poll status down packet loss", "change administrator ownership"]
    },
    "Purchase": {
        "what": "Procurement lifecycle: purchase orders, buying, ordering, approving, quoting, replenishment, receiving or allocating purchased equipment, software, licenses or services.",
        "not_for": "A device fault is Hardware; installing already-owned software is Administrative rights.",
        "examples": ["log new purchase PO", "ordered items received", "request quote", "log replenishment"]
    },
    "Storage": {
        "what": "Files and content storage, including file/folder/document/shared-drive/SharePoint/mailbox access or permissions, mailbox quota, disk capacity, archiving, retention, backup and recovery.",
        "not_for": "Account/application/repository/VPN/badge access is Access. Buying more capacity is Purchase only when procurement is explicitly central.",
        "examples": ["grant access to shared folder", "wants to access documents", "increase mailbox size", "set up archive"]
    },
}


def load_key() -> str:
    key = os.environ.get("AI_GATEWAY_API_KEY", "").strip()
    if key:
        return key
    for line in (PROJECT / ".env").read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("AI_GATEWAY_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("AI_GATEWAY_API_KEY ausente.")


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def append_jsonl(path: Path, row: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush(); os.fsync(f.fileno())


def one_request(text: str, key: str) -> dict:
    payload = {"model": MODEL, "state": text,
               "questions": {"topic": {"type": "choice", "instructions": INSTRUCTIONS,
                                          "criteria": CRITERIA}}}
    req = Request(API_URL, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"), method="POST",
                  headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    start = time.perf_counter()
    with urlopen(req, timeout=90) as response:
        body = json.loads(response.read().decode("utf-8"))
    answer = body["answers"]["topic"]
    probs = {c: float(answer["probabilities"][c]) for c in CLASSES}
    if answer["choice"] not in CLASSES or set(answer["probabilities"]) != set(CLASSES):
        raise ValueError("Classes inesperadas na resposta.")
    if not math.isclose(sum(probs.values()), 1.0, abs_tol=1e-5):
        raise ValueError("Probabilidades nao somam 1.")
    usage = body.get("usage", {})
    return {"prediction": answer["choice"], "confidence": float(answer["confidence"]),
            "probabilities": probs, "input_tokens": int(usage.get("inputTokens", 0)),
            "output_tokens": int(usage.get("outputTokens", 0)),
            "latency_s": time.perf_counter() - start}


def score(rows: list[dict]) -> dict:
    y = [r["true_label"] for r in rows]; p = [r["prediction"] for r in rows]
    cm = confusion_matrix(y, p, labels=CLASSES); total = int(cm.sum()); pcs = []
    for i, c in enumerate(CLASSES):
        vp = int(cm[i, i]); fn = int(cm[i].sum() - vp); fp = int(cm[:, i].sum() - vp)
        vn = total - vp - fn - fp; precision = vp / (vp + fp) if vp + fp else 0.0
        recall = vp / (vp + fn) if vp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        pcs.append({"class": c, "n": vp + fn, "VP": vp, "FP": fp, "FN": fn, "VN": vn,
                    "precision": precision, "recall": recall, "f1": f1,
                    "exploratory_because_n_below_30": vp + fn < 30})
    return {"n": total, "confusion_matrix": cm.tolist(), "row_sums": cm.sum(axis=1).astype(int).tolist(),
            "accuracy": float(np.trace(cm) / total), "macro_f1": float(np.mean([x["f1"] for x in pcs])),
            "per_class": pcs}


def main() -> None:
    sample = pd.read_csv(SAMPLE)
    validation = sample[sample.partition == "validation"]
    selected = pd.concat([validation[validation.Topic_group == c].sample(PER_CLASS, random_state=SEED + i)
                          for i, c in enumerate(CLASSES)]).sort_values("record_id")
    selected_ids = set(selected.record_id)
    baseline_all = read_jsonl(BASELINE)
    baseline = [r for r in baseline_all if r["partition"] == "validation" and r["language"] == "en"
                and r["record_id"] in selected_ids]
    if len(baseline) != len(selected) or len(selected) != PER_CLASS * len(CLASSES):
        raise RuntimeError("Selecao pareada da validacao incompleta.")

    existing = read_jsonl(DEST) if DEST.exists() else []
    if len({r["record_id"] for r in existing}) != len(existing):
        raise RuntimeError("Checkpoint novo contem IDs duplicados.")
    done = {r["record_id"] for r in existing}
    pending = [r for r in selected.itertuples(index=False) if r.record_id not in done]
    key = load_key(); request_count = 0; last_success = time.monotonic()
    print(f"reteste: {len(existing)} concluidas, {len(pending)} pendentes", flush=True)
    for item in pending:
        while True:
            if request_count >= MAX_HTTP_REQUESTS:
                print("limite de requisicoes atingido; checkpoint preservado", flush=True); return
            since_success = time.monotonic() - last_success
            if since_success > NO_SUCCESS_ABORT_S:
                print("API sem resposta bem-sucedida por mais de 3 minutos; parando", flush=True); return
            try:
                result = one_request(str(item.Document), key); request_count += 1
                row = {"record_id": item.record_id, "partition": "validation", "language": "en",
                       "true_label": item.Topic_group, "configuration": "structured_criteria_v1",
                       "model": MODEL} | result
                append_jsonl(DEST, row); existing.append(row); last_success = time.monotonic()
                if len(existing) % 10 == 0:
                    print(f"persistidas: {len(existing)}/{len(selected)}; requisicoes HTTP nesta execucao: {request_count}", flush=True)
                time.sleep(MIN_INTERVAL_S)
                break
            except Exception as exc:
                request_count += 1
                print(f"falha {type(exc).__name__}; requisicoes HTTP={request_count}", flush=True)
                time.sleep(MIN_INTERVAL_S)

    baseline_by_id = {r["record_id"]: r for r in baseline}
    new_ordered = sorted(existing, key=lambda r: r["record_id"])
    old_ordered = [baseline_by_id[r["record_id"]] for r in new_ordered]
    old_correct = np.array([r["prediction"] == r["true_label"] for r in old_ordered])
    new_correct = np.array([r["prediction"] == r["true_label"] for r in new_ordered])
    analysis = {"method": {"partition": "validation only", "paired": True, "language": "en",
                            "selection": "10 random records per class from the actual validation sample",
                            "seed": SEED, "new_http_requests_this_run": request_count,
                            "workers": 1, "minimum_interval_seconds": MIN_INTERVAL_S,
                            "model_held_constant": MODEL,
                            "limitation": "Per-class n=10 is exploratory; raw pre-preprocessing text was unavailable."},
                "baseline_original": score(old_ordered), "structured_criteria": score(new_ordered),
                "paired_correctness": {"n": len(new_ordered),
                    "both_correct": int(sum(old_correct & new_correct)),
                    "baseline_only_correct": int(sum(old_correct & ~new_correct)),
                    "structured_only_correct": int(sum(~old_correct & new_correct)),
                    "both_wrong": int(sum(~old_correct & ~new_correct))},
                "criteria_sha256": hashlib.sha256(json.dumps(CRITERIA, sort_keys=True).encode()).hexdigest()}
    ANALYSIS.write_text(json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "complete", "new_rows": len(existing),
                      "baseline_macro_f1": analysis["baseline_original"]["macro_f1"],
                      "structured_macro_f1": analysis["structured_criteria"]["macro_f1"],
                      "paired": analysis["paired_correctness"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
