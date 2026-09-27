# Resposta final do Codex — português e causa raiz

A causa raiz é lexical: o TF-IDF aprendeu principalmente vocabulário em inglês e perde quase toda a representação quando recebe português. Método: diagnóstico pareado nos mesmos 800 tickets, sem retreino e sem tocar no teste congelado.

- Cobertura unigram média: **91,8% em EN contra 22,8% em PT (n=800 pares)**; mediana **93,2% contra 22,9%**. Wilcoxon pareado bicaudal: **n=800, p=3,19×10⁻¹³²**.
- Features TF-IDF não nulas por texto: mediana **143 em EN contra 14 em PT (n=800 pares)**. Em PT, **41/800** vetores ficam vazios e **106/800** têm no máximo duas features.
- Mantendo somente palavras idênticas no par EN–PT e presentes no vocabulário, o macro-F1 ainda é **0,442 (n=800)**; removendo-as dos textos PT, cai para **0,038 (n=800)**, contra **0,415** no PT completo. A ablação também desfaz bigramas, portanto é evidência mecanística, não efeito causal isolado de cada palavra.
- Um vetor zero escolhe Hardware, com score **0,270** pelos interceptos. Hardware recebe **475/800 = 59,4%** das previsões PT, embora represente **100/800 = 12,5%** dos casos reais no desenho balanceado.
- Entre os **106** vetores PT com no máximo duas features, **79/106 = 74,5%** vão para Hardware. Para Hardware: `VP=91`, `FP=384`, `FN=9`, `VN=316`; precisão `91/(91+384)=0,192`, recall `91/(91+9)=0,910`, F1 `=0,317` (n=100 positivos; one-vs-rest sobre n=800).
- Score máximo médio: **0,786 em EN contra 0,568 em PT (n=800 pares)**; diferença PT−EN de **−0,218**, Wilcoxon pareado bicaudal, **n=800, p=3,19×10⁻⁷⁴**.
- Pelos cortes congelados, **441/800 = 55,1%** dos tickets PT iriam para humano; **359/800 = 44,9%** permaneceriam na automação. A faixa alta acerta **234/359 = 65,2%**; dos **475** erros PT, **125/475 = 26,3%** têm score de faixa alta.

Não é possível separar percentualmente idioma e tradução nesta amostra, porque todo texto PT muda simultaneamente de idioma e passa por um único tradutor PT-PT. A recomendação foi prototipar `paraphrase-multilingual-MiniLM-L12-v2` congelado, em lotes `float32`, com cabeça linear; medir PT→EN em paralelo como baseline de baixo esforço. Nenhum pacote ou modelo externo foi instalado.

Prompt correspondente: [`30-causa-raiz-portugues-prompt.md`](30-causa-raiz-portugues-prompt.md).
