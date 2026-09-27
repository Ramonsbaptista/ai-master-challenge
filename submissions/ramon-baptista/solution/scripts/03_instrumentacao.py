from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OUTPUT = ROOT / "submissions" / "ramon-baptista" / "solution" / "outputs" / "03_instrumentacao_numeros.json"

total = 8469
closed = 2769
invalid = 1365
valid = 1404
ratings = 2769
dataset_2 = 47837

# Cenário do diagnóstico: controle determinístico bloqueia 90% das cronologias inválidas.
# Arredondamento para cima: o cenário exige prevenir pelo menos 90% dos casos.
prevented_90 = math.ceil(invalid * 0.90)
remaining_invalid = invalid - prevented_90
usable_after = valid + prevented_90

# Margem de erro conservadora para proporções, p=0,5, aproximação normal, 95%.
def margin_95(n: int) -> float:
    return 1.96 * math.sqrt(0.25 / n)

result = {
    "observado": {
        "tickets_base_1": total,
        "avaliacoes": ratings,
        "taxa_avaliacoes_pct": 100 * ratings / total,
        "fechados_completos": closed,
        "cronologias_invalidas": invalid,
        "invalidas_entre_fechados_pct": 100 * invalid / closed,
        "tempos_validos": valid,
        "validos_entre_fechados_pct": 100 * valid / closed,
        "dataset_2_textos": dataset_2,
    },
    "premissa_controle_90_pct": {
        "registros_invalidos_prevenidos": prevented_90,
        "registros_invalidos_remanescentes": remaining_invalid,
        "registros_cronologicamente_utilizaveis": usable_after,
        "cobertura_utilizavel_fechados_pct": 100 * usable_after / closed,
    },
    "amostragem": {
        "n_100_margem_95_pontos_percentuais": 100 * margin_95(100),
        "n_400_margem_95_pontos_percentuais": 100 * margin_95(400),
    },
}

# Sensibilidade ilustrativa de capacidade. Somente premissas externas já declaradas variam:
# participação das faixas, minutos atuais/futuros por ticket e custo carregado por hora.
scenarios = {
    "conservador": {
        "shares": {"A": 0.10, "B": 0.55, "C": 0.35},
        "current": {"A": 12, "B": 20, "C": 35},
        "future": {"A": 4, "B": 16, "C": 35},
        "hourly_cost": 40,
    },
    "base": {
        "shares": {"A": 0.20, "B": 0.65, "C": 0.15},
        "current": {"A": 12, "B": 20, "C": 35},
        "future": {"A": 2, "B": 13, "C": 35},
        "hourly_cost": 50,
    },
    "favoravel": {
        "shares": {"A": 0.30, "B": 0.60, "C": 0.10},
        "current": {"A": 14, "B": 22, "C": 35},
        "future": {"A": 1, "B": 10, "C": 35},
        "hourly_cost": 60,
    },
}


def capacity_case(case: dict) -> dict:
    shares = case["shares"]
    current = case["current"]
    future = case["future"]
    hours_current = total * sum(shares[k] * current[k] for k in shares) / 60
    hours_future = total * sum(shares[k] * future[k] for k in shares) / 60
    hours_released = hours_current - hours_future
    return {
        "n_tickets": total,
        "horas_atuais": hours_current,
        "horas_futuras": hours_future,
        "horas_liberadas": hours_released,
        "capacidade_liberada_pct": 100 * hours_released / hours_current,
        "beneficio_bruto_reais": hours_released * case["hourly_cost"],
    }


result["cenarios_capacidade"] = {}
for name, case in scenarios.items():
    result["cenarios_capacidade"][name] = {
        "premissas": {
            "participacao_pct": {k: 100 * v for k, v in case["shares"].items()},
            "minutos_atuais": case["current"],
            "minutos_futuros": case["future"],
            "custo_carregado_reais_hora": case["hourly_cost"],
            "origem": "premissas ilustrativas; não constam das bases",
        },
        "resultados": capacity_case(case),
    }

# Sensibilidade um fator por vez ao redor do cenário-base. Para cada família de premissas,
# substitui-se apenas o valor conservador/favorável e mede-se a amplitude do benefício bruto.
base = scenarios["base"]
sensitivity = {}
for factor in ("shares", "minutes", "hourly_cost"):
    values = []
    for endpoint in ("conservador", "favoravel"):
        mixed = {
            "shares": base["shares"],
            "current": base["current"],
            "future": base["future"],
            "hourly_cost": base["hourly_cost"],
        }
        if factor == "minutes":
            mixed["current"] = scenarios[endpoint]["current"]
            mixed["future"] = scenarios[endpoint]["future"]
        else:
            mixed[factor] = scenarios[endpoint][factor]
        values.append(capacity_case(mixed)["beneficio_bruto_reais"])
    sensitivity[factor] = {
        "beneficio_bruto_min_reais": min(values),
        "beneficio_bruto_max_reais": max(values),
        "amplitude_reais": max(values) - min(values),
    }
result["sensibilidade_um_fator_por_vez"] = sensitivity
result["premissa_mais_sensivel"] = max(sensitivity, key=lambda key: sensitivity[key]["amplitude_reais"])

OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
