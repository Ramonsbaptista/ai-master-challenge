from __future__ import annotations

import os

import numpy as np

from .core import route, routing_thresholds
from .language import should_send_to_human
from .out_of_scope import should_divert_robustness


MAX_TICKET_LENGTH = 5000

CATEGORY_NAMES = {
    "Access": "Acesso a sistemas",
    "Administrative rights": "Permissões administrativas",
    "HR Support": "Atendimento de Recursos Humanos",
    "Hardware": "Equipamentos",
    "Internal Project": "Projetos internos",
    "Miscellaneous": "Assuntos gerais",
    "Purchase": "Compras",
    "Storage": "Armazenamento",
}


class TicketInputError(ValueError):
    pass


def classify_ticket(text: str, model, manifest: dict, guard: dict,
                    safety_mode: bool = False,
                    out_of_scope_guard: bool | None = None) -> dict:
    """Aplica uma única regra de classificação para CLI e interface web."""
    clean_text = text.strip()
    if not clean_text:
        raise TicketInputError("Digite o texto do ticket antes de analisar.")
    if len(clean_text) > MAX_TICKET_LENGTH:
        raise TicketInputError(
            f"O ticket tem {len(clean_text):,} caracteres. O limite é {MAX_TICKET_LENGTH:,}; "
            "reduza o texto e tente novamente."
        )

    probabilities = model.predict_proba([clean_text])[0]
    index = int(np.argmax(probabilities))
    score = float(probabilities[index])
    category = str(model.classes_[index])
    low, high = routing_thresholds(manifest)
    original_band = str(route(np.array([score]), low, high)[0])
    diverted, coverage, recognized, total = should_send_to_human(clean_text, model, guard)
    if out_of_scope_guard is None:
        out_of_scope_guard = os.getenv("TICKET_CLASSIFIER_ROBUSTNESS_GUARD", "").casefold() in {
            "1", "true", "yes", "on"
        }
    out_of_scope_diversion = bool(out_of_scope_guard and should_divert_robustness(clean_text))

    if safety_mode:
        band = "modo_seguranca"
        reason = "O modo de segurança está ativo; nenhum ticket é encaminhado automaticamente."
    elif out_of_scope_diversion:
        band = "fora_do_escopo"
        reason = "O assunto pode estar fora das oito filas de TI; uma pessoa fará a análise."
    elif diverted:
        band = "protecao_idioma"
        reason = "O sistema ainda não foi validado para este idioma; uma pessoa fará a análise."
    elif original_band != "alta":
        band = original_band
        reason = "O modelo não reconheceu o assunto com segurança suficiente para encaminhar sozinho."
    else:
        band = original_band
        reason = "O modelo reconheceu o assunto com segurança suficiente para automatizar o encaminhamento."

    automatic = not safety_mode and not diverted and not out_of_scope_diversion and original_band == "alta"
    return {
        "automatic": automatic,
        "decision": "encaminhamento_automatico" if automatic else "analise_humana",
        "headline": "Vai direto para a fila" if automatic else "Vai para uma pessoa",
        "reason": reason,
        "category": category,
        "category_name": CATEGORY_NAMES.get(category, category),
        "score": score,
        "band": band,
        "original_band": original_band,
        "language_diversion": diverted,
        "out_of_scope_diversion": out_of_scope_diversion,
        "coverage": coverage,
        "recognized": recognized,
        "total": total,
    }
