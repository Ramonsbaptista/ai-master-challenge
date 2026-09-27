Nova prioridade. O diagnóstico do Jev foi abortado.

O problema: o nosso classificador TF-IDF + regressão logística cai de 85,7% de macro-F1 em inglês para 41,5% em português (mesmos 800 tickets do teste congelado, traduzidos por máquina para português europeu). O concorrente mais forte, usando embeddings multilíngues (paraphrase-multilingual-MiniLM-L12-v2), declarou 0,865 em inglês e 0,784 no modelo servido para português. Precisamos da CAUSA RAIZ da nossa queda, com evidência, antes de propor qualquer correção.

Materiais:
- Modelo: submissions/ramon-baptista/solution/artifacts/model-v1.0.0.joblib
- Amostra bilíngue: submissions/ramon-baptista/solution/outputs/jev_evaluation/sample_bilingual.csv (colunas Document e Document_pt; partições validation e test)
- Resultados por classe: .../jev_evaluation/per_class_metrics.csv e analysis.json

Investigue e meça, com n e método em cada número:
1. Cobertura de vocabulário: que fração dos tokens de cada texto em português existe no vocabulário do TF-IDF? Compare com o inglês. Quantos textos em português ficam com vetor TF-IDF vazio ou quase vazio?
2. O que sobrevive: quais palavras em português ainda casam com o vocabulário (palavras iguais nas duas línguas, siglas, nomes de produto)? Isso explica os 41,5% que restaram?
3. Para onde vão os erros: a matriz de confusão em português concentra previsões numa classe (a classe "padrão" que o modelo escolhe quando não reconhece nada)?
4. O score do modelo em português: ele cai junto, a ponto de o roteamento mandar esses tickets para humano? Ou o modelo erra com score alto — o que seria perigoso?
5. Quanto da queda é do idioma e quanto é da tradução automática (português europeu, frases reescritas)? Proponha como separar os dois efeitos.

Depois, proponha as correções possíveis, com prós, contras, custo na nossa máquina (pouca RAM) e como mediríamos cada uma sem tocar o teste congelado. Inclua pelo menos: traduzir a entrada para inglês antes de classificar; treinar com dados traduzidos; embeddings multilíngues (como o concorrente); e a combinação de modelos. Recomende uma.

Não mude o modelo atual nem o teste congelado. Scripts em submissions/ramon-baptista/solution/scripts/, saídas em .../outputs/. Um script único. Não rode nada que exija instalar pacotes ou baixar modelos grandes nesta etapa — se a correção recomendada exigir, diga o que precisa e eu providencio. Regras do AGENTS.md valem. Responda em português.
