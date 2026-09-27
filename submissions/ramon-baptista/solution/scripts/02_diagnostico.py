from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


ROOT = Path(__file__).resolve().parents[4]
DATA_PATH = ROOT / "data" / "customer_support_tickets.csv"
OUTPUT_DIR = ROOT / "submissions" / "ramon-baptista" / "solution" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SEGMENTS = ["Ticket Channel", "Ticket Priority", "Ticket Type"]
# O ranking decisório usa dois fatores para preservar amostra. O cruzamento antigo de três
# fatores gerava grupos de n=10 a 23 e, portanto, só poderia ser exploratório.
COMBINATION = ["Ticket Channel", "Ticket Type"]
RATING_CATEGORICAL = [
    "Ticket Channel",
    "Ticket Priority",
    "Ticket Type",
    "Ticket Subject",
    "Product Purchased",
    "Customer Gender",
]


def pct(num: float, den: float) -> float:
    return 100.0 * num / den if den else np.nan


def fmt_int(value: float | int) -> str:
    return f"{int(round(value)):,}".replace(",", ".")


def fmt_num(value: float, digits: int = 1) -> str:
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def md_table(frame: pd.DataFrame) -> str:
    shown = frame.copy()
    lines = [
        "| " + " | ".join(map(str, shown.columns)) + " |",
        "|" + "|".join(["---"] * len(shown.columns)) + "|",
    ]
    for row in shown.itertuples(index=False, name=None):
        values = []
        for value in row:
            if pd.isna(value):
                text = "n.d."
            elif isinstance(value, (float, np.floating)):
                text = fmt_num(float(value), 2)
            else:
                text = str(value)
            values.append(text.replace("|", "\\|").replace("\n", " "))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def segment_summary(data: pd.DataFrame, column: str) -> pd.DataFrame:
    rows = []
    for value, group in data.groupby(column, dropna=False, observed=True):
        valid = group.loc[group["valid_duration"]]
        invalid = group.loc[group["invalid_duration"]]
        durations = valid["resolution_hours"]
        rows.append(
            {
                "dimensao": column,
                "segmento": value,
                "tickets_total": len(group),
                "pct_volume_total": pct(len(group), len(data)),
                "fechados": int(group["complete_closed"].sum()),
                "fechados_validos_tempo": len(valid),
                "pct_cobertura_tempo_no_segmento": pct(len(valid), len(group)),
                "tempos_invalidos": len(invalid),
                "pct_invalido_entre_fechados": pct(len(invalid), int(group["complete_closed"].sum())),
                "mediana_h": durations.median(),
                "p75_h": durations.quantile(0.75),
                "p90_h": durations.quantile(0.90),
                "media_h": durations.mean(),
            }
        )
    return pd.DataFrame(rows)


def categorical_wald(model, variable: str) -> tuple[float, int, float]:
    prefix = f"C({variable})["
    indices = [i for i, name in enumerate(model.model.exog_names) if name.startswith(prefix)]
    restriction = np.zeros((len(indices), len(model.params)))
    for row, index in enumerate(indices):
        restriction[row, index] = 1.0
    test = model.wald_test(restriction, scalar=True)
    return float(test.statistic), len(indices), float(test.pvalue)


def adjusted_category_range(model, analysis: pd.DataFrame, variable: str) -> tuple[float, str, str]:
    levels = sorted(analysis[variable].dropna().unique())
    predictions = []
    for level in levels:
        scenario = analysis.copy()
        scenario[variable] = level
        predictions.append((level, float(model.predict(scenario).mean())))
    low = min(predictions, key=lambda item: item[1])
    high = max(predictions, key=lambda item: item[1])
    return high[1] - low[1], str(low[0]), str(high[0])


# Uma única leitura da fonte. Todas as saídas abaixo são derivadas desta execução.
df = pd.read_csv(DATA_PATH, low_memory=False)
df["first_response_dt"] = pd.to_datetime(df["First Response Time"], errors="coerce")
df["resolution_dt"] = pd.to_datetime(df["Time to Resolution"], errors="coerce")
df["rating"] = pd.to_numeric(df["Customer Satisfaction Rating"], errors="coerce")
df["age"] = pd.to_numeric(df["Customer Age"], errors="coerce")
df["complete_closed"] = (
    df["first_response_dt"].notna()
    & df["resolution_dt"].notna()
    & df["rating"].notna()
)
df["resolution_hours"] = (df["resolution_dt"] - df["first_response_dt"]).dt.total_seconds() / 3600
df["invalid_duration"] = df["complete_closed"] & df["resolution_hours"].lt(0)
df["valid_duration"] = df["complete_closed"] & df["resolution_hours"].ge(0)

