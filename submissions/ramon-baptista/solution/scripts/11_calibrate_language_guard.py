from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ticket_classifier.language import language_evidence, vocabulary_coverage

ENGLISH_MARKERS = sorted({"i", "my", "the", "and", "is", "are", "was", "were", "to", "from", "for", "with", "this", "that", "cannot", "cant", "forgot", "please", "need", "shows", "error", "not"})
PORTUGUESE_MARKERS = sorted({"o", "os", "as", "meu", "minha", "nao", "e", "do", "da", "dos", "das", "para", "com", "esta", "estao", "foi", "quebrou", "preciso", "senha", "tela", "teclado", "funciona", "pedido"})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    sample = pd.read_csv(ROOT / "outputs" / "jev_evaluation" / "sample_bilingual.csv")
    validation = sample.loc[sample["partition"].eq("validation")].copy()
    if validation.empty or set(validation["partition"]) != {"validation"}:
        raise AssertionError("A calibracao deve usar somente a particao validation.")
    short = pd.read_csv(ROOT / "data" / "language_guard_short_validation.csv")
    if set(short["partition"]) != {"validation_short_exploratory"}:
        raise AssertionError("O conjunto curto deve estar identificado como validacao exploratoria.")
    model = joblib.load(ROOT / "artifacts" / "model-v1.0.0.joblib")
    rows = []
    for language, column in (("en", "Document"), ("pt", "Document_pt")):
        for record_id, text in zip(validation["record_id"], validation[column], strict=True):
            coverage, recognized, total = vocabulary_coverage(str(text), model)
            rows.append({"record_id": record_id, "source": "bilingual_validation", "language": language,
                         "text": str(text), "coverage": coverage, "recognized_tokens": recognized,
                         "total_tokens": total})
    for row in short.itertuples(index=False):
        coverage, recognized, total = vocabulary_coverage(row.text, model)
        rows.append({"record_id": row.record_id, "source": "short_validation_exploratory",
                     "language": row.language, "text": row.text, "coverage": coverage,
                     "recognized_tokens": recognized, "total_tokens": total})
    diagnostics = pd.DataFrame(rows)
    old_diverted = ((diagnostics.total_tokens >= 10) & (diagnostics.coverage < 0.80))
    markers = {"english_markers": ENGLISH_MARKERS, "portuguese_markers": PORTUGUESE_MARKERS}
    hits = diagnostics.text.map(lambda text: language_evidence(text, markers))
    diagnostics[["english_marker_hits", "portuguese_marker_hits"]] = pd.DataFrame(hits.tolist(), index=diagnostics.index)
    candidates = []
    for minimum_tokens in (4, 6, 8, 10):
        for marker_hits in (1, 2, 3):
            for threshold in (step / 20 for step in range(21)):
                pt_signal = ((diagnostics.portuguese_marker_hits >= marker_hits) & (diagnostics.portuguese_marker_hits > diagnostics.english_marker_hits))
                en_signal = ((diagnostics.english_marker_hits >= marker_hits) & (diagnostics.english_marker_hits > diagnostics.portuguese_marker_hits))
                fallback = ((diagnostics.total_tokens >= minimum_tokens) & (diagnostics.coverage < threshold))
                diverted = pt_signal | (~en_signal & fallback)
                en_false = int((diverted & diagnostics.language.eq("en")).sum())
                pt_missed = int((~diverted & diagnostics.language.eq("pt")).sum())
                candidates.append((en_false, pt_missed, -marker_hits, minimum_tokens, threshold, diverted))
    en_false, pt_missed, neg_hits, minimum_tokens, threshold, new_diverted = min(candidates, key=lambda x: x[:5])
    marker_hits = -neg_hits

    def errors(mask: pd.Series, diverted: pd.Series) -> dict:
        en = mask & diagnostics.language.eq("en")
        pt = mask & diagnostics.language.eq("pt")
        return {"n_en": int(en.sum()), "n_pt": int(pt.sum()),
                "en_false_diverted_n": int((en & diverted).sum()),
                "pt_missed_n": int((pt & ~diverted).sum())}

    all_mask = pd.Series(True, index=diagnostics.index)
    short_mask = diagnostics.source.eq("short_validation_exploratory")
    before_after = {
        "method": "contagem exata por idioma: EN desviado e falso positivo; PT nao desviado e falso negativo",
        "foundation": "mede diretamente os dois sentidos de falha da protecao",
        "assumptions": ["rotulos da validacao estao corretos", "conjunto curto e exploratorio porque n<30 por idioma"],
        "all_validation": {"before": errors(all_mask, old_diverted), "after": errors(all_mask, new_diverted)},
        "short_validation_exploratory": {"before": errors(short_mask, old_diverted), "after": errors(short_mask, new_diverted)},
    }
    artifact = {
        "version": "1.1.0",
        "method": "Marcadores lexicais com desempate por cobertura unigram; evidencia explicita prevalece sobre cobertura.",
        "selection": "Grade predefinida na validacao: minimiza falsos desvios EN e depois PT nao detectados; teste congelado excluido.",
        "foundation": "Marcadores evitam que poucas palavras fora do vocabulario dominem textos curtos; cobertura trata casos sem evidencia.",
        "assumptions": ["Document e ingles e Document_pt e traducao pareada.", "A heuristica nao e detector universal.", "Amostra curta n<30 por idioma e exploratoria."],
        "partition": "validation + validation_short_exploratory",
        "minimum_tokens": minimum_tokens, "minimum_marker_hits": marker_hits, "threshold": threshold,
        "english_markers": ENGLISH_MARKERS, "portuguese_markers": PORTUGUESE_MARKERS,
        "n_en": int(diagnostics.language.eq("en").sum()), "n_pt": int(diagnostics.language.eq("pt").sum()),
        "errors_before_after": before_after,
    }
    guard_path = ROOT / "artifacts" / "language_guard.json"
    guard_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest_path = ROOT / "artifacts" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"]["language_guard"] = {"path": "language_guard.json", "sha256": sha256(guard_path)}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    diagnostics.drop(columns="text").assign(old_diverted=old_diverted, new_diverted=new_diverted).to_csv(ROOT / "outputs" / "language_guard_validation.csv", index=False, encoding="utf-8", lineterminator="\n")
    (ROOT / "outputs" / "language_guard_before_after.json").write_text(json.dumps(before_after, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(artifact, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
