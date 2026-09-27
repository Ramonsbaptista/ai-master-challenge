from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, wilcoxon
from sklearn.metrics import confusion_matrix, f1_score


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "artifacts" / "model-v1.0.0.joblib"
MANIFEST_PATH = ROOT / "artifacts" / "manifest.json"
SAMPLE_PATH = ROOT / "outputs" / "jev_evaluation" / "sample_bilingual.csv"
OUT = ROOT / "outputs" / "language_root_cause"
SEED = 20260924
BOOTSTRAPS = 5000
NEAR_EMPTY_NNZ_MAX = 2
NEAR_EMPTY_COVERAGE_MAX = 0.05


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def py(value):
    if isinstance(value, dict):
        return {str(k): py(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [py(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        return None if not np.isfinite(value) else float(value)
    return value


def safe_div(a: float, b: float) -> float:
    return float(a / b) if b else float("nan")


def aggregate_metrics(y_true, y_pred, classes):
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    rows = []
    total = int(cm.sum())
    for i, label in enumerate(classes):
        vp = int(cm[i, i])
        fn = int(cm[i, :].sum() - vp)
        fp = int(cm[:, i].sum() - vp)
        vn = total - vp - fn - fp
        precision = safe_div(vp, vp + fp)
        recall = safe_div(vp, vp + fn)
        specificity = safe_div(vn, vn + fp)
        f1 = safe_div(2 * precision * recall, precision + recall)
        rows.append({"class": label, "n": int(cm[i, :].sum()), "VP": vp, "FP": fp,
                     "FN": fn, "VN": vn, "precision": precision, "recall": recall,
                     "specificity": specificity, "f1": f1})
    if not all(sum(cm[i, :]) == rows[i]["n"] for i in range(len(classes))):
        raise AssertionError("Falha: soma de linha da matriz != n da classe.")
    if total != len(y_true):
        raise AssertionError("Falha: soma total da matriz != n do conjunto.")
    return cm, rows, {
        "n": total,
        "accuracy": float(np.trace(cm) / total),
        "macro_f1": float(f1_score(y_true, y_pred, labels=classes, average="macro")),
        "weighted_f1": float(f1_score(y_true, y_pred, labels=classes, average="weighted")),
    }


def paired_bootstrap_macro_f1(y, pred_a, pred_b, classes):
    rng = np.random.default_rng(SEED)
    y = np.asarray(y)
    a = np.asarray(pred_a)
    b = np.asarray(pred_b)
    diffs = np.empty(BOOTSTRAPS)
    for i in range(BOOTSTRAPS):
        idx = rng.integers(0, len(y), len(y))
        diffs[i] = (f1_score(y[idx], a[idx], labels=classes, average="macro") -
                    f1_score(y[idx], b[idx], labels=classes, average="macro"))
    point = (f1_score(y, a, labels=classes, average="macro") -
             f1_score(y, b, labels=classes, average="macro"))
    return {"n": len(y), "method": f"bootstrap pareado percentil, {BOOTSTRAPS} reamostragens, seed={SEED}",
            "difference_a_minus_b": float(point),
            "ci95": [float(x) for x in np.quantile(diffs, [0.025, 0.975])]}


def coverage_summary(g: pd.DataFrame, language: str):
    token_total = int(g.token_count.sum())
    matched_total = int(g.matched_token_count.sum())
    feature_total = int(g.feature_count.sum())
    matched_feature_total = int(g.matched_feature_count.sum())
    return {
        "language": language,
        "n": len(g),
        "token_coverage_micro": safe_div(matched_total, token_total),
        "token_coverage_micro_numerator": matched_total,
        "token_coverage_micro_denominator": token_total,
        "token_coverage_per_text_median": float(g.token_coverage.median()),
        "token_coverage_per_text_q25": float(g.token_coverage.quantile(.25)),
        "token_coverage_per_text_q75": float(g.token_coverage.quantile(.75)),
        "feature_coverage_micro": safe_div(matched_feature_total, feature_total),
        "feature_coverage_micro_numerator": matched_feature_total,
        "feature_coverage_micro_denominator": feature_total,
        "nnz_median": float(g.nnz.median()),
        "nnz_q25": float(g.nnz.quantile(.25)),
        "nnz_q75": float(g.nnz.quantile(.75)),
        "empty_n": int((g.nnz == 0).sum()),
        "empty_fraction": float((g.nnz == 0).mean()),
        "near_empty_nnz_le_2_n": int((g.nnz <= NEAR_EMPTY_NNZ_MAX).sum()),
        "near_empty_nnz_le_2_fraction": float((g.nnz <= NEAR_EMPTY_NNZ_MAX).mean()),
        "near_empty_coverage_le_5pct_n": int((g.feature_coverage <= NEAR_EMPTY_COVERAGE_MAX).sum()),
        "near_empty_coverage_le_5pct_fraction": float((g.feature_coverage <= NEAR_EMPTY_COVERAGE_MAX).mean()),
        "method": "micro = ocorrências reconhecidas / ocorrências analisadas; estatísticas por texto usam mediana e quartis por assimetria; vazio = nnz 0; quase vazio reportado separadamente como nnz<=2 e cobertura de features<=5% (cortes diagnósticos predefinidos, não otimizados).",
    }


def fmt_pct(x):
    return "NA" if x is None or not math.isfinite(x) else f"{100*x:.1f}%"


def fmt_num(x, digits=3):
    return "NA" if x is None or not math.isfinite(x) else f"{x:.{digits}f}"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    model = joblib.load(MODEL_PATH)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    sample = pd.read_csv(SAMPLE_PATH)
    test = sample.loc[sample["partition"].eq("test")].copy().reset_index(drop=True)
    if len(test) != 800:
        raise AssertionError(f"Teste esperado n=800, encontrado n={len(test)}.")
    if test["record_id"].duplicated().any():
        raise AssertionError("record_id duplicado no teste.")
    classes = list(model.classes_)
    expected = sorted(test["Topic_group"].unique().tolist())
    if sorted(classes) != expected:
        raise AssertionError("Classes do modelo e do teste não coincidem.")
    class_counts = test["Topic_group"].value_counts().reindex(classes)
    if not (class_counts == 100).all():
        raise AssertionError(f"Teste não tem 100 casos por classe: {class_counts.to_dict()}")

    vectorizer = model.named_steps["tfidf"]
    classifier = model.named_steps["classifier"]
    vocabulary = vectorizer.vocabulary_
    unigram_vocab = {term for term in vocabulary if " " not in term}
    analyzer = vectorizer.build_analyzer()
    preprocessor = vectorizer.build_preprocessor()
    tokenizer = vectorizer.build_tokenizer()
    feature_names = np.asarray(vectorizer.get_feature_names_out())

    predictions = {}
    matrices = {}
    per_class_all = []
    aggregates = {}
    diagnostic_rows = []
    token_stats = {"en": Counter(), "pt": Counter()}
    token_docfreq = {"en": Counter(), "pt": Counter()}
    original_token_cache = {}

    for lang, col in (("en", "Document"), ("pt", "Document_pt")):
        texts = test[col].fillna("").astype(str).tolist()
        x = vectorizer.transform(texts)
        proba = model.predict_proba(texts)
        pred = classes[np.argmax(proba, axis=1)] if isinstance(classes, np.ndarray) else np.asarray(classes)[np.argmax(proba, axis=1)]
        score = proba.max(axis=1)
        predictions[lang] = {"pred": np.asarray(pred), "score": score, "x": x, "proba": proba}
        cm, pc, agg = aggregate_metrics(test["Topic_group"].to_numpy(), pred, classes)
        matrices[lang] = cm
        aggregates[lang] = agg
        per_class_all.extend([{"language": lang, **row} for row in pc])
        for i, text in enumerate(texts):
            tokens = tokenizer(preprocessor(text))
            features = analyzer(text)
            matched_tokens = [t for t in tokens if t in unigram_vocab]
            matched_features = [f for f in features if f in vocabulary]
            token_stats[lang].update(matched_tokens)
            token_docfreq[lang].update(set(matched_tokens))
            original_token_cache[(lang, i)] = tokens
            diagnostic_rows.append({
                "record_id": test.at[i, "record_id"], "language": lang,
                "true_label": test.at[i, "Topic_group"], "prediction": pred[i],
                "correct": bool(pred[i] == test.at[i, "Topic_group"]), "score": float(score[i]),
                "token_count": len(tokens), "matched_token_count": len(matched_tokens),
                "token_coverage": safe_div(len(matched_tokens), len(tokens)) if tokens else 0.0,
                "feature_count": len(features), "matched_feature_count": len(matched_features),
                "feature_coverage": safe_div(len(matched_features), len(features)) if features else 0.0,
                "nnz": int(x[i].nnz),
            })

    diag = pd.DataFrame(diagnostic_rows)
    diag.to_csv(OUT / "text_level_diagnostics.csv", index=False, lineterminator="\n")
    coverage = [coverage_summary(diag[diag.language.eq(lang)], lang) for lang in ("en", "pt")]
    pd.DataFrame(coverage).to_csv(OUT / "coverage_summary.csv", index=False, lineterminator="\n")

    # Termos idênticos dentro de cada par EN/PT: proxy observável para siglas, marcas,
    # nomes técnicos, números e empréstimos linguísticos. Não rotulamos nomes de produto
    # por dicionário subjetivo; entregamos os termos e sua contribuição para auditoria.
    shared_sets = []
    shared_only_texts = []
    without_shared_texts = []
    category_counts = Counter()
    pt_survivor_rows = []
    for i in range(len(test)):
        en_tokens = original_token_cache[("en", i)]
        pt_tokens = original_token_cache[("pt", i)]
        shared = set(en_tokens).intersection(pt_tokens).intersection(unigram_vocab)
        shared_sets.append(shared)
        shared_only = [t for t in pt_tokens if t in shared]
        without_shared = [t for t in pt_tokens if t not in shared]
        shared_only_texts.append(" ".join(shared_only))
        without_shared_texts.append(" ".join(without_shared))
        for t in pt_tokens:
            if t not in unigram_vocab:
                continue
            if t in shared:
                cat = "idêntico_no_par_EN_PT"
            elif any(ch.isdigit() for ch in t):
                cat = "alfanumérico"
            elif len(t) <= 4:
                cat = "curto_sigla_ou_ambíguo"
            else:
                cat = "outro_termo_do_vocabulario_EN"
            category_counts[cat] += 1

    pred_shared = model.predict(shared_only_texts)
    pred_without = model.predict(without_shared_texts)
    _, pc_shared, agg_shared = aggregate_metrics(test.Topic_group.to_numpy(), pred_shared, classes)
    _, pc_without, agg_without = aggregate_metrics(test.Topic_group.to_numpy(), pred_without, classes)
    ablations = {
        "full_pt": aggregates["pt"],
        "shared_identical_only": agg_shared,
        "without_shared_identical": agg_without,
        "method": "contrafactuais no mesmo n=800: (a) somente unigramas PT que também aparecem no texto EN pareado e no vocabulário; (b) remoção desses unigramas do PT. Preserva rótulos e não ajusta o modelo; mudanças também afetam bigramas, portanto são evidência mecanística, não efeito causal isolado de cada token.",
    }

    # Contribuição linear dos termos para a classe prevista em PT.
    xpt = predictions["pt"]["x"]
    pred_pt = predictions["pt"]["pred"]
    correct_pt = pred_pt == test.Topic_group.to_numpy()
    class_to_idx = {c: i for i, c in enumerate(classes)}
    total_contrib_all = defaultdict(float)
    total_contrib_correct = defaultdict(float)
    occurrence_docs = Counter()
    correct_docs = Counter()
    for i in range(len(test)):
        row = xpt.getrow(i)
        coef = classifier.coef_[class_to_idx[pred_pt[i]], row.indices]
        contrib = row.data * coef
        for idx, value in zip(row.indices, contrib):
            if value <= 0:
                continue
            term = feature_names[idx]
            total_contrib_all[term] += float(value)
            occurrence_docs[term] += 1
            if correct_pt[i]:
                total_contrib_correct[term] += float(value)
                correct_docs[term] += 1
    all_terms = set(total_contrib_all) | set(token_stats["pt"])
    for term in all_terms:
        pt_survivor_rows.append({
            "term": term,
            "feature_kind": "bigram" if " " in term else "unigram",
            "pt_token_occurrences": int(token_stats["pt"].get(term, 0)),
            "pt_document_frequency": int(token_docfreq["pt"].get(term, 0)),
            "positive_contribution_all": float(total_contrib_all.get(term, 0.0)),
            "positive_contribution_correct_predictions": float(total_contrib_correct.get(term, 0.0)),
            "documents_positive_contribution": int(occurrence_docs.get(term, 0)),
            "correct_documents_positive_contribution": int(correct_docs.get(term, 0)),
        })
    survivors = pd.DataFrame(pt_survivor_rows).sort_values(
        ["positive_contribution_correct_predictions", "pt_document_frequency"], ascending=False)
    survivors.to_csv(OUT / "surviving_terms_pt.csv", index=False, lineterminator="\n")

    # Classe padrão: decisão do classificador quando x é o vetor zero.
    zero_logits = classifier.intercept_.copy()
    zero_proba = np.exp(zero_logits - zero_logits.max())
    zero_proba = zero_proba / zero_proba.sum()
    zero_idx = int(np.argmax(zero_proba))
    default_class = classes[zero_idx]
    default_score = float(zero_proba[zero_idx])
    prediction_distribution = []
    for lang in ("en", "pt"):
        g = diag[diag.language.eq(lang)]
        for label in classes:
            count = int((g.prediction == label).sum())
            prediction_distribution.append({"language": lang, "class": label, "n": len(g),
                                            "predicted_n": count, "predicted_fraction": count / len(g)})
    pred_dist_df = pd.DataFrame(prediction_distribution)
    pred_dist_df.to_csv(OUT / "prediction_distribution.csv", index=False, lineterminator="\n")

    cm_rows = []
    for lang, cm in matrices.items():
        for i, true_label in enumerate(classes):
            for j, predicted_label in enumerate(classes):
                cm_rows.append({"language": lang, "true_label": true_label,
                                "predicted_label": predicted_label, "n": int(cm[i, j])})
    pd.DataFrame(cm_rows).to_csv(OUT / "confusion_matrices_long.csv", index=False, lineterminator="\n")
    pd.DataFrame(per_class_all).to_csv(OUT / "per_class_metrics_root_cause.csv", index=False, lineterminator="\n")

    # Associação cobertura-acerto, sem impor linearidade.
    pt_diag = diag[diag.language.eq("pt")].copy()
    q_edges = np.unique(pt_diag.token_coverage.quantile([0, .25, .5, .75, 1]).to_numpy())
    if len(q_edges) >= 3:
        pt_diag["coverage_bin"] = pd.cut(pt_diag.token_coverage, bins=q_edges,
                                          include_lowest=True, duplicates="drop")
    else:
        pt_diag["coverage_bin"] = "sem_variação_suficiente"
    coverage_accuracy_bins = []
    for name, g in pt_diag.groupby("coverage_bin", observed=True):
        coverage_accuracy_bins.append({"bin": str(name), "n": len(g),
                                       "coverage_median": float(g.token_coverage.median()),
                                       "accuracy": float(g.correct.mean())})
    pd.DataFrame(coverage_accuracy_bins).to_csv(OUT / "coverage_accuracy_bins_pt.csv", index=False, lineterminator="\n")
    cov_correct = pt_diag.loc[pt_diag.correct, "token_coverage"].to_numpy()
    cov_wrong = pt_diag.loc[~pt_diag.correct, "token_coverage"].to_numpy()
    mw = mannwhitneyu(cov_correct, cov_wrong, alternative="two-sided")
    coverage_association = {
        "n": len(pt_diag), "correct_n": len(cov_correct), "wrong_n": len(cov_wrong),
        "correct_median_coverage": float(np.median(cov_correct)),
        "wrong_median_coverage": float(np.median(cov_wrong)),
        "mann_whitney_u": float(mw.statistic), "p_value_two_sided": float(mw.pvalue),
        "method": "Mann-Whitney bicaudal, escolhido em vez de teste t porque cobertura é limitada a [0,1], assimétrica e com empates; pressupõe observações independentes entre tickets e interpreta diferença de distribuição, não causalidade.",
        "bins": coverage_accuracy_bins,
    }

    # Score e roteamento: aplica sem reajuste os cortes de produção escolhidos na validação EN.
    low = float(manifest["routing_thresholds"]["low"])
    high = float(manifest["routing_thresholds"]["high"])
    routing_rows = []
    score_summary = {}
    for lang in ("en", "pt"):
        scores = predictions[lang]["score"]
        correct = predictions[lang]["pred"] == test.Topic_group.to_numpy()
        bands = np.where(scores < low, "baixa", np.where(scores < high, "media", "alta"))
        score_summary[lang] = {
            "n": len(scores), "mean": float(np.mean(scores)), "median": float(np.median(scores)),
            "q25": float(np.quantile(scores, .25)), "q75": float(np.quantile(scores, .75)),
            "wrong_n": int((~correct).sum()),
            "wrong_score_mean": float(np.mean(scores[~correct])),
            "wrong_score_median": float(np.median(scores[~correct])),
            "wrong_high_band_n": int(((~correct) & (bands == "alta")).sum()),
            "wrong_high_band_fraction_of_errors": float(((~correct) & (bands == "alta")).sum() / (~correct).sum()),
        }
        for band in ("baixa", "media", "alta"):
            mask = bands == band
            routing_rows.append({"language": lang, "band": band, "n_total": len(scores),
                                 "band_n": int(mask.sum()), "coverage": float(mask.mean()),
                                 "accuracy": float(correct[mask].mean()) if mask.any() else float("nan"),
                                 "errors_n": int((mask & ~correct).sum()), "low": low, "high": high})
    pd.DataFrame(routing_rows).to_csv(OUT / "routing_metrics.csv", index=False, lineterminator="\n")
    paired_score_test = wilcoxon(predictions["en"]["score"], predictions["pt"]["score"],
                                 alternative="two-sided", zero_method="wilcox")
    score_comparison = {
        "n_pairs": len(test), "pt_minus_en_mean": float(np.mean(predictions["pt"]["score"] - predictions["en"]["score"])),
        "pt_minus_en_median": float(np.median(predictions["pt"]["score"] - predictions["en"]["score"])),
        "wilcoxon_statistic": float(paired_score_test.statistic), "p_value_two_sided": float(paired_score_test.pvalue),
        "method": "Wilcoxon pareado bicaudal, escolhido em vez de t pareado porque probabilidades máximas são limitadas, assimétricas e pareadas pelo mesmo ticket; pressupõe diferenças aproximadamente simétricas para interpretação de deslocamento.",
    }

    default_concentration = {}
    for lang in ("en", "pt"):
        g = diag[diag.language.eq(lang)]
        empty = g[g.nnz.eq(0)]
        near = g[g.nnz.le(NEAR_EMPTY_NNZ_MAX)]
        default_concentration[lang] = {
            "n": len(g), "predicted_default_n": int(g.prediction.eq(default_class).sum()),
            "predicted_default_fraction": float(g.prediction.eq(default_class).mean()),
            "empty_n": len(empty), "empty_predicted_default_n": int(empty.prediction.eq(default_class).sum()),
            "near_empty_n": len(near), "near_empty_predicted_default_n": int(near.prediction.eq(default_class).sum()),
            "near_empty_predicted_default_fraction": float(near.prediction.eq(default_class).mean()) if len(near) else float("nan"),
        }

    top_survivors = survivors.head(30).to_dict("records")
    bootstrap_drop = paired_bootstrap_macro_f1(test.Topic_group.to_numpy(), predictions["en"]["pred"],
                                                predictions["pt"]["pred"], classes)
    report_obj = {
        "provenance": {"model": str(MODEL_PATH.relative_to(ROOT)), "model_sha256": sha256_file(MODEL_PATH),
                       "sample": str(SAMPLE_PATH.relative_to(ROOT)), "sample_sha256": sha256_file(SAMPLE_PATH),
                       "manifest": str(MANIFEST_PATH.relative_to(ROOT)), "script_seed": SEED},
        "sample": {"n": len(test), "classes": classes, "n_per_class": class_counts.to_dict(),
                   "method": "partição test da amostra bilíngue congelada; 100 tickets por classe; textos EN e PT pareados por record_id."},
        "model": {"vocabulary_features_n": len(vocabulary), "unigram_vocabulary_n": len(unigram_vocab),
                  "ngram_range": list(vectorizer.ngram_range), "default_zero_vector_class": default_class,
                  "default_zero_vector_score": default_score,
                  "method": "classe padrão calculada aplicando softmax aos interceptos da regressão logística com vetor TF-IDF exatamente zero."},
        "performance": {"english": aggregates["en"], "portuguese": aggregates["pt"],
                        "macro_f1_drop_en_minus_pt": bootstrap_drop},
        "coverage": coverage,
        "coverage_accuracy_association_pt": coverage_association,
        "survivors": {"occurrence_categories": dict(category_counts), "top_positive_terms": top_survivors,
                      "ablations": ablations,
                      "method": "sobrevivente = token/feature produzido pelo analisador congelado e presente no vocabulário; termo idêntico = unigrama presente nos dois textos do par. Contribuição = TF-IDF × coeficiente da classe prevista; somam-se apenas contribuições positivas."},
        "confusion": {"class_order": classes, "english": matrices["en"], "portuguese": matrices["pt"],
                      "default_class_concentration": default_concentration,
                      "consistency": "linhas conferidas contra n da classe; total conferido contra n=800."},
        "scores": {"thresholds": {"low": low, "high": high, "source": "manifest; escolhidos apenas na validação original EN"},
                   "summary": score_summary, "paired_comparison": score_comparison, "routing": routing_rows,
                   "method": "score = máxima predict_proba, não calibrada; cortes congelados aplicados sem ajuste ao mesmo n=800."},
        "translation_language_identifiability": {
            "result": "não identificável nos dados atuais",
            "reason": "todo texto PT é simultaneamente mudança de idioma e saída de uma única tradução automática PT-PT; não há português humano/nativo nem outro tradutor para formar contraste independente.",
            "proposed_validation_only_design": [
                "Usar somente a partição validation (n=800; teste permanece intocado) e manter pareamento por record_id.",
                "Condição A: EN original.",
                "Condição B: EN→PT-PT→EN por tradução automática; A versus B estima dano de reescrita/tradução mantendo o idioma final inglês.",
                "Condição C: PT-PT automático atual.",
                "Condição D: PT-PT revisado por humano, preservando conteúdo; C versus D estima artefato/qualidade da tradução dentro do mesmo idioma.",
                "Condição E: PT-BR revisado por humano; D versus E estima efeito de variante regional, não efeito total de idioma.",
                "A versus D mede efeito combinado de idioma mais escolhas inevitáveis de formulação humana; reportar interação e não forçar decomposição aditiva.",
                "Comparar por bootstrap pareado de macro-F1 e McNemar para acerto; declarar n=800 e IC95%; não escolher solução pelo teste congelado."
            ],
        },
    }
    (OUT / "analysis.json").write_text(json.dumps(py(report_obj), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    cov_en, cov_pt = coverage
    pt_dist = pred_dist_df[pred_dist_df.language.eq("pt")].sort_values("predicted_n", ascending=False)
    top_class = pt_dist.iloc[0]
    route_pt = {r["band"]: r for r in routing_rows if r["language"] == "pt"}
    per_pt = [r for r in per_class_all if r["language"] == "pt"]
    lines = [
        "# Diagnóstico de causa raiz — queda EN→PT do TF-IDF + regressão logística",
        "",
        "## Resultado executivo",
        "",
        f"No teste congelado balanceado (n={len(test)}; método: 100 tickets por classe, textos pareados por `record_id`), o macro-F1 foi {aggregates['en']['macro_f1']:.3f} em EN e {aggregates['pt']['macro_f1']:.3f} em PT. A queda pareada foi {bootstrap_drop['difference_a_minus_b']:.3f} (IC95% {bootstrap_drop['ci95'][0]:.3f} a {bootstrap_drop['ci95'][1]:.3f}; método: bootstrap pareado percentil com {BOOTSTRAPS} reamostragens, escolhido porque macro-F1 não tem variância analítica simples; pressupõe tickets independentes e pares EN/PT corretos).",
        "",
        f"A causa raiz observada é quebra de representação: o modelo foi treinado em vocabulário inglês e só pode usar features PT que já existam nesse vocabulário. A cobertura lexical micro caiu de {fmt_pct(cov_en['token_coverage_micro'])} ({cov_en['token_coverage_micro_numerator']}/{cov_en['token_coverage_micro_denominator']} ocorrências; n={len(test)} textos) para {fmt_pct(cov_pt['token_coverage_micro'])} ({cov_pt['token_coverage_micro_numerator']}/{cov_pt['token_coverage_micro_denominator']}; n={len(test)}). A cobertura de uni+bigramas caiu de {fmt_pct(cov_en['feature_coverage_micro'])} para {fmt_pct(cov_pt['feature_coverage_micro'])} (mesmo método e n={len(test)}).",
        "",
        f"Em PT, vetores vazios: {cov_pt['empty_n']}/{len(test)} ({fmt_pct(cov_pt['empty_fraction'])}); quase vazios por nnz≤{NEAR_EMPTY_NNZ_MAX}: {cov_pt['near_empty_nnz_le_2_n']}/{len(test)} ({fmt_pct(cov_pt['near_empty_nnz_le_2_fraction'])}); quase vazios por cobertura de features≤{fmt_pct(NEAR_EMPTY_COVERAGE_MAX)}: {cov_pt['near_empty_coverage_le_5pct_n']}/{len(test)} ({fmt_pct(cov_pt['near_empty_coverage_le_5pct_fraction'])}). Os dois critérios são diagnósticos predefinidos e reportados separadamente; não foram escolhidos para maximizar o efeito.",
        "",
        "## O que sobrevive e quanto explica",
        "",
        f"O contrafactual com somente unigramas idênticos no par EN–PT e presentes no vocabulário obteve macro-F1 {agg_shared['macro_f1']:.3f} (n={len(test)}); removendo esses termos do PT, o macro-F1 foi {agg_without['macro_f1']:.3f} (n={len(test)}), contra {aggregates['pt']['macro_f1']:.3f} no PT completo (n={len(test)}). Método: ablação pareada, sem retreino; como remover tokens também desfaz bigramas, isto demonstra mecanismo, mas não identifica efeito causal isolado de cada palavra.",
        "",
        "Os termos sobreviventes com maior contribuição positiva para previsões corretas estão em `surviving_terms_pt.csv`. A contribuição é `TF-IDF × coeficiente` da classe prevista, somada apenas quando positiva; isso distingue frequência de influência real. A categoria “idêntico_no_par_EN_PT” é objetiva; “curto_sigla_ou_ambíguo” não é chamado automaticamente de sigla para evitar classificação subjetiva.",
        "",
        "## Para onde vão os erros",
        "",
        f"Com vetor exatamente zero, os interceptos escolhem **{default_class}** com score {default_score:.3f} (método: softmax dos interceptos; n conceitual=1 vetor zero). Em PT, essa classe recebeu {default_concentration['pt']['predicted_default_n']}/{len(test)} previsões ({fmt_pct(default_concentration['pt']['predicted_default_fraction'])}); entre vetores com nnz≤{NEAR_EMPTY_NNZ_MAX}, recebeu {default_concentration['pt']['near_empty_predicted_default_n']}/{default_concentration['pt']['near_empty_n']} ({fmt_pct(default_concentration['pt']['near_empty_predicted_default_fraction'])}). A classe mais prevista em PT foi {top_class['class']}: {int(top_class['predicted_n'])}/{len(test)} ({fmt_pct(top_class['predicted_fraction'])}).",
        "",
        "Métricas PT por classe (método one-vs-rest; n=100 positivos por classe e n=800 total; fórmulas mostradas):",
        "",
    ]
    for r in per_pt:
        lines.append(f"- {r['class']} (n={r['n']}): precisão = VP/(VP+FP) = {r['VP']}/({r['VP']}+{r['FP']}) = {r['precision']:.3f}; recall = VP/(VP+FN) = {r['VP']}/({r['VP']}+{r['FN']}) = {r['recall']:.3f}; especificidade = VN/(VN+FP) = {r['VN']}/({r['VN']}+{r['FP']}) = {r['specificity']:.3f}; F1 = 2×precisão×recall/(precisão+recall) = {r['f1']:.3f}. VP={r['VP']}, FP={r['FP']}, FN={r['FN']}, VN={r['VN']}.")
    lines += [
        "",
        f"Agregados PT (n={len(test)}): acurácia = soma da diagonal/n = {int(np.trace(matrices['pt']))}/{len(test)} = {aggregates['pt']['accuracy']:.3f}; macro-F1 = média simples dos oito F1 por classe = {aggregates['pt']['macro_f1']:.3f}; F1 ponderado pela quantidade real de cada classe = {aggregates['pt']['weighted_f1']:.3f}. Como há 100 casos por classe, macro e ponderado coincidem. A matriz passou nas checagens de linhas e total.",
        "",
        "## Score e roteamento",
        "",
        f"O score máximo médio mudou de {score_summary['en']['mean']:.3f} em EN (n={len(test)}) para {score_summary['pt']['mean']:.3f} em PT (n={len(test)}); diferença PT−EN média {score_comparison['pt_minus_en_mean']:.3f}, mediana {score_comparison['pt_minus_en_median']:.3f}, p={score_comparison['p_value_two_sided']:.3g} (Wilcoxon pareado bicaudal; probabilidades são limitadas e assimétricas; pressupõe pares independentes e distribuição aproximadamente simétrica das diferenças).",
        "",
        f"Aplicando sem ajuste os cortes congelados do manifesto (baixa < {low:.3f}; alta ≥ {high:.3f}), a faixa alta em PT reteve {route_pt['alta']['band_n']}/{len(test)} ({fmt_pct(route_pt['alta']['coverage'])}) com acurácia {fmt_pct(route_pt['alta']['accuracy'])} (n={route_pt['alta']['band_n']}; método: acertos/aceitos). Entre todos os {score_summary['pt']['wrong_n']} erros PT, {score_summary['pt']['wrong_high_band_n']} ({fmt_pct(score_summary['pt']['wrong_high_band_fraction_of_errors'])}) ficaram na faixa alta. Portanto, o score não é um detector confiável de idioma/OOV; erros de alta confiança são o risco principal.",
        "",
        "## Idioma versus tradução automática",
        "",
        "Os efeitos não são separáveis nesta amostra: todos os textos PT são simultaneamente outro idioma e produto de um único tradutor PT-PT. Qualquer percentual atribuído a cada causa seria não identificável.",
        "",
        "Experimento sem tocar no teste: usar somente os 800 pares de validação e produzir EN original, EN→PT→EN, PT-PT automático, PT-PT revisado por humano e PT-BR revisado por humano. Comparar macro-F1 por bootstrap pareado (5.000 reamostragens, IC95%) e acerto por McNemar. EN original versus backtranslation estima dano de reescrita mantendo inglês; PT automático versus PT humano estima artefato do tradutor dentro de PT; PT-PT versus PT-BR estima variante regional. EN versus PT humano continua sendo efeito combinado de idioma e formulação, devendo ser reportado como tal, inclusive com interação.",
        "",
        "## Correções candidatas e recomendação",
        "",
        "1. **Traduzir PT→EN antes do classificador atual.** Prós: preserva modelo leve, implantação rápida, reutiliza limiares após nova calibração. Contras: latência/custo e falhas de tradução; dependência externa ou de um modelo local. Custo na máquina: mínimo se API; alto se tradutor neural local. Medição: escolher tradutor e novos cortes apenas na validação traduzida (n=800), com macro-F1 pareado, latência p50/p95, custo por ticket, cobertura e acurácia por faixa; teste congelado uma única vez após decisão.",
        "2. **Treinar com dados traduzidos para PT.** Prós: inferência TF-IDF continua barata e transparente; adapta vocabulário PT. Contras: duplica/expande matriz esparsa, herda artefatos do tradutor e pode degradar EN. Custo: RAM moderada; o corpus duplicado teria n=66.970 exemplos antes da validação, como premissa derivada de 2×33.485 linhas de treino do manifesto, e até 100 mil features conforme configuração atual. Medição: traduzir somente treino, comparar EN/PT na validação (n=800 por idioma) e exigir não inferioridade EN mais ganho PT; recalibrar cortes apenas na validação.",
        "3. **Embeddings multilíngues (`paraphrase-multilingual-MiniLM-L12-v2`) + classificador linear.** Prós: representação compartilhada entre idiomas e benchmark direto com o concorrente. Contras: exige baixar modelo, inferência mais lenta e armazenamento/cache dos vetores; menor explicabilidade lexical. Custo: nesta etapa não medido; precisa disponibilizar o modelo e dependências, sem instalação agora. Para pouca RAM, gerar embeddings em lotes, salvar `float32`/memmap e treinar apenas a cabeça linear. Medição: congelar o encoder; selecionar cabeça/regularização e cortes só na validação; registrar macro-F1 EN/PT, RAM de pico, tamanho, latência p50/p95 e roteamento.",
        "4. **Combinação de modelos.** Prós: TF-IDF pode preservar excelência EN e embeddings/ tradução cobrir PT; fallback por idioma reduz regressão. Contras: duas pipelines, calibração e monitoramento mais complexos; combinação por score bruto é inválida sem calibração comum. Custo: soma dos componentes. Medição: na validação, comparar roteamento determinístico por idioma, stacking out-of-fold ou média de probabilidades calibradas; exigir n≥100 por faixa e classe antes de conclusões.",
        "",
        "**Recomendação:** prototipar primeiro embeddings multilíngues com encoder congelado e cabeça linear, em lotes, porque ataca diretamente a causa raiz (espaço lexical monolíngue) e é a comparação mais limpa com o concorrente. Manter o TF-IDF para EN numa combinação por detecção de idioma apenas se a validação mostrar que o encoder perde desempenho EN. Em paralelo, PT→EN é o baseline de baixo esforço e deve ser medido antes da decisão final; ele pode vencer em custo/qualidade se houver uma API já aprovada. Nenhuma alternativa deve ser escolhida ou calibrada no teste congelado.",
        "",
        "## Premissas e limites",
        "",
        "- “Quase vazio” usa dois cortes diagnósticos declarados (nnz≤2; cobertura≤5%), não uma definição operacional de qualidade.",
        "- O score é `predict_proba` máximo não calibrado, conforme o manifesto; não é probabilidade validada fora do inglês.",
        "- A identificação de termos sobreviventes é mecânica pelo vocabulário; nomes de produto não foram inferidos por uma lista externa.",
        "- Os 800 tickets são uma amostra balanceada (100 por classe), portanto proporções de classes previstas descrevem este teste e não prevalência de produção.",
    ]
    (OUT / "diagnostico_causa_raiz.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "ok", "output_dir": str(OUT), "n_test": len(test),
        "macro_f1_en": aggregates["en"]["macro_f1"], "macro_f1_pt": aggregates["pt"]["macro_f1"],
        "token_coverage_en": cov_en["token_coverage_micro"], "token_coverage_pt": cov_pt["token_coverage_micro"],
        "empty_pt_n": cov_pt["empty_n"], "near_empty_pt_n": cov_pt["near_empty_nnz_le_2_n"],
        "default_class": default_class, "pt_high_band_errors_n": score_summary["pt"]["wrong_high_band_n"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
