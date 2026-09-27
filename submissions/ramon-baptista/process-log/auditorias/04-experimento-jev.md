# Auditoria 4 — Jev como desafiante, e o problema do português

**Datas:** 2026-09-22 a 2026-09-23
**Desenho do experimento:** Codex (modelo GPT-5.6 sol), executor
**Execução:** script do executor (`solution/scripts/04_avaliar_jev.py`); as etapas bloqueadas pelo
sandbox (tradução e chamadas com controle de ritmo) foram rodadas fora dele, sem alterar o método
**Auditor:** Ramon Baptista

## A pergunta

A empresa opera no Brasil, mas o classificador foi treinado em inglês. Um modelo novo, o Jev
(TypeSafe AI, lançado em 15/09/2026), promete classificação estruturada com nota de confiança.
Duas perguntas: o Jev é melhor que o nosso modelo? E ele resolve o português?

## O desenho

- 800 tickets do teste congelado (100 por classe) e 800 da validação, com os rótulos originais.
- Os mesmos 1.600 textos traduzidos para português por tradutor offline (Argos, en→pt).
- Quatro medições: nosso modelo e o Jev, cada um em inglês e em português — 3.200 chamadas ao Jev.
- O limiar de roteamento do Jev escolhido só na validação; o teste nunca usado para ajuste.
- Estabilidade: 50 tickets repetidos 3 vezes. Textos sem informação: 80 casos ("olá", "ok", ".").
- Comparações com McNemar e bootstrap pareado (5.000 reamostragens).

## Resultado (teste congelado, n = 800)

| | Inglês | Português traduzido | Queda |
|---|---|---|---|
| **Nosso modelo (TF-IDF)** | **85,7%** | 41,5% | −44,2 pontos |
| **Jev** | 38,6% | 36,8% | −1,9 ponto |

*macro-F1*

**Em inglês, o nosso modelo ganha por 47 pontos** (IC 95% de 43 a 51 pontos; McNemar p ≈ 10⁻⁸³).
Em 389 tickets só o nosso modelo acertou; em 27, só o Jev.

**Por que o Jev perde:** ele classifica "a frio", só com a descrição das categorias. O nosso modelo
aprendeu com 33 mil exemplos como esta base rotula os tickets, inclusive categorias com sentido
próprio como "Miscellaneous" e "Internal Project". O Jev não acertou nenhum ticket de
"Administrative rights" (0 de 100) e jogou 269 dos 800 em "Miscellaneous".

**Em português, os dois quebram por motivos opostos.** O nosso modelo cai 44 pontos porque aprendeu
vocabulário em inglês. O Jev praticamente não muda (−1,9 ponto, IC incluindo zero, p = 0,07):
entende português tão bem quanto inglês, mas parte de um nível baixo. Mesmo em português, o nosso
modelo ainda fica à frente (41,5% contra 36,8%).

## Calibração — o motivo decisivo

- Erro de calibração (ECE, 10 faixas) de **0,42**. Confiança média de 0,83 quando acerta e 0,78
  quando erra: a nota praticamente não separa acerto de erro.
- **Nenhum limiar atingiu 90% de acerto na validação.** Cobertura automática possível: **0%**.
- **Os 80 textos sem informação foram todos para "Miscellaneous" com confiança 1,0.** O que era
  suspeita no teste de fumaça (n=5) se confirmou em escala.

A documentação oficial já avisava que a confiança "difere de probabilidade" e que o inglês é o
idioma em que o modelo é melhor. O experimento confirmou as duas coisas nos nossos dados.

## O que o Jev faz bem

- **Estável:** 49 de 50 tickets (98%) com a mesma resposta em 3 chamadas; variação média de
  confiança de 0,03.
- **Rápido:** 0,42 s na mediana, 0,61 s no P95.
- **Barato:** 2,2 milhões de tokens de entrada — cerca de US$ 0,09 no preço de tabela
  (US$ 0,04 por milhão; saída sem preço publicado). Gratuito no período do teste.

## Decisões

1. **O Jev não entra como classificador.** Perde nas duas línguas, e a confiança dele não permite
   automatizar nenhuma faixa.
2. **Português não tem solução medida.** A posição mantida: quando a barreira detectar português,
   encaminhar para pessoa; coletar base rotulada em português (mínimo de 100 por classe); testar embeddings
   multilíngues como próximo candidato.

## Limitações

- O português do experimento é **tradução automática em variante europeia**, não português
  brasileiro de cliente real. O número é referência, não previsão de produção.
- Os critérios das categorias para o Jev foram escritos uma vez, sem ajuste. Descrições melhores
  poderiam melhorar o Jev; mesmo assim, a falta de calibração continuaria impedindo o roteamento.

## Custos de execução que vale registrar

O experimento levou bem mais que o previsto, quase todo o tempo em problema de ambiente, e não de
método: o sandbox do executor bloqueou a instalação e a leitura do tradutor; o plano gratuito do
gateway parava de responder a cada ~29 chamadas em rajada (resolvido com uma chamada a cada 2 s);
a máquina ficou sem memória duas vezes e o processo foi encerrado. O checkpoint gravado a cada
chamada, implementado pelo executor após a primeira falha, foi o que evitou perder o trabalho.
