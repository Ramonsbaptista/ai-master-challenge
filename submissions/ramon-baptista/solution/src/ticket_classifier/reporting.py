from __future__ import annotations

from .core import OUTPUTS, load_manifest


def pct(value: float) -> str:
    return f"{100 * value:.2f}%".replace(".", ",")


def formula_row(row: dict) -> str:
    vp, fp, fn, vn = (row[k] for k in ("VP", "FP", "FN", "VN"))
    pden, rden, sden = vp + fp, vp + fn, vn + fp
    return (
        f"| {row['class']} | {row['n']} | {vp} | {fp} | {fn} | {vn} | "
        f"{vp}/({vp}+{fp})={pct(row['precision'])} | "
        f"{vp}/({vp}+{fn})={pct(row['recall'])} | "
        f"{vn}/({vn}+{fp})={pct(row['specificity'])} | "
        f"2×{row['precision']:.6f}×{row['recall']:.6f}/({row['precision']:.6f}+{row['recall']:.6f})={pct(row['f1'])} |"
    )


def main() -> None:
    m = load_manifest()
    test = m["test"]
    n = test["n"]
    lines = [
        "# Avaliação congelada do protótipo", "",
        f"Método: TF-IDF + regressão logística; hiperparâmetros escolhidos por macro-F1 na validação. Teste n={n}, usado uma única vez e reproduzido por IDs congelados.", "",
        "## Matriz de confusão", "",
        "Linhas = classe real; colunas = classe prevista. Ordem: " + ", ".join(m["classes"]) + ".", "",
        "```text", *["\t".join(map(str, row)) for row in test["confusion_matrix"]], "```", "",
        "Checagem: a soma total da matriz é " + str(sum(map(sum, test["confusion_matrix"]))) + f" e bate com n={n}; cada linha foi validada contra o n real da classe.", "",
        "## Métricas por classe", "",
        "| Classe | n | VP | FP | FN | VN | Precisão = VP/(VP+FP) | Recall = VP/(VP+FN) | Especificidade = VN/(VN+FP) | F1 = 2PR/(P+R) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        *[formula_row(row) for row in test["per_class"]], "",
        "Fundamento: métricas one-vs-rest por classe; macro-F1 dá peso igual a cada classe, F1 ponderado usa o n real de cada classe e acurácia é a diagonal sobre o total.", "",
        "## Modelo versus baseline", "",
        "| Método | n | Macro-F1 | F1 ponderado | Acurácia |", "|---|---:|---:|---:|---:|",
        f"| Modelo | {n} | {pct(test['metrics']['macro_f1'])} | {pct(test['metrics']['weighted_f1'])} | {pct(test['metrics']['accuracy'])} |",
        f"| Baseline (classe majoritária: {m['majority_class']}) | {n} | {pct(test['baseline_metrics']['macro_f1'])} | {pct(test['baseline_metrics']['weighted_f1'])} | {pct(test['baseline_metrics']['accuracy'])} |", "",
        "## Roteamento por score do modelo", "",
        f"Cortes escolhidos apenas na validação: baixa < {m['routing_thresholds']['low']:.6f}; média de {m['routing_thresholds']['low']:.6f} a < {m['routing_thresholds']['high']:.6f}; alta >= {m['routing_thresholds']['high']:.6f}.", "",
        "Premissas operacionais: n>=100 por faixa, alta com acerto >=90%, média >=75%, monotonicidade; maximização da cobertura alta e depois média. O score não é calibrado.", "",
        "| Faixa | n | Cobertura | Taxa de acerto |", "|---|---:|---:|---:|",
    ]
    for band in ("baixa", "media", "alta"):
        r = m["test_routing"][band]
        lines.append(f"| {band} | {r['n']} | {pct(r['coverage'])} | {pct(r['accuracy'])} |")
    lines += ["", "Fundamento: cobertura é n da faixa/n do teste; taxa de acerto é predições corretas/n da faixa. Os cortes não foram ajustados no teste.", ""]
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    (OUTPUTS / "model_evaluation.md").write_text("\n".join(lines), encoding="utf-8")
    print(OUTPUTS / "model_evaluation.md")


if __name__ == "__main__":
    main()
