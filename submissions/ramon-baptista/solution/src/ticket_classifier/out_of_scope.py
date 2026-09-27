from __future__ import annotations

import re


# Camada proposta, desativada por padrão. Os termos foram escolhidos somente na
# parcela de calibração do experimento de robustez; ver outputs/robustez/.
OUT_OF_SCOPE_PATTERNS = (
    r"\brefund(?:ed|s)?\b",
    r"\b(?:billing|charged|chargeback)\b",
    r"\b(?:delivery|shipment)\b",
    r"\b(?:cancel subscription|cancel my order)\b",
    r"\b(?:complaint|complain)\b",
)

# Padrões de ambiguidade que produziram encaminhamento automático errado na
# metade de calibração do conjunto sintético. Não escolhem outra fila: bloqueiam
# a automação. Mantidos separados para que a evidência e o custo sejam auditáveis.
AMBIGUITY_PATTERNS = (
    r"\bcannot sign in\b",
    r"\b(?:privileged|privil\w*) access\b",
    r"\badd (?:the )?team to project\b",
    r"\bhelp desk\b",
    r"\bprocurement order\b",
    r"\bbuy a?\s*(?:new )?(?:license|office phone)\b",
    r"\bmore\s*space in project drive\b",
)


def should_divert_out_of_scope(text: str) -> bool:
    """Detecta assuntos comerciais fora das oito filas internas de TI."""
    normalized = text.casefold()
    return any(re.search(pattern, normalized) for pattern in OUT_OF_SCOPE_PATTERNS)


def should_divert_robustness(text: str) -> bool:
    """Barreira proposta e calibrada para assuntos fora do escopo."""
    return should_divert_out_of_scope(text)
