# ---------------------------------------------------------------------------
# SCRIPT DE AMBIENTE — nao altera metodo, amostra, criterios nem metricas.
# Foi executado fora do sandbox do executor (GPT), que bloqueava a leitura do
# tradutor e fazia chamadas em rajada ao gateway. O desenho do experimento e
# a funcao de chamada sao os de 04_avaliar_jev.py.
# ---------------------------------------------------------------------------
"""Gera a amostra bilingue para o experimento do Jev.

Papel deste script: preparacao de ambiente/dados. O metodo (100 por classe em
validacao e teste, traducao offline Argos en->pt) foi decidido pelo executor;
aqui apenas executamos a traducao fora do sandbox, que bloqueia a leitura do
modelo.

Saida: outputs/jev_evaluation/sample_bilingual.csv com record_id, particao,
classe verdadeira, texto em ingles, texto em portugues e o sha256 do texto de
origem (para conferencia).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

# defina ARGOS_PACKAGES_DIR apontando para a pasta do modelo Argos en->pt 1.9

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "all_tickets_processed_improved_v3.csv"
SPLIT = ROOT / "artifacts" / "split_ids.json"
OUT = ROOT / "outputs" / "jev_evaluation"
CACHE = OUT / "translation_cache.json"
DESTINO = OUT / "sample_bilingual.csv"
SEED = 20260922
POR_CLASSE = 100


def sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(DATA)
    # mesma regra de identificacao usada pelo executor em 04_avaliar_jev.py:
    # sha256 de "posicao \x1f texto \x1f rotulo".
    frame["record_id"] = [
        hashlib.sha256(f"{i}\x1f{texto}\x1f{rotulo}".encode()).hexdigest()
        for i, (texto, rotulo) in enumerate(zip(frame.Document, frame.Topic_group, strict=True))
    ]
    split = json.loads(SPLIT.read_text(encoding="utf-8"))

    partes = []
    for nome in ("validation", "test"):
        sub = frame[frame.record_id.isin(split[nome])]
        # amostragem estratificada sem groupby.apply: o pandas 3.0 remove a coluna
        # de agrupamento do resultado, o que quebrava o restante do script.
        for classe in sorted(sub["Topic_group"].unique()):
            grupo = sub[sub["Topic_group"] == classe]
            escolhido = grupo.sample(n=min(POR_CLASSE, len(grupo)), random_state=SEED)
            partes.append(escolhido.assign(partition=nome))
    amostra = pd.concat(partes, ignore_index=True)
    print(f"amostra: {len(amostra)} textos "
          f"({amostra.partition.value_counts().to_dict()})", flush=True)

    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    print(f"cache existente: {len(cache)} traducoes", flush=True)

    import argostranslate.translate as tr
    tr.translate("warmup", "en", "pt")  # inicializa o pipeline uma unica vez

    t0 = time.time()
    traduzidos = []
    for i, texto in enumerate(amostra["Document"].astype(str), start=1):
        h = sha(texto)
        if h not in cache:
            cache[h] = tr.translate(texto, "en", "pt").strip()
            if i % 50 == 0:
                CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
                passado = time.time() - t0
                print(f"  {i}/{len(amostra)} | {passado/60:.1f} min decorridos", flush=True)
        traduzidos.append(cache[h])
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")

    saida = pd.DataFrame({
        "record_id": amostra.record_id.values,
        "partition": amostra.partition.values,
        "Topic_group": amostra.Topic_group.values,
        "Document": amostra.Document.astype(str).values,
        "Document_pt": traduzidos,
        "sha256_en": [sha(t) for t in amostra["Document"].astype(str)],
    })
    saida.to_csv(DESTINO, index=False, lineterminator="\n", encoding="utf-8")
    print(f"gravado: {DESTINO} | {len(saida)} linhas | {(time.time()-t0)/60:.1f} min", flush=True)


if __name__ == "__main__":
    sys.exit(main())
