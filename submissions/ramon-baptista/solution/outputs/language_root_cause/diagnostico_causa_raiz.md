# Diagnóstico de causa raiz — queda EN→PT do TF-IDF + regressão logística

## Resultado executivo

No teste congelado balanceado (n=800; método: 100 tickets por classe, textos pareados por `record_id`), o macro-F1 foi 0.857 em EN e 0.415 em PT. A queda pareada foi 0.442 (IC95% 0.405 a 0.479; método: bootstrap pareado percentil com 5000 reamostragens, escolhido porque macro-F1 não tem variância analítica simples; pressupõe tickets independentes e pares EN/PT corretos).

A causa raiz observada é quebra de representação: o modelo foi treinado em vocabulário inglês e só pode usar features PT que já existam nesse vocabulário. A cobertura lexical micro caiu de 99.5% (33736/33920 ocorrências; n=800 textos) para 28.8% (9851/34244; n=800). A cobertura de uni+bigramas caiu de 85.0% para 17.2% (mesmo método e n=800).

Em PT, vetores vazios: 8/800 (1.0%); quase vazios por nnz≤2: 106/800 (13.2%); quase vazios por cobertura de features≤5.0%: 34/800 (4.2%). Os dois critérios são diagnósticos predefinidos e reportados separadamente; não foram escolhidos para maximizar o efeito.

## O que sobrevive e quanto explica

O contrafactual com somente unigramas idênticos no par EN–PT e presentes no vocabulário obteve macro-F1 0.442 (n=800); removendo esses termos do PT, o macro-F1 foi 0.038 (n=800), contra 0.415 no PT completo (n=800). Método: ablação pareada, sem retreino; como remover tokens também desfaz bigramas, isto demonstra mecanismo, mas não identifica efeito causal isolado de cada palavra.

Os termos sobreviventes com maior contribuição positiva para previsões corretas estão em `surviving_terms_pt.csv`. A contribuição é `TF-IDF × coeficiente` da classe prevista, somada apenas quando positiva; isso distingue frequência de influência real. A categoria “idêntico_no_par_EN_PT” é objetiva; “curto_sigla_ou_ambíguo” não é chamado automaticamente de sigla para evitar classificação subjetiva.

## Para onde vão os erros

Com vetor exatamente zero, os interceptos escolhem **Hardware** com score 0.270 (método: softmax dos interceptos; n conceitual=1 vetor zero). Em PT, essa classe recebeu 475/800 previsões (59.4%); entre vetores com nnz≤2, recebeu 79/106 (74.5%). A classe mais prevista em PT foi Hardware: 475/800 (59.4%).

Métricas PT por classe (método one-vs-rest; n=100 positivos por classe e n=800 total; fórmulas mostradas):

- Access (n=100): precisão = VP/(VP+FP) = 15/(15+6) = 0.714; recall = VP/(VP+FN) = 15/(15+85) = 0.150; especificidade = VN/(VN+FP) = 694/(694+6) = 0.991; F1 = 2×precisão×recall/(precisão+recall) = 0.248. VP=15, FP=6, FN=85, VN=694.
- Administrative rights (n=100): precisão = VP/(VP+FP) = 44/(44+16) = 0.733; recall = VP/(VP+FN) = 44/(44+56) = 0.440; especificidade = VN/(VN+FP) = 684/(684+16) = 0.977; F1 = 2×precisão×recall/(precisão+recall) = 0.550. VP=44, FP=16, FN=56, VN=684.
- HR Support (n=100): precisão = VP/(VP+FP) = 30/(30+29) = 0.508; recall = VP/(VP+FN) = 30/(30+70) = 0.300; especificidade = VN/(VN+FP) = 671/(671+29) = 0.959; F1 = 2×precisão×recall/(precisão+recall) = 0.377. VP=30, FP=29, FN=70, VN=671.
- Hardware (n=100): precisão = VP/(VP+FP) = 91/(91+384) = 0.192; recall = VP/(VP+FN) = 91/(91+9) = 0.910; especificidade = VN/(VN+FP) = 316/(316+384) = 0.451; F1 = 2×precisão×recall/(precisão+recall) = 0.317. VP=91, FP=384, FN=9, VN=316.
- Internal Project (n=100): precisão = VP/(VP+FP) = 37/(37+4) = 0.902; recall = VP/(VP+FN) = 37/(37+63) = 0.370; especificidade = VN/(VN+FP) = 696/(696+4) = 0.994; F1 = 2×precisão×recall/(precisão+recall) = 0.525. VP=37, FP=4, FN=63, VN=696.
- Miscellaneous (n=100): precisão = VP/(VP+FP) = 26/(26+34) = 0.433; recall = VP/(VP+FN) = 26/(26+74) = 0.260; especificidade = VN/(VN+FP) = 666/(666+34) = 0.951; F1 = 2×precisão×recall/(precisão+recall) = 0.325. VP=26, FP=34, FN=74, VN=666.
- Purchase (n=100): precisão = VP/(VP+FP) = 75/(75+1) = 0.987; recall = VP/(VP+FN) = 75/(75+25) = 0.750; especificidade = VN/(VN+FP) = 699/(699+1) = 0.999; F1 = 2×precisão×recall/(precisão+recall) = 0.852. VP=75, FP=1, FN=25, VN=699.
- Storage (n=100): precisão = VP/(VP+FP) = 7/(7+1) = 0.875; recall = VP/(VP+FN) = 7/(7+93) = 0.070; especificidade = VN/(VN+FP) = 699/(699+1) = 0.999; F1 = 2×precisão×recall/(precisão+recall) = 0.130. VP=7, FP=1, FN=93, VN=699.

