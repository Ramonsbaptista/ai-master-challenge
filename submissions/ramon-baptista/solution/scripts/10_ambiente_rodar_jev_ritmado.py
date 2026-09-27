# ---------------------------------------------------------------------------
# SCRIPT DE AMBIENTE — nao altera metodo, amostra, criterios nem metricas.
# Foi executado fora do sandbox do executor (GPT), que bloqueava a leitura do
# tradutor e fazia chamadas em rajada ao gateway. O desenho do experimento e
# a funcao de chamada sao os de 04_avaliar_jev.py.
# ---------------------------------------------------------------------------
"""Executa as chamadas pendentes ao Jev com ritmo controlado.

Papel deste script: operacao de ambiente. O desenho do experimento, as tarefas,
o formato do checkpoint e a funcao de chamada sao os do executor, em
submissions/ramon-baptista/solution/scripts/04_avaliar_jev.py. Aqui apenas:

- rodamos em serie (uma chamada por vez), porque o plano gratuito do gateway
  para de responder depois de ~29 chamadas em rajada;
- respeitamos um intervalo entre chamadas e fazemos pausas longas quando a API
  para de responder, em vez de desistir;
- gravamos no MESMO checkpoint (jev_results.jsonl), no mesmo formato.

Nada aqui altera metodo, amostra, criterios ou metricas.
"""
from __future__ import annotations

import importlib.util
import os
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SCRIPT = Path(__file__).resolve().parent / "04_avaliar_jev.py"

INTERVALO_S = float(os.environ.get("JEV_INTERVALO_S", "2.0"))
PAUSA_BLOQUEIO_S = [60, 120, 300, 600]  # espera crescente quando a API para de responder


def carregar_modulo():
    spec = importlib.util.spec_from_file_location("avaliar_jev", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    m = carregar_modulo()
    import pandas as pd

    key = m.load_key()
    sample = pd.read_csv(m.OUT / "sample_bilingual.csv")
    tarefas = []
    for row in sample.itertuples(index=False):
        for language, text in (("en", row.Document), ("pt", row.Document_pt)):
            tarefas.append({"record_id": row.record_id, "partition": row.partition,
                            "true_label": row.Topic_group, "language": language, "text": text})

    caminho = m.OUT / "jev_results.jsonl"
    feitas = m.read_jsonl(caminho) if caminho.exists() else []
    concluidas = {m.call_key(r) for r in feitas}
    if len(concluidas) != len(feitas):
        print("checkpoint com chaves duplicadas; parando", flush=True)
        return 1
    pendentes = [t for t in tarefas if m.call_key(t) not in concluidas]
    total = len(tarefas)
    print(f"retomando: {len(feitas)} concluidas, {len(pendentes)} pendentes, total {total}", flush=True)

    inicio = time.time()
    for n, tarefa in enumerate(pendentes, start=1):
        tentativa_bloqueio = 0
        while True:
            try:
                resultado = m.jev_one(tarefa["text"], key)
                break
            except Exception as exc:  # a mensagem do executor nao contem a chave
                espera = PAUSA_BLOQUEIO_S[min(tentativa_bloqueio, len(PAUSA_BLOQUEIO_S) - 1)]
                tentativa_bloqueio += 1
                print(f"  API sem resposta ({type(exc).__name__}); pausa de {espera}s "
                      f"[tentativa {tentativa_bloqueio}]", flush=True)
                if tentativa_bloqueio > 12:
                    print("  bloqueio persistente; parando com checkpoint salvo", flush=True)
                    return 2
                time.sleep(espera)
        linha = {k: v for k, v in tarefa.items() if k != "text"} | resultado
        m.append_jsonl(caminho, linha)
        feitas_agora = len(feitas) + n
        if n % 25 == 0 or feitas_agora == total:
            decorrido = (time.time() - inicio) / 60
            ritmo = n / max(decorrido, 1e-9)
            restante = (len(pendentes) - n) / max(ritmo, 1e-9)
            print(f"  {feitas_agora}/{total} | {decorrido:.1f} min | ~{restante:.0f} min restantes", flush=True)
        time.sleep(INTERVALO_S)

    print("concluido", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