total = len(df)
closed = int(df["complete_closed"].sum())
invalid = int(df["invalid_duration"].sum())
valid = int(df["valid_duration"].sum())
incomplete = total - closed
valid_df = df.loc[df["valid_duration"]].copy()

# Volume e tempo por cada dimensão pedida.
segment_tables = [segment_summary(df, column) for column in SEGMENTS]
segments = pd.concat(segment_tables, ignore_index=True)
segments.to_csv(OUTPUT_DIR / "02_volume_tempos_segmentos.csv", index=False, encoding="utf-8-sig")

# Combinações com base mínima para evitar rankings movidos por poucos casos.
combo_rows = []
for keys, group in df.groupby(COMBINATION, dropna=False, observed=True):
    good = group.loc[group["valid_duration"]]
    bad = group.loc[group["invalid_duration"]]
    durations = good["resolution_hours"]
    combo_rows.append(
        {
            **dict(zip(COMBINATION, keys)),
            "tickets_total": len(group),
            "fechados": int(group["complete_closed"].sum()),
            "fechados_validos_tempo": len(good),
            "tempos_invalidos": len(bad),
            "mediana_h": durations.median(),
            "p75_h": durations.quantile(0.75),
            "p90_h": durations.quantile(0.90),
        }
    )
combinations = pd.DataFrame(combo_rows)
minimum_n = 30
combinations["status_amostra"] = np.where(
    combinations["fechados_validos_tempo"].ge(minimum_n),
    "elegível para conclusão",
    "exploratório (n<30)",
)
combinations["elegivel_ranking"] = combinations["fechados_validos_tempo"].ge(minimum_n)
combinations = combinations.sort_values(
    ["elegivel_ranking", "mediana_h", "fechados_validos_tempo"], ascending=[False, False, False]
)
combinations.to_csv(OUTPUT_DIR / "02_combinacoes_gargalo.csv", index=False, encoding="utf-8-sig")
worst_combinations = combinations.loc[combinations["elegivel_ranking"]].head(10).copy()

# Satisfação: regressão linear multivariada com erros HC3. A nota é ordinal, mas o modelo
# estima diretamente diferenças em pontos; HC3 evita depender de variância constante.
# A amostra principal usa todos os avaliados para fatores observáveis que não dependem do tempo.
rating_df = df.loc[df["rating"].notna(), RATING_CATEGORICAL + ["age", "rating"]].dropna().copy()
cat_terms = " + ".join(f'C(Q("{column}"))' for column in RATING_CATEGORICAL)
# Q protege nomes com espaços; os nomes de coeficientes são tratados por termo abaixo.
rating_formula = f'rating ~ {cat_terms} + age'
rating_model = smf.ols(rating_formula, data=rating_df).fit(cov_type="HC3")

rating_tests = []
for variable in RATING_CATEGORICAL:
    term = f'C(Q("{variable}"))'
    indices = [
        index
        for index, name in enumerate(rating_model.model.exog_names)
        if name.startswith(term + "[")
    ]
    restriction = np.zeros((len(indices), len(rating_model.params)))
    for row, index in enumerate(indices):
        restriction[row, index] = 1.0
    test = rating_model.wald_test(restriction, scalar=True)

    levels = sorted(rating_df[variable].dropna().unique())
    predictions = []
    for level in levels:
        scenario = rating_df.copy()
        scenario[variable] = level
        predictions.append((str(level), float(rating_model.predict(scenario).mean())))
    low = min(predictions, key=lambda item: item[1])
    high = max(predictions, key=lambda item: item[1])
    rating_tests.append(
        {
            "variavel": variable,
            "amostra_n": len(rating_df),
            "teste": "Wald conjunto HC3",
            "estatistica": float(test.statistic),
            "graus_liberdade": len(indices),
            "p_valor": float(test.pvalue),
            "magnitude_ajustada_pontos": high[1] - low[1],
            "nivel_menor_predicao": low[0],
            "nivel_maior_predicao": high[0],
        }
    )

# Idade: efeito ajustado entre P25 e P75.
age_index = rating_model.model.exog_names.index("age")
age_test = rating_model.wald_test(np.eye(1, len(rating_model.params), age_index), scalar=True)
age_iqr = float(rating_df["age"].quantile(0.75) - rating_df["age"].quantile(0.25))
rating_tests.append(
    {
        "variavel": "Customer Age",
        "amostra_n": len(rating_df),
        "teste": "Wald HC3",
        "estatistica": float(age_test.statistic),
        "graus_liberdade": 1,
        "p_valor": float(age_test.pvalue),
        "magnitude_ajustada_pontos": abs(float(rating_model.params.iloc[age_index])) * age_iqr,
        "nivel_menor_predicao": "P25",
        "nivel_maior_predicao": "P75",
    }
)

