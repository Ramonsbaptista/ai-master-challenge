Aprovado. Construa o protótipo na versão enxuta que acordamos, com os seus dois ajustes.

ESCOPO FECHADO:
- Classificador TF-IDF + regressão logística, treinado e avaliado só na Base 2.
- Baseline ingênuo (classe majoritária) para comparação.
- Split estratificado treino / validação / teste, com seed fixa. Hiperparâmetros escolhidos só na validação; teste avaliado uma única vez.
- Conjunto de teste CONGELADO: salvar os identificadores exatos dos registros do teste, a ordem das classes e as predições esperadas. O avaliador nunca refaz o split.
- Modelo final salvo e versionado, com um único manifesto legível: hashes SHA-256 dos dados, do split e do modelo; versões de Python e das bibliotecas; classes em ordem; matriz e métricas esperadas.
- Métricas conforme a seção "Métricas de classificação" do AGENTS.md: matriz de confusão, VP/FP/FN/VN por classe, fórmulas substituídas, precisão, recall, especificidade e F1 por classe, macro-F1, F1 ponderado e acurácia, e todas as checagens de consistência — o script para com erro se qualquer uma falhar.
- Roteamento em três faixas a partir do score, com cortes escolhidos na VALIDAÇÃO, nunca no teste. Reportar cobertura, taxa de acerto e volume de cada faixa, com n. Se o score não estiver calibrado, chame de "score do modelo".
- requirements.txt com versões exatas.
- run.ps1 e run.sh: verificam versão suportada do Python, criam o ambiente, instalam e abrem o menu. Mensagem clara se faltar Python, apontando o Colab.
- Menu de terminal: 1 classificar um ticket digitado, 2 reproduzir a avaliação, 3 informações do modelo, 0 sair.
- Mensagens de erro no formato causa / como corrigir / diagnóstico, só para as falhas previsíveis.
- Um teste de ponta a ponta.
- Notebook do Colab fino: só instala o projeto e chama o mesmo código. Se o tempo apertar, deixe o notebook por último.
- README da solução com setup e o comando exato para Windows e para macOS/Linux.

RESTRIÇÕES:
- Tudo dentro de submissions/ramon-baptista/solution/. Não altere diagnostico.md nem proposta-instrumentacao.md.
- Os dados brutos estão em C:\Users\Ramon\g4-ai-master\data\. Copie para dentro da solução apenas o que o protótipo precisa.
- Caminhos sempre relativos à raiz do projeto, com pathlib.
- Pouca RAM: matriz TF-IDF esparsa, nunca .toarray().
- Regras do AGENTS.md valem integralmente.

AO TERMINAR, entregue:
1. A matriz de confusão e a tabela por classe, com os números de origem e as fórmulas.
2. Macro-F1, F1 ponderado e acurácia do modelo e do baseline, lado a lado.
3. Os cortes das três faixas e o desempenho de cada uma.
4. O resultado do teste de ponta a ponta.
5. O que ficou pendente, se algo ficou.

Não diga que testou algo que não testou.