Agregados PT (n=800): acurácia = soma da diagonal/n = 325/800 = 0.406; macro-F1 = média simples dos oito F1 por classe = 0.415; F1 ponderado pela quantidade real de cada classe = 0.415. Como há 100 casos por classe, macro e ponderado coincidem. A matriz passou nas checagens de linhas e total.

## Score e roteamento

O score máximo médio mudou de 0.786 em EN (n=800) para 0.568 em PT (n=800); diferença PT−EN média -0.218, mediana -0.193, p=3.19e-74 (Wilcoxon pareado bicaudal; probabilidades são limitadas e assimétricas; pressupõe pares independentes e distribuição aproximadamente simétrica das diferenças).

Aplicando sem ajuste os cortes congelados do manifesto (baixa < 0.522; alta ≥ 0.540), a faixa alta em PT reteve 359/800 (44.9%) com acurácia 65.2% (n=359; método: acertos/aceitos). Entre todos os 475 erros PT, 125 (26.3%) ficaram na faixa alta. Portanto, o score não é um detector confiável de idioma/OOV; erros de alta confiança são o risco principal.

## Idioma versus tradução automática

Os efeitos não são separáveis nesta amostra: todos os textos PT são simultaneamente outro idioma e produto de um único tradutor PT-PT. Qualquer percentual atribuído a cada causa seria não identificável.

Experimento sem tocar no teste: usar somente os 800 pares de validação e produzir EN original, EN→PT→EN, PT-PT automático, PT-PT revisado por humano e PT-BR revisado por humano. Comparar macro-F1 por bootstrap pareado (5.000 reamostragens, IC95%) e acerto por McNemar. EN original versus backtranslation estima dano de reescrita mantendo inglês; PT automático versus PT humano estima artefato do tradutor dentro de PT; PT-PT versus PT-BR estima variante regional. EN versus PT humano continua sendo efeito combinado de idioma e formulação, devendo ser reportado como tal, inclusive com interação.

## Correções candidatas e recomendação

1. **Traduzir PT→EN antes do classificador atual.** Prós: preserva modelo leve, implantação rápida, reutiliza limiares após nova calibração. Contras: latência/custo e falhas de tradução; dependência externa ou de um modelo local. Custo na máquina: mínimo se API; alto se tradutor neural local. Medição: escolher tradutor e novos cortes apenas na validação traduzida (n=800), com macro-F1 pareado, latência p50/p95, custo por ticket, cobertura e acurácia por faixa; teste congelado uma única vez após decisão.
2. **Treinar com dados traduzidos para PT.** Prós: inferência TF-IDF continua barata e transparente; adapta vocabulário PT. Contras: duplica/expande matriz esparsa, herda artefatos do tradutor e pode degradar EN. Custo: RAM moderada; o corpus duplicado teria n=66.970 exemplos antes da validação, como premissa derivada de 2×33.485 linhas de treino do manifesto, e até 100 mil features conforme configuração atual. Medição: traduzir somente treino, comparar EN/PT na validação (n=800 por idioma) e exigir não inferioridade EN mais ganho PT; recalibrar cortes apenas na validação.
3. **Embeddings multilíngues (`paraphrase-multilingual-MiniLM-L12-v2`) + classificador linear.** Prós: representação compartilhada entre idiomas e benchmark direto com o concorrente. Contras: exige baixar modelo, inferência mais lenta e armazenamento/cache dos vetores; menor explicabilidade lexical. Custo: nesta etapa não medido; precisa disponibilizar o modelo e dependências, sem instalação agora. Para pouca RAM, gerar embeddings em lotes, salvar `float32`/memmap e treinar apenas a cabeça linear. Medição: congelar o encoder; selecionar cabeça/regularização e cortes só na validação; registrar macro-F1 EN/PT, RAM de pico, tamanho, latência p50/p95 e roteamento.
4. **Combinação de modelos.** Prós: TF-IDF pode preservar excelência EN e embeddings/ tradução cobrir PT; fallback por idioma reduz regressão. Contras: duas pipelines, calibração e monitoramento mais complexos; combinação por score bruto é inválida sem calibração comum. Custo: soma dos componentes. Medição: na validação, comparar roteamento determinístico por idioma, stacking out-of-fold ou média de probabilidades calibradas; exigir n≥100 por faixa e classe antes de conclusões.

**Recomendação:** prototipar primeiro embeddings multilíngues com encoder congelado e cabeça linear, em lotes, porque ataca diretamente a causa raiz (espaço lexical monolíngue) e é a comparação mais limpa com o concorrente. Manter o TF-IDF para EN numa combinação por detecção de idioma apenas se a validação mostrar que o encoder perde desempenho EN. Em paralelo, PT→EN é o baseline de baixo esforço e deve ser medido antes da decisão final; ele pode vencer em custo/qualidade se houver uma API já aprovada. Nenhuma alternativa deve ser escolhida ou calibrada no teste congelado.

## Premissas e limites

- “Quase vazio” usa dois cortes diagnósticos declarados (nnz≤2; cobertura≤5%), não uma definição operacional de qualidade.
- O score é `predict_proba` máximo não calibrado, conforme o manifesto; não é probabilidade validada fora do inglês.
- A identificação de termos sobreviventes é mecânica pelo vocabulário; nomes de produto não foram inferidos por uma lista externa.
- Os 800 tickets são uma amostra balanceada (100 por classe), portanto proporções de classes previstas descrevem este teste e não prevalência de produção.
