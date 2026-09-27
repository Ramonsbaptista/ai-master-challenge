from __future__ import annotations

import csv
import hashlib
import json
import os
from datetime import datetime

from .core import OUTPUTS, PrototypeError, load_manifest, load_verified_model
from .evaluate import reproduce
from .language import load_language_guard
from .service import CATEGORY_NAMES, TicketInputError, classify_ticket

def safety_mode_active() -> bool:
    return os.getenv("TICKET_CLASSIFIER_KILL_SWITCH", "").strip().casefold() in {
        "1", "true", "yes", "on", "sim"
    }


def save_history(text: str, decision: str, category: str, score: float | None, band: str) -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    path = OUTPUTS / "classification_history.csv"
    if path.exists() and path.stat().st_size:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            old_fields = reader.fieldnames or []
            old_rows = list(reader)
        if "texto" in old_fields:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["data_hora", "texto_sha256", "tamanho_caracteres", "decisao",
                                 "categoria_tecnica", "score_nao_calibrado", "faixa_tecnica"])
                for row in old_rows:
                    old_text = row.get("texto", "")
                    writer.writerow([row.get("data_hora", ""),
                                     hashlib.sha256(old_text.encode("utf-8")).hexdigest(),
                                     len(old_text), "historico_sem_decisao_explicita",
                                     row.get("categoria_tecnica", ""),
                                     row.get("score_nao_calibrado", ""),
                                     row.get("faixa_tecnica", "")])
    is_new = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        if is_new:
            writer.writerow(["data_hora", "texto_sha256", "tamanho_caracteres", "decisao",
                             "categoria_tecnica", "score_nao_calibrado", "faixa_tecnica"])
        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        rendered_score = "" if score is None else f"{score:.6f}"
        writer.writerow([datetime.now().astimezone().isoformat(timespec="seconds"), text_hash,
                         len(text), decision, category, rendered_score, band])


def classification_message(category: str, score: float, band: str, manifest: dict,
                           language_diversion: bool = False, coverage: float | None = None,
                           recognized: int | None = None, total: int | None = None) -> str:
    business_category = CATEGORY_NAMES.get(category, category)
    if language_diversion:
        decision = "Decisão: enviar para uma pessoa analisar."
        reason = "Por quê: o sistema ainda não foi validado para textos em português; um atendente vai analisar."
        risk = "Proteção aplicada: nenhuma fila será escolhida automaticamente."
    elif band == "alta":
        routing = manifest["test_routing"]["alta"]
        decision = f"Decisão: encaminhar direto para a fila de {business_category}."
        reason = "Por quê: o sistema reconheceu o assunto com segurança suficiente para automatizar o encaminhamento."
        risk = (f"Risco: em tickets com este nível de segurança, o sistema acertou "
                f"{round(100 * routing['accuracy'])} de cada 100 no teste congelado "
                f"(método: acertos/n da faixa; n={routing['n']}).")
    else:
        decision = "Decisão: enviar para uma pessoa analisar."
        reason = "Por quê: o sistema não reconheceu o assunto com segurança suficiente para encaminhar sozinho."
        risk = "Proteção aplicada: nenhuma fila será escolhida automaticamente."
    detail = (f"Detalhe técnico: categoria sugerida={category}; score não calibrado={score:.4f}; "
              f"faixa técnica={band}.")
    if language_diversion:
        detail += (f" Cobertura do vocabulário inglês={coverage:.1%} "
                   f"({recognized}/{total} tokens reconhecidos).")
    return "\n".join((decision, reason, risk, detail))


