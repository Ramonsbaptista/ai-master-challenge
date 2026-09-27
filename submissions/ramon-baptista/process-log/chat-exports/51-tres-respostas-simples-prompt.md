Auditoria do Claude Code sobre o bloco "As três perguntas do diretor de operações", aprovada pelo Ramon. Refaça as três respostas. Faça sozinho, sem agentes paralelos. Regras do AGENTS.md valem. Só texto; PROIBIDO alterar números, modelo ou código.

## Problemas

1. Linguagem técnica demais para um diretor: "testes conjuntos de Wald", "regressão multivariada", "P90", fórmula no meio da frase. O tom aprovado do README é frase curta, sem jargão, cena concreta.
2. "Onde perdemos tempo" aponta "Chat × cancelamento, 7,32 h (n=75)" como o fluxo mais lento. Isso contradiz o próprio diagnóstico: 49,3% dos tickets fechados têm resolução antes da primeira resposta (n=2.769), a distribuição sugere horários sorteados, não há horário de abertura, e a diferença para a mediana geral (~6,3 h) é de cerca de 1 hora, sem teste mostrando que não é acaso. Ranquear canais com esses horários é afirmar um gargalo que os dados não sustentam.

## Formato de cada resposta (máximo 4 linhas)
- 1 frase com a resposta direta;
- 1 número principal, com n;
- 1 frase com o que fazer;
- o método e as ressalvas técnicas só no link para o detalhe.

## Direção do conteúdo (confira cada número no arquivo de origem antes de usar)
- **Onde perdemos tempo?** Os horários da base não permitem apontar um gargalo por canal ou tipo com segurança (use o dado que prova isso). O que se vê com clareza é o volume sem resolução (confira o percentual publicado, ~67%, e o n). O primeiro passo é registrar abertura, filas, escalonamentos e esforço ativo.
- **O que impacta a satisfação?** Nenhum dos 8 fatores testados explica a nota (use o número). A pesquisa atual não mede o que precisa; o primeiro passo é redesenhar a pesquisa e ligá-la aos eventos do atendimento.
- **Quanto desperdiçamos?** O que foi medido: tempo corrido excedente (381 ticket-horas acima do limite de cauda de cada tipo, n=1.404), explicado em palavras simples. O ganho financeiro é cenário, não ROI: faixa de R$ 16,9 mil a R$ 94,0 mil de benefício bruto, sob premissas. O primeiro passo é medir esforço ativo e custos para virar ROI.

Não use "P90", "p-valor", "Wald", "regressão" nem fórmulas no bloco; troque por palavras ("os 10% mais demorados", "nenhum sinal acima do acaso"). Se for indispensável, deixe no detalhe linkado.

Se o item "1. Hoje, a operação ainda não tem um relógio confiável" dos Findings ainda repetir o bloco, ajuste para ser o detalhe da primeira resposta.

Ao final, em até 12 linhas: o bloco novo na íntegra e a origem de cada número (arquivo).