# Tempo é testado separadamente somente nos 1.404 fechados cronologicamente válidos.
time_rating = valid_df[RATING_CATEGORICAL + ["age", "rating", "resolution_hours"]].dropna().copy()
time_rating["log_resolution_hours"] = np.log1p(time_rating["resolution_hours"])
time_formula = rating_formula + " + log_resolution_hours"
time_model = smf.ols(time_formula, data=time_rating).fit(cov_type="HC3")
time_index = time_model.model.exog_names.index("log_resolution_hours")
time_test = time_model.wald_test(np.eye(1, len(time_model.params), time_index), scalar=True)
q25 = float(time_rating["resolution_hours"].quantile(0.25))
q75 = float(time_rating["resolution_hours"].quantile(0.75))
time_effect = float(time_model.params.iloc[time_index]) * (np.log1p(q75) - np.log1p(q25))
rating_tests.append(
    {
        "variavel": "Tempo entre primeira resposta e resolução",
        "amostra_n": len(time_rating),
        "teste": "Wald HC3; tempo em log(1+h)",
        "estatistica": float(time_test.statistic),
        "graus_liberdade": 1,
        "p_valor": float(time_test.pvalue),
        "magnitude_ajustada_pontos": time_effect,
        "nivel_menor_predicao": f"P25={q25:.2f}h",
        "nivel_maior_predicao": f"P75={q75:.2f}h",
    }
)
rating_results = pd.DataFrame(rating_tests).sort_values("p_valor")
rating_results["significativo_5pct"] = rating_results["p_valor"].lt(0.05)
rating_results.to_csv(OUTPUT_DIR / "02_satisfacao_testes.csv", index=False, encoding="utf-8-sig")

# Tempo corrido excedente: horas acima do P90 dos tickets válidos do mesmo tipo. O P90 é
# usado como limite de cauda, em vez da mediana, para não classificar metade da operação
# como oportunidade por construção. É tempo corrido acumulado, não esforço de agentes.
benchmarks = valid_df.groupby("Ticket Type", observed=True)["resolution_hours"].quantile(0.90).rename("benchmark_h")
valid_df = valid_df.join(benchmarks, on="Ticket Type")
valid_df["excess_elapsed_hours"] = (valid_df["resolution_hours"] - valid_df["benchmark_h"]).clip(lower=0)
excess_total = float(valid_df["excess_elapsed_hours"].sum())
excess_by_type = (
    valid_df.groupby("Ticket Type", observed=True)
    .agg(
        tickets_validos=("Ticket ID", "size"),
        benchmark_p90_h=("benchmark_h", "first"),
        ticket_horas_excedentes=("excess_elapsed_hours", "sum"),
        tickets_acima_benchmark=("excess_elapsed_hours", lambda s: int(s.gt(0).sum())),
    )
    .reset_index()
    .sort_values("ticket_horas_excedentes", ascending=False)
)
excess_by_type.to_csv(OUTPUT_DIR / "02_tempo_corrido_excedente.csv", index=False, encoding="utf-8-sig")
# Nome legado citado apenas para retirar o artefato obsoleto durante a regeneração.
legacy_output = OUTPUT_DIR / "02_desperdicio_horas.csv"
if legacy_output.exists():
    legacy_output.unlink()

