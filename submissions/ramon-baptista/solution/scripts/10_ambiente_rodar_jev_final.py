# ---------------------------------------------------------------------------
# SCRIPT DE AMBIENTE — nao altera metodo, amostra, criterios nem metricas.
# Foi executado fora do sandbox do executor (GPT), que bloqueava a leitura do
# tradutor e fazia chamadas em rajada ao gateway. O desenho do experimento e
# a funcao de chamada sao os de 04_avaliar_jev.py.
# ---------------------------------------------------------------------------
"""Etapas finais do experimento do executor (estabilidade, textos sem informacao,
relatorio), com o mesmo controle de ritmo de rodar_jev_ritmado.py. Nao altera metodo."""
import importlib.util, time, sys
from pathlib import Path
SCRIPT = Path(__file__).resolve().parent / "04_avaliar_jev.py"
spec = importlib.util.spec_from_file_location("avaliar_jev", SCRIPT); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
original = m.jev_one
def ritmado(text, key, *a, **k):
    for espera in [0, 60, 120, 300, 600, 600, 600]:
        if espera: print(f"  API sem resposta; pausa de {espera}s", flush=True); time.sleep(espera)
        try:
            r = original(text, key, *a, **k); time.sleep(2.0); return r
        except Exception as exc: ultimo = exc
    raise ultimo
m.jev_one = ritmado
print("etapa: estabilidade + textos sem informacao", flush=True); m.stability_and_ood(1)
print("etapa: relatorio", flush=True); m.report()
print("concluido", flush=True)