def classify() -> None:
    text = input("Digite o texto do ticket: ").strip()
    if not text:
        save_history(text, "analise_humana", "", None, "entrada_invalida")
        print("Decisão: enviar para uma pessoa analisar.\n"
              "Por quê: o ticket está vazio; nenhuma fila será escolhida automaticamente.\n"
              "Proteção aplicada: falha segura, sem erro técnico.")
        return
    model, manifest = load_verified_model()
    guard = load_language_guard()
    try:
        result = classify_ticket(text, model, manifest, guard, safety_mode_active())
    except TicketInputError as exc:
        save_history(text, "analise_humana", "", None, "entrada_invalida")
        print(f"Decisão: enviar para uma pessoa analisar.\nPor quê: {exc}")
        return
    save_history(text, result["decision"], result["category"], result["score"], result["band"])
    if result["band"] == "modo_seguranca":
        print("Decisão: enviar para uma pessoa analisar.\n"
              "Por quê: o modo de segurança está ativo; nenhum ticket é encaminhado automaticamente.\n"
              f"Detalhe técnico: categoria sugerida={result['category']}; score não calibrado={result['score']:.4f}; "
              f"faixa original={result['original_band']}.")
    else:
        print(classification_message(result["category"], result["score"], result["band"], manifest,
                                     result["language_diversion"], result["coverage"],
                                     result["recognized"], result["total"]))
    print(f"Histórico salvo em: {OUTPUTS / 'classification_history.csv'}")


def print_evaluation() -> None:
    result, manifest = reproduce(), load_manifest()
    test, high = manifest["test"], manifest["test_routing"]["alta"]
    print("\nConclusão para o negócio")
    print(f"A reprodução passou: hashes, registros e resultados conferem no teste congelado (n={result['n']}).")
    print(f"O modelo acertou {100 * test['metrics']['accuracy']:.2f}% dos tickets (método: diagonal da matriz/n; n={result['n']}).")
    print(f"Na automação, acertou {round(100 * high['accuracy'])} de cada 100 tickets (método: acertos/n da faixa alta; n={high['n']}).")
    print("Premissa operacional: somente essa faixa é encaminhada automaticamente; os demais tickets vão para uma pessoa.")
    print("\nDetalhes técnicos — matriz de confusão (linhas=reais; colunas=previstas)")
    print("Ordem: " + " | ".join(CATEGORY_NAMES[c] for c in manifest["classes"]))
    for matrix_row in result["matrix"]:
        print(" ".join(f"{value:4d}" for value in matrix_row))
    print("\nMétricas por categoria (one-vs-rest; todas as categorias têm n>=100)")
    for row in result["per_class"]:
        vp, fp, fn, vn = (row[k] for k in ("VP", "FP", "FN", "VN"))
        print(f"{CATEGORY_NAMES[row['class']]} (n={row['n']}): VP={vp}, FP={fp}, FN={fn}, VN={vn}")
        print(f"  precisão = {vp}/({vp}+{fp}) = {row['precision']:.4f}; "
              f"recall = {vp}/({vp}+{fn}) = {row['recall']:.4f}; "
              f"especificidade = {vn}/({vn}+{fp}) = {row['specificity']:.4f}; "
              f"F1 = 2×P×R/(P+R) = {row['f1']:.4f}")
    metrics = result["metrics"]
    print(f"\nAgregados (n={metrics['n']}): macro-F1={metrics['macro_f1']:.4f} (média simples entre categorias); "
          f"F1 ponderado={metrics['weighted_f1']:.4f} (ponderado pelo n de cada categoria); "
          f"acurácia={metrics['accuracy']:.4f} (diagonal/n).")
    print("Fundamento: o macro-F1 é o principal porque dá o mesmo peso a categorias desbalanceadas; "
          "as demais métricas mostram desempenho global e por categoria.")


def info() -> None:
    m = load_manifest()
    summary = {k: m[k] for k in ("model_version", "created_on", "seed", "method", "classes",
                                  "routing_thresholds", "versions", "files")}
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main() -> None:
    actions = {"1": classify, "2": print_evaluation, "3": info}
    while True:
        if safety_mode_active():
            print("\nModo de segurança ativo: todos os tickets vão para análise humana")
        print("\n1 Classificar um ticket\n2 Reproduzir a avaliação\n3 Informações técnicas do modelo\n0 Sair")
        choice = input("> ").strip()
        if choice == "0":
            return
        try:
            actions.get(choice, lambda: print("Opção inválida. Escolha 0, 1, 2 ou 3."))()
        except (PrototypeError, AssertionError, FileNotFoundError) as exc:
            print(exc)


if __name__ == "__main__":
    main()