overall = valid_df["resolution_hours"].describe(percentiles=[0.25, 0.5, 0.75, 0.90])
summary = {
    "populacao": {
        "tickets_total": total,
        "fechados_completos": closed,
        "incompletos_estruturais": incomplete,
        "fechados_tempo_invalido": invalid,
        "fechados_tempo_valido": valid,
    },
    "tempo_valido_horas": {
        "mediana": float(overall["50%"]),
        "p75": float(overall["75%"]),
        "p90": float(overall["90%"]),
        "media": float(overall["mean"]),
    },
    "tempo_corrido_excedente": {
        "definicao": "soma das horas corridas acima do P90 do respectivo tipo de ticket",
        "referencia": "P90 por tipo; limite de cauda que não seleciona metade dos casos por construção",
        "amostra_n": valid,
        "ticket_horas_excedentes": excess_total,
    },
    "modelos_satisfacao": {
        "n_categorias_e_demografia": len(rating_df),
        "r2": float(rating_model.rsquared),
        "r2_ajustado": float(rating_model.rsquared_adj),
        "n_com_tempo_valido": len(time_rating),
        "r2_com_tempo": float(time_model.rsquared),
        "r2_ajustado_com_tempo": float(time_model.rsquared_adj),
    },
}
(OUTPUT_DIR / "02_resumo.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

worst_md = worst_combinations[
    COMBINATION + ["tickets_total", "fechados_validos_tempo", "mediana_h", "p75_h", "p90_h"]
].rename(
    columns={
        "Ticket Channel": "Canal",
        "Ticket Priority": "Prioridade",
        "Ticket Type": "Tipo",
        "tickets_total": "Volume total",
        "fechados_validos_tempo": "N válido",
        "mediana_h": "Mediana (h)",
        "p75_h": "P75 (h)",
        "p90_h": "P90 (h)",
    }
)

segment_exec = (
    segments.sort_values(["dimensao", "mediana_h"], ascending=[True, False])
    .groupby("dimensao", sort=False)
    .head(3)[["dimensao", "segmento", "tickets_total", "fechados_validos_tempo", "mediana_h", "p90_h"]]
    .rename(
        columns={
            "dimensao": "Recorte",
            "segmento": "Segmento",
            "tickets_total": "Volume total",
            "fechados_validos_tempo": "N válido",
            "mediana_h": "Mediana (h)",
            "p90_h": "P90 (h)",
        }
    )
)

sig = rating_results.loc[rating_results["significativo_5pct"]]
largest_effect = rating_results.iloc[rating_results["magnitude_ajustada_pontos"].abs().argmax()]

report = f"""# Diagnóstico operacional do Dataset 1

## Conclusão executiva

A base mostra um problema de mensuração antes de mostrar um problema operacional comparável. Dos **{fmt_int(total)} tickets**, apenas **{fmt_int(valid)} ({fmt_num(pct(valid, total))}%)** permitem medir de forma cronologicamente válida o intervalo entre primeira resposta e resolução. Outros **{fmt_int(invalid)} fechados ({fmt_num(pct(invalid, closed))}% dos fechados)** registram resolução antes da primeira resposta e foram excluídos do cálculo de tempo. Os **{fmt_int(incomplete)} abertos ({fmt_num(pct(incomplete, total))}%)** também foram excluídos porque ainda não têm resolução; tratá-los como zero reduziria artificialmente os tempos.

Nos registros válidos, a resolução leva **{fmt_num(overall['50%'])} horas na mediana**, **{fmt_num(overall['75%'])} horas no P75** e **{fmt_num(overall['90%'])} horas no P90**. A mediana é a medida central principal porque a distribuição tem cauda e valores extremos; a média de **{fmt_num(overall['mean'])} horas** é mantida apenas para auditoria e não representa o ticket típico.

Não apareceu um fator confiável de satisfação a 5% no modelo multivariado (**{len(sig)} de {len(rating_results)} variáveis testadas**). Mesmo a maior amplitude ajustada foi de apenas **{fmt_num(abs(largest_effect['magnitude_ajustada_pontos']), 2)} ponto** na escala de 1 a 5, em **{largest_effect['variavel']}**. O modelo explica **{fmt_num(100 * rating_model.rsquared, 1)}%** da variação das notas; portanto, a base não sustenta priorizar canal, prioridade, tipo, assunto, produto, gênero ou idade como alavanca de satisfação.

Nos **{fmt_int(valid)} tickets válidos**, há **{fmt_num(excess_total, 0)} ticket-horas de tempo corrido excedente acima do P90 do respectivo tipo**. O P90 foi escolhido como limite de cauda para não selecionar metade dos casos por construção. A medida localiza casos extremos; não mede trabalho de agentes nem economia.

## 1. Onde a operação trava

### Critério de inclusão

- Volume: todos os {fmt_int(total)} tickets.
- Tempo: somente os {fmt_int(valid)} fechados com primeira resposta e resolução presentes e resolução igual ou posterior à primeira resposta.
- Excluídos do tempo: {fmt_int(incomplete)} abertos sem desfecho e {fmt_int(invalid)} fechados com duração negativa.
- O arquivo não contém data de abertura do ticket. `Date of Purchase` é data da compra e não foi usada como início do atendimento. Logo, não é possível medir espera até a primeira resposta.

### Segmentos com maior mediana

{md_table(segment_exec)}

A tabela completa, inclusive cobertura e taxa de duração inválida por segmento, está em `02_volume_tempos_segmentos.csv`.

### Combinações com piores tempos

Para reduzir rankings instáveis, o cruzamento foi agregado para **canal × tipo**. Entram na conclusão apenas combinações com pelo menos **{minimum_n} tickets fechados válidos**; as demais permanecem no CSV marcadas como exploratórias e não são ranqueadas aqui.

{md_table(worst_md)}

Esses são pontos de investigação, não prova causal. A base não informa equipe responsável, complexidade, escalonamentos, fila nem esforço ativo.

## 2. O que impacta a satisfação do cliente

Foi ajustada uma regressão multivariada da nota de 1 a 5 com canal, prioridade, tipo, assunto, produto, gênero e idade nos {fmt_int(len(rating_df))} tickets avaliados. Cada variável categórica foi submetida a teste conjunto de Wald com erros robustos HC3. O tempo foi testado à parte nos {fmt_int(len(time_rating))} tickets com cronologia válida, usando `log(1 + horas)` para reduzir a influência da cauda.

{md_table(rating_results[["variavel", "amostra_n", "p_valor", "magnitude_ajustada_pontos", "significativo_5pct"]].rename(columns={"variavel": "Variável", "amostra_n": "N", "p_valor": "p-valor", "magnitude_ajustada_pontos": "Magnitude ajustada (pontos)", "significativo_5pct": "Significativo a 5%"}))}

Conclusão: **não há evidência estatística suficiente de influência** entre as variáveis observadas e a nota. “Não significativo” não prova efeito zero; indica que, com esta base e este desenho, não há sinal confiável para decisão. As magnitudes ajustadas também são pequenas, e o baixo R² mostra que quase toda a variação permanece sem explicação.

## 3. Tempo corrido excedente

Como não existe tempo de trabalho ativo, a medida defensável é de **tempo corrido excedente**. Para cada tipo de ticket, foi usado o P90 dos casos válidos como limite de cauda; somou-se somente a parcela que o ultrapassa: **{fmt_num(excess_total, 0)} ticket-horas (n={fmt_int(valid)})**. O arquivo `02_tempo_corrido_excedente.csv` abre o total por tipo. O método pressupõe que o P90 seja uma referência operacional útil; ele identifica extremos relativos, não prova ineficiência.

Horas simultâneas de tickets diferentes se somam como ticket-horas, e parte do intervalo pode ser espera sem trabalho humano. Por isso, esse total não é convertido em horas de trabalho ou reais.

## O que os dados permitem concluir com segurança

- O volume é de {fmt_int(total)} tickets, distribuível por canal, prioridade e tipo.
- Somente {fmt_int(valid)} tickets sustentam cálculo válido do intervalo entre primeira resposta e resolução.
- Entre esses casos, a mediana é {fmt_num(overall['50%'])} horas e o P90 é {fmt_num(overall['90%'])} horas.
- As combinações de canal × tipo listadas concentram as maiores medianas observadas sob o corte mínimo de {minimum_n} casos válidos; grupos menores são exploratórios.
- As variáveis testadas não apresentam associação estatística confiável com satisfação a 5% neste conjunto.
- Existem {fmt_num(excess_total, 0)} ticket-horas acima do P90 do respectivo tipo (n={fmt_int(valid)}), uma medida de cauda e não de esforço humano.

## O que os dados não permitem concluir

- Tempo até a primeira resposta, porque não há data de abertura do ticket.
- SLA global dos tickets abertos ou tempo final dos casos ainda não encerrados.
- Causalidade: o desenho é observacional e não controla equipe, fila, complexidade ou escalonamento.
- Horas de trabalho evitáveis, capacidade de equipe ou economia real, porque não há esforço ativo nem custos.
- Que melhorar um canal, prioridade ou tipo elevará satisfação; a nota não mostrou sinal estatístico útil.
- Que o texto descreve clientes reais: descrições têm placeholder e os e-mails usam domínios `example.*`.

## Arquivos produzidos

- `02_volume_tempos_segmentos.csv`: volume, cobertura, inválidos e tempos por canal, prioridade e tipo.
- `02_combinacoes_gargalo.csv`: combinações de canal × tipo, status exploratório e critério de elegibilidade do ranking.
- `02_satisfacao_testes.csv`: testes, p-valores e magnitudes ajustadas.
- `02_tempo_corrido_excedente.csv`: ticket-horas acima do P90 por tipo.
- `02_resumo.json`: indicadores principais para auditoria.
"""

(OUTPUT_DIR / "02_diagnostico.md").write_text(report, encoding="utf-8")

print(f"Diagnóstico concluído: {total} tickets; {valid} tempos válidos; {invalid} inválidos.")
print(f"Relatório: {OUTPUT_DIR / '02_diagnostico.md'}")
