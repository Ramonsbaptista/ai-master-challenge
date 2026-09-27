from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "submissions" / "ramon-baptista" / "solution" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

D1_PATH = DATA_DIR / "customer_support_tickets.csv"
D2_PATH = DATA_DIR / "all_tickets_processed_improved_v3.csv"


def pct(n: int | float, d: int | float) -> float:
    return round(100 * n / d, 2) if d else 0.0


def md_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    shown = df if max_rows is None else df.head(max_rows)
    if shown.empty:
        return "_(sem registros)_"
    cols = [str(c) for c in shown.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for row in shown.itertuples(index=False, name=None):
        vals = []
        for value in row:
            if pd.isna(value):
                text = "NA"
            elif isinstance(value, float):
                text = f"{value:.2f}"
            else:
                text = str(value)
            vals.append(text.replace("|", "\\|").replace("\n", " "))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def column_profile(df: pd.DataFrame, dataset: str) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        s = df[col]
        non_null = s.dropna()
        rows.append(
            {
                "dataset": dataset,
                "coluna": col,
                "dtype": str(s.dtype),
                "linhas": len(s),
                "faltantes": int(s.isna().sum()),
                "faltantes_pct": pct(s.isna().sum(), len(s)),
                "vazios_apos_trim": int(non_null.astype(str).str.strip().eq("").sum()),
                "valores_unicos_incluindo_na": int(s.nunique(dropna=False)),
                "exemplo": "" if non_null.empty else str(non_null.iloc[0])[:120],
            }
        )
    return pd.DataFrame(rows)


def value_counts_table(df: pd.DataFrame, columns: list[str], dataset: str) -> pd.DataFrame:
    frames = []
    for col in columns:
        counts = df[col].fillna("<FALTANTE>").astype(str).value_counts(dropna=False)
        frames.append(
            pd.DataFrame(
                {
                    "dataset": dataset,
                    "coluna": col,
                    "valor": counts.index,
                    "quantidade": counts.values,
                    "percentual": [pct(x, len(df)) for x in counts.values],
                }
            )
        )
    return pd.concat(frames, ignore_index=True)


def numeric_profile(df: pd.DataFrame, columns: list[str], dataset: str) -> pd.DataFrame:
    rows = []
    for col in columns:
        s = pd.to_numeric(df[col], errors="coerce")
        q = s.describe(percentiles=[0.25, 0.5, 0.75])
        rows.append(
            {
                "dataset": dataset,
                "coluna": col,
                "contagem": int(q.get("count", 0)),
                "media": q.get("mean"),
                "desvio_padrao": q.get("std"),
                "minimo": q.get("min"),
                "p25": q.get("25%"),
                "mediana": q.get("50%"),
                "p75": q.get("75%"),
                "maximo": q.get("max"),
            }
        )
    return pd.DataFrame(rows)


def normalize_text(s: pd.Series) -> pd.Series:
    return (
        s.fillna("")
        .astype(str)
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )


# Leitura única de cada fonte. keep_default_na preserva a semântica usual de ausências.
d1 = pd.read_csv(D1_PATH, low_memory=False)
d2 = pd.read_csv(D2_PATH, low_memory=False)

# Conversões usadas apenas na análise; os arquivos-fonte não são alterados.
date_cols = ["Date of Purchase", "First Response Time", "Time to Resolution"]
date_parsed = {col: pd.to_datetime(d1[col], errors="coerce") for col in date_cols}

profiles = pd.concat([column_profile(d1, "dataset_1"), column_profile(d2, "dataset_2")], ignore_index=True)
profiles.to_csv(OUTPUT_DIR / "01_perfil_colunas.csv", index=False, encoding="utf-8-sig")

d1_cat_cols = [
    "Customer Gender", "Product Purchased", "Ticket Type", "Ticket Subject",
    "Ticket Status", "Ticket Priority", "Ticket Channel", "Customer Satisfaction Rating",
]
d2_cat_cols = ["Topic_group"]
distributions = pd.concat(
    [value_counts_table(d1, d1_cat_cols, "dataset_1"), value_counts_table(d2, d2_cat_cols, "dataset_2")],
    ignore_index=True,
)
distributions.to_csv(OUTPUT_DIR / "01_distribuicoes_categoricas.csv", index=False, encoding="utf-8-sig")

numeric = numeric_profile(d1, ["Customer Age", "Customer Satisfaction Rating"], "dataset_1")
numeric.to_csv(OUTPUT_DIR / "01_resumo_numerico.csv", index=False, encoding="utf-8-sig")

# Duplicatas e consistência do Dataset 1.
d1_exact_dups = int(d1.duplicated(keep=False).sum())
d1_exact_extra = int(d1.duplicated().sum())
d1_id_dups = int(d1["Ticket ID"].duplicated(keep=False).sum())
d1_id_extra = int(d1["Ticket ID"].duplicated().sum())
d1_desc_norm = normalize_text(d1["Ticket Description"])
d1_desc_dup_rows = int(d1_desc_norm[d1_desc_norm.ne("")].duplicated(keep=False).sum())
d1_desc_dup_extra = int(d1_desc_norm[d1_desc_norm.ne("")].duplicated().sum())
d1_email_valid = d1["Customer Email"].fillna("").astype(str).str.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
d1_example_domain = d1["Customer Email"].fillna("").astype(str).str.lower().str.endswith("@example.com")
d1_reserved_domain = d1["Customer Email"].fillna("").astype(str).str.lower().str.endswith(("@example.com", "@example.net", "@example.org"))
d1_bad_age = pd.to_numeric(d1["Customer Age"], errors="coerce").notna() & ~pd.to_numeric(d1["Customer Age"], errors="coerce").between(0, 120)
d1_bad_rating = pd.to_numeric(d1["Customer Satisfaction Rating"], errors="coerce").notna() & ~pd.to_numeric(d1["Customer Satisfaction Rating"], errors="coerce").between(1, 5)
d1_bad_dates = {col: int(d1[col].notna().sum() - date_parsed[col].notna().sum()) for col in date_cols}
d1_response_before_purchase = int((date_parsed["First Response Time"] < date_parsed["Date of Purchase"]).sum())
d1_resolution_before_response = int((date_parsed["Time to Resolution"] < date_parsed["First Response Time"]).sum())
d1_placeholder_desc = int(d1["Ticket Description"].fillna("").astype(str).str.contains(r"\{[^{}]+\}", regex=True).sum())
d1_placeholder_res = int(d1["Resolution"].fillna("").astype(str).str.contains(r"\{[^{}]+\}", regex=True).sum())

status_missing = (
    d1.groupby("Ticket Status", dropna=False)[["Resolution", "First Response Time", "Time to Resolution", "Customer Satisfaction Rating"]]
    .agg(lambda s: int(s.isna().sum()))
    .reset_index()
)
status_counts = d1["Ticket Status"].value_counts(dropna=False).rename_axis("Ticket Status").reset_index(name="tickets")
status_missing = status_counts.merge(status_missing, on="Ticket Status", how="left")
status_missing.to_csv(OUTPUT_DIR / "01_faltantes_por_status_dataset1.csv", index=False, encoding="utf-8-sig")

# Duplicatas, conflitos e texto do Dataset 2.
d2_doc_norm = normalize_text(d2["Document"])
d2_exact_dups = int(d2.duplicated(keep=False).sum())
d2_exact_extra = int(d2.duplicated().sum())
d2_doc_dup_rows = int(d2_doc_norm[d2_doc_norm.ne("")].duplicated(keep=False).sum())
d2_doc_dup_extra = int(d2_doc_norm[d2_doc_norm.ne("")].duplicated().sum())
d2_label_conflicts = (
    pd.DataFrame({"documento_normalizado": d2_doc_norm, "rotulo": d2["Topic_group"]})
    .query("documento_normalizado != ''")
    .groupby("documento_normalizado")["rotulo"]
    .nunique(dropna=False)
)
d2_conflicting_unique_docs = int((d2_label_conflicts > 1).sum())
d2_conflict_doc_set = set(d2_label_conflicts[d2_label_conflicts > 1].index)
d2_conflicting_rows = int(d2_doc_norm.isin(d2_conflict_doc_set).sum())
d2_words = d2["Document"].fillna("").astype(str).str.split().str.len()
d2_chars = d2["Document"].fillna("").astype(str).str.len()
d2_empty_after_trim = int(d2_doc_norm.eq("").sum())

dup_examples = (
    pd.DataFrame({"Document": d2["Document"], "Topic_group": d2["Topic_group"], "documento_normalizado": d2_doc_norm})
    .loc[d2_doc_norm.ne("") & d2_doc_norm.duplicated(keep=False)]
    .sort_values("documento_normalizado")
)
dup_examples.to_csv(OUTPUT_DIR / "01_duplicatas_textuais_dataset2.csv", index=False, encoding="utf-8-sig")

date_summary = pd.DataFrame(
    [
        {
            "coluna": col,
            "validos": int(parsed.notna().sum()),
            "invalidos_nao_faltantes": d1_bad_dates[col],
            "minimo": parsed.min(),
            "maximo": parsed.max(),
        }
        for col, parsed in date_parsed.items()
    ]
)
date_summary.to_csv(OUTPUT_DIR / "01_resumo_datas_dataset1.csv", index=False, encoding="utf-8-sig")

summary = {
    "dataset_1": {
        "arquivo": str(D1_PATH.relative_to(ROOT)), "linhas": len(d1), "colunas": len(d1.columns),
        "duplicatas_exatas_linhas_envolvidas": d1_exact_dups, "duplicatas_exatas_excedentes": d1_exact_extra,
        "ids_duplicados_linhas_envolvidas": d1_id_dups, "ids_duplicados_excedentes": d1_id_extra,
        "descricoes_duplicadas_linhas_envolvidas": d1_desc_dup_rows, "descricoes_duplicadas_excedentes": d1_desc_dup_extra,
        "emails_formato_invalido": int((~d1_email_valid).sum()), "emails_example_com": int(d1_example_domain.sum()),
        "emails_dominio_reservado_example": int(d1_reserved_domain.sum()),
        "idades_fora_0_120": int(d1_bad_age.sum()), "ratings_fora_1_5": int(d1_bad_rating.sum()),
        "datas_invalidas_nao_faltantes": d1_bad_dates,
        "resposta_antes_da_compra": d1_response_before_purchase,
        "resolucao_antes_da_resposta": d1_resolution_before_response,
        "descricao_com_placeholder": d1_placeholder_desc, "resolucao_com_placeholder": d1_placeholder_res,
    },
    "dataset_2": {
        "arquivo": str(D2_PATH.relative_to(ROOT)), "linhas": len(d2), "colunas": len(d2.columns),
        "duplicatas_exatas_linhas_envolvidas": d2_exact_dups, "duplicatas_exatas_excedentes": d2_exact_extra,
        "documentos_duplicados_linhas_envolvidas": d2_doc_dup_rows, "documentos_duplicados_excedentes": d2_doc_dup_extra,
        "documentos_unicos_com_rotulos_conflitantes": d2_conflicting_unique_docs,
        "linhas_em_conflitos_de_rotulo": d2_conflicting_rows, "documentos_vazios_apos_trim": d2_empty_after_trim,
        "palavras_documento": {k: round(float(v), 2) for k, v in d2_words.describe().to_dict().items()},
        "caracteres_documento": {k: round(float(v), 2) for k, v in d2_chars.describe().to_dict().items()},
    },
}
(OUTPUT_DIR / "01_resumo.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

d1_missing = profiles.query("dataset == 'dataset_1'")[["coluna", "faltantes", "faltantes_pct", "valores_unicos_incluindo_na"]]
d2_missing = profiles.query("dataset == 'dataset_2'")[["coluna", "faltantes", "faltantes_pct", "valores_unicos_incluindo_na"]]
d1_dist = distributions.query("dataset == 'dataset_1'")
d2_dist = distributions.query("dataset == 'dataset_2'")

report = f"""# Exploração dos datasets — etapa 2

## Escopo e separação metodológica

Os datasets foram analisados separadamente. O Dataset 2 é a única fonte indicada para treinar e medir o classificador de tickets internos. O Dataset 1 serve apenas ao diagnóstico operacional de suporte ao consumidor, com sua taxonomia própria. Não foi feita fusão de rótulos, correspondência registro a registro ou criação de uma taxonomia comum.

## Dataset 1 — suporte ao consumidor

Arquivo: `{D1_PATH.relative_to(ROOT)}`. Contém **{len(d1):,} linhas e {len(d1.columns)} colunas**: identificador do ticket, dados demográficos e de contato, produto e data de compra, tipo/assunto do chamado, descrição, status, resolução, prioridade, canal, tempos e satisfação.

### Faltantes e cardinalidade

{md_table(d1_missing)}

### Distribuições categóricas

{md_table(d1_dist)}

### Variáveis numéricas

{md_table(numeric)}

### Datas

{md_table(date_summary)}

### Faltantes por status

{md_table(status_missing)}

### Duplicatas e qualidade

- Há **{d1_exact_extra:,} linhas excedentes exatamente duplicadas** ({d1_exact_dups:,} linhas envolvidas) e **{d1_id_extra:,} IDs excedentes duplicados** ({d1_id_dups:,} linhas envolvidas).
- Após normalizar caixa e espaços, há **{d1_desc_dup_extra:,} descrições excedentes repetidas**, envolvendo **{d1_desc_dup_rows:,} linhas**. Isso limita qualquer interpretação da descrição como relato espontâneo independente.
- **{int(d1_reserved_domain.sum()):,} de {len(d1):,} e-mails ({pct(d1_reserved_domain.sum(), len(d1)):.2f}%)** usam os domínios reservados `example.com`, `example.net` ou `example.org` (desses, **{int(d1_example_domain.sum()):,}** são `example.com`); **{int((~d1_email_valid).sum()):,}** não passam numa validação sintática simples. Os contatos, portanto, não devem ser tratados como contatos reais.
- Existem **{d1_placeholder_desc:,} descrições** e **{d1_placeholder_res:,} resoluções** com placeholders literais entre chaves (por exemplo, `{{product_purchased}}`), evidência de texto template não totalmente interpolado.
- Foram encontrados **{int(d1_bad_age.sum()):,} valores de idade fora de 0–120**, **{int(d1_bad_rating.sum()):,} avaliações preenchidas fora de 1–5**, **{sum(d1_bad_dates.values()):,} datas preenchidas mas não parseáveis**, **{d1_response_before_purchase:,} primeiras respostas anteriores à compra** e **{d1_resolution_before_response:,} resoluções anteriores à primeira resposta**.
- A tabela “faltantes por status” mostra se resolução, tempos e satisfação ausentes são estruturais ao ciclo do ticket ou falhas aleatórias; isso deve ser considerado antes de calcular SLAs ou satisfação.

## Dataset 2 — tickets internos de TI

Arquivo: `{D2_PATH.relative_to(ROOT)}`. Contém **{len(d2):,} linhas e {len(d2.columns)} colunas**: `Document` (texto já processado) e `Topic_group` (rótulo supervisionado).

### Faltantes e cardinalidade

{md_table(d2_missing)}

### Distribuição dos rótulos

{md_table(d2_dist)}

### Comprimento do texto processado

{md_table(pd.DataFrame([
    {"unidade": "palavras", **{k: round(float(v), 2) for k, v in d2_words.describe().to_dict().items()}},
    {"unidade": "caracteres", **{k: round(float(v), 2) for k, v in d2_chars.describe().to_dict().items()}},
]))}

### Duplicatas e qualidade

- Não foram encontradas linhas exatamente duplicadas (**{d2_exact_extra:,} excedentes; {d2_exact_dups:,} envolvidas**).
- Não foram encontrados documentos repetidos após normalizar caixa e espaços (**{d2_doc_dup_extra:,} excedentes; {d2_doc_dup_rows:,} linhas envolvidas**). Portanto, não há evidência desse tipo específico de vazamento no arquivo atual.
- Não foram encontrados textos normalizados com mais de um rótulo (**{d2_conflicting_unique_docs:,} textos; {d2_conflicting_rows:,} linhas afetadas**). Isso não prova que toda anotação esteja correta; apenas afasta conflitos diretamente observáveis entre textos idênticos.
- Há **{d2_empty_after_trim:,} documentos vazios após remover espaços**. Esses registros não carregam sinal textual utilizável.
- O campo `Document` já está fortemente processado (minúsculas/termos separados, sem o ticket bruto nem metadados operacionais). Assim, a análise mede o corpus entregue, não a qualidade ou fidelidade do texto original.

## O que os dados permitem concluir

### Dataset 1

- Descrever volume e composição dos tickets pelas categorias existentes: produto, tipo, assunto, prioridade, canal, status, demografia e satisfação registrada.
- Quantificar faltantes e verificar como eles se distribuem por status.
- Medir intervalos de tempo entre compra, primeira resposta e resolução nos registros em que ambas as datas necessárias existem, ressalvadas as inconsistências apontadas.
- Identificar associações descritivas dentro desta amostra, como diferenças de satisfação ou tempo por produto/canal/tipo. Associação não implica causalidade.

### Dataset 2

- Medir o desbalanceamento das oito classes internas e construir uma avaliação estratificada do classificador.
- Treinar um classificador para **esses oito rótulos**, usando o texto processado disponível.
- Definir uma divisão estratificada de treino e teste; no arquivo atual, não há textos normalizados repetidos que exijam agrupamento especial.
- Comparar modelos sob uma mesma política de validação e métricas adequadas ao desbalanceamento (por exemplo, macro-F1 e métricas por classe).

## O que os dados não permitem concluir

### Dataset 1

- Não permitem inferir desempenho de um classificador para os rótulos do Dataset 2, nem mapear tipos de consumidor para classes internas de TI.
- Não permitem afirmar representatividade de uma população/empresa, tendência temporal real ou causalidade sem informação sobre amostragem, origem e processo de geração.
- Não permitem tratar e-mails como contatos reais; todos usam um dos domínios reservados `example.com`, `example.net` ou `example.org`.
- Não permitem calcular SLA global sem viés ignorando os tempos faltantes e sua relação com status.
- Não permitem assumir que descrições/resoluções são relatos humanos independentes, devido a templates, placeholders e repetições.

### Dataset 2

- Não permitem avaliar atendimento, SLA, resolução, satisfação, prioridade, canal, cliente ou evolução temporal: essas colunas não existem.
- Não permitem medir generalização para chamados de consumidor, para taxonomias diferentes ou para texto bruto fora do pré-processamento fornecido.
- Não permitem concluir que todos os rótulos são corretos; duplicatas conflitantes mostram ambiguidade/inconsistência observável.
- Não permitem estimar desempenho honesto com divisão aleatória ingênua se textos repetidos cruzarem treino e teste.
- Não permitem explicar por que um ticket ocorreu ou inferir relações causais; o dataset contém apenas texto processado e rótulo.

## Arquivos gerados

- `01_relatorio_exploracao.md`: relatório principal.
- `01_resumo.json`: indicadores principais em formato estruturado.
- `01_perfil_colunas.csv`: faltantes, cardinalidade e exemplos de todas as colunas.
- `01_distribuicoes_categoricas.csv`: distribuições completas das categorias relevantes.
- `01_resumo_numerico.csv`: estatísticas numéricas do Dataset 1.
- `01_resumo_datas_dataset1.csv`: validade e intervalos das datas.
- `01_faltantes_por_status_dataset1.csv`: faltantes operacionais por status.
- `01_duplicatas_textuais_dataset2.csv`: linhas repetidas do corpus para auditoria.
"""
(OUTPUT_DIR / "01_relatorio_exploracao.md").write_text(report, encoding="utf-8")

print(f"Exploração concluída: {len(d1):,} linhas no Dataset 1 e {len(d2):,} no Dataset 2.")
print(f"Saídas gravadas em: {OUTPUT_DIR}")
