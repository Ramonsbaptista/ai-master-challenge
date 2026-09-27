Antes de construir o classificador, duas questões.

## 1. Rigor no cálculo das métricas

A métrica principal é o macro-F1, mas a qualidade dele depende inteiramente de precisão e recall estarem calculados corretamente, e a acurácia também vai aparecer na entrega. Por isso, quero que você seja extremamente criterioso ao calcular acurácia, precisão, recall (sensibilidade) e F1, e que explique claramente como chega a cada número, para sermos capazes de identificar erros.

Acrescentei uma seção no AGENTS.md ("Métricas de classificação — mostrar o cálculo, não só o resultado"). Leia e confirme como vai aplicá-la. Em especial:
- como vai apresentar VP, FP, FN e VN de um problema com 8 classes, onde "positivo" e "negativo" dependem da classe que está sendo avaliada;
- como vai garantir que as somas da matriz batem com o n de cada classe e do conjunto de teste;
- como vai deixar claro, na entrega, a diferença entre macro-F1, F1 ponderado e acurácia, e quando cada um engana.

## 2. Viabilidade de orquestrar o projeto no n8n

Eu domino n8n e uso em produção. Usando TF-IDF + regressão logística como classificador, é tecnicamente viável orquestrar o projeto via n8n em vez de 100% em Python?

Quero uma análise honesta, separando as partes do projeto:
- o TREINAMENTO e a AVALIAÇÃO do modelo (split, ajuste, matriz de confusão, métricas);
- a INFERÊNCIA (classificar um ticket novo e devolver categoria + confiança);
- o ROTEAMENTO (decidir entre as três faixas com base na confiança e no tipo);
- a COLETA das métricas de instrumentação (CSAT, CES, IQS, NPS) e o modo sombra.

Para cada parte, diga: dá para fazer no n8n? Com qual nó ou abordagem (Code node em JavaScript, Code node em Python, chamada HTTP para um serviço Python, etc.)? Quais os riscos e limitações concretas? E o que ganho ou perco em reprodutibilidade, auditabilidade e manutenção em relação a fazer em Python puro?

Considere também:
- o avaliador do G4 precisa conseguir rodar a solução seguindo as instruções de setup;
- a máquina atual tem pouca RAM;
- o protótipo precisa rodar com os dados reais, não com três exemplos.

Termine com uma recomendação clara: qual arquitetura você propõe e por quê, e o que eu mostraria na entrevista para aproveitar o meu domínio de n8n sem comprometer a reprodutibilidade.

Não escreva código nem crie arquivos nesta etapa. Regras do AGENTS.md valem. Responda em português.
