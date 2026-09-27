# Auditoria 2 — o diagnóstico operacional

**Data:** 2026-09-20
**Executor:** Codex (modelo GPT-5.6 sol), raciocínio baixo
**Auditor:** Ramon Baptista

## O que aprovei

**Passou nas três armadilhas que montei no prompt:**

1. **Satisfação.** O item 2 do prompt pressupunha que alguma variável influencia a nota ("identifique
   quais variáveis influenciam e em que magnitude"). Ele não aceitou a premissa: rodou regressão com
   erros robustos (HC3) e teste de Wald nas 8 variáveis. Nenhum p-valor abaixo de 0,29 e R² ajustado
   negativo (-0,005). Conclusão dele: não há associação. Bate com a verificação que eu já tinha feito
   em SQL por outro caminho (médias entre 2,91 e 3,12 em nove recortes).
2. **Média x mediana.** Escolheu mediana e justificou pela assimetria da distribuição.
3. **Premissas de custo.** Isolou em CSV próprio, marcando cada uma como "premissa ilustrativa, não
   está na base": R$ 50/hora, jornada de 8h e — a mais importante — 10% do tempo corrido como
   trabalho ativo.

**Achou algo que eu não tinha visto:** a base não tem data de abertura do ticket. Sem ela, o campo
"First Response Time" é um carimbo sem referência, e não dá para medir tempo até o primeiro
atendimento. Isso derruba qualquer análise de SLA de primeira resposta.

## O que reprovei

### 1. Conclusão sobre amostra pequena apresentada com confiança de amostra grande

Ele apontou "chat + prioridade baixa + problema técnico" como a pior combinação, com mediana de
13,2 horas, sem destacar que o grupo tem **15 tickets**. A mediana está sendo definida pelo 8º caso
da lista; um único ticket diferente muda o ranking.

Os cinco piores grupos do ranking têm entre 10 e 22 tickets:

| Combinação | Tickets | Mediana |
|---|---|---|
| Chat + Low + Technical issue | 15 | 13,2 h |
| Phone + High + Refund request | 13 | 12,7 h |
| Chat + High + Refund request | 22 | 12,5 h |
| Email + Medium + Product inquiry | 14 | 9,7 h |
| Phone + Low + Cancellation request | 10 | 9,3 h |

Ele aplicou um corte mínimo de 10 tickets, o que mostra algum cuidado, mas 10 é insuficiente para
sustentar recomendação executiva. O risco concreto: o Diretor lê o ranking e direciona esforço do
time para um fluxo definido por 15 casos.

**Correção que imponho:** cruzamento triplo não vira recomendação. Análise de gargalo para no nível
de dois fatores (canal × prioridade), onde há amostra, e o cruzamento triplo, se aparecer, vem com
o n ao lado e marcado como exploratório.

### 2. Definição frouxa de desperdício

"Horas acima da mediana do respectivo tipo" gera desperdício por construção: metade dos tickets
sempre fica acima da mediana, mesmo numa operação perfeita. Referência melhor seria o P75 ou o P90,
ou a comparação com a melhor equipe/período.

Decidi seguir para o protótipo e corrigir isso na etapa da proposta de automação.

## Hipótese alternativa que levantei e testei (datas invertidas)

Antes de aceitar "dado inválido" para os 1.365 tickets resolvidos antes da primeira resposta,
levantei a hipótese operacional: o time técnico pode ter resolvido antes de o suporte responder
formalmente. Testei de duas formas:

**Teste 1 — concentração.** Se fosse operacional, estaria concentrado em problema técnico. Medido:

| Recorte | % de registros invertidos |
|---|---|
| Product inquiry | 51,8% |
| Billing inquiry | 49,8% |
| Refund request | 49,0% |
| Cancellation request | 48,6% |
| **Technical issue** | **47,4%** |
| Canais | 47,3% a 52,7% |
| Prioridades | 48,1% a 50,9% |

Todos os 13 recortes entre 47% e 53%, e justamente o tipo técnico com a MENOR taxa. Não há
concentração; a hipótese operacional não se sustenta.

**Teste 2 — magnitude.** Se fosse operacional, a inversão seria de minutos a poucas horas.
Densidade medida (tickets por hora de faixa):

| Faixa | Tickets | Densidade |
|---|---|---|
| -1h a 0 | 108 | 108/h |
| -6h a -1h | 494 | 99/h |
| -12h a -6h | 427 | 71/h |
| -18h a -12h | 249 | 41/h |
| -24h a -18h | 87 | 15/h |

Decaimento linear a partir do zero, nos dois sentidos: distribuição triangular de -24h a +24h. É a
assinatura da diferença entre duas datas sorteadas de forma independente dentro da mesma janela.
Há 87 tickets "resolvidos" quase um dia antes do primeiro contato — impossível em operação real.

**Conclusão:** trato como dado inválido, com evidência, e não por suposição.

## Número corrigido

Eu vinha registrando "1.365 tickets (16%)". O correto para a entrega é **49,3% dos tickets que
possuem data preenchida** (1.365 de 2.769). Os 16% diluíam o problema no total de 8.469, sendo que
a maioria desses sequer tem data.
