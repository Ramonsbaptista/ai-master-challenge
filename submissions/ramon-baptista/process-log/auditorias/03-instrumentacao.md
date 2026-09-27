# Auditoria 3 — a proposta de instrumentação

**Data:** 2026-09-22
**Executor:** Codex (modelo GPT-5.6 sol), raciocínio baixo
**Auditor:** Ramon Baptista

## Mudança de método antes desta etapa

Depois de avaliar como o executor vinha lidando com estatística, identifiquei um padrão: ele aplica
bem o método quando o prompt exige, e falha justamente onde não é cobrado. Exemplos das etapas
anteriores: rodou regressão robusta com teste de Wald quando pedi evidência estatística, mas
produziu ranking de gargalo sobre 15 tickets quando pedi apenas "quais combinações concentram os
piores tempos".

Em vez de repetir instruções a cada prompt, criei o arquivo `AGENTS.md` na raiz do projeto, lido
automaticamente pelo executor em toda execução. Ele fixa:

- método escolhido, premissas, fundamento e **n** ao lado de todo número;
- n<30 é exploratório e não vira recomendação; segmentos exigem n≥100;
- teste da métrica que se autoinfla: *qual valor ela produziria numa operação impecável?*;
- nomenclatura correta (tempo corrido excedente ≠ desperdício; benefício bruto ≠ ROI; nota 1–5 em
  faixas ≠ NPS);
- proibição de afirmar verificação não realizada.

Motivo: cada execução do Codex começa sem memória da anterior. Sem o arquivo, a disciplina se perde
a cada nova chamada.

## Resultado: a instrução melhorou a entrega de forma verificável

| Antes do AGENTS.md | Depois |
|---|---|
| "1.365 tickets têm resolução antes da primeira resposta." | "1.365 cronologias inválidas entre 2.769 fechados: 49,3% (n=2.769). Método: resolução anterior à primeira resposta; fundamento: sequência incompatível com o processo." |
| Ranking de gargalo com n=15 sem ressalva | "Resultados com n<30 são exploratórios; métricas por segmento exigem n≥100" aplicado no próprio desenho |
| "Desperdício" para tempo acima da mediana | IQS desenhado explicitamente para não se autoinflar: "tende a 100% por aderência real" |
| R$ 46,2 mil apresentados sem qualificação suficiente | "O valor não é ROI" + lista do que falta descontar |

Também justificou os pisos de amostra com a margem correspondente (n=100 → ±9,8 p.p.; n=400 →
±4,9 p.p., ambos a 95%) e observou que a incerteza do NPS exige bootstrap, por não ser proporção
simples. Recusou converter CSAT em faixas: "seria perda de informação e não a transforma em NPS".

## O que continua reprovado

**1. Os 20% / 65% / 15% continuam carregando o cenário financeiro.** Agora estão marcados como
premissa ilustrativa, o que é honesto, mas as 924,5 horas e os R$ 46,2 mil dependem inteiramente
desses três números inventados. Enquanto a elegibilidade real por etapa não for medida, esse
cenário não deve ocupar posição de destaque na entrega.

**2. Mudança de recomendação sem justificativa.** Na análise das quatro métricas, ele recomendou
disparar o CSAT no evento `Resolved` (não `Closed`), entre 15 minutos e 2 horas depois. No
documento final, passou para "disparo no encerramento, envio até 5 minutos depois". Mudou os dois
parâmetros sem explicar. Adoto a primeira versão, que separa resolução de fechamento administrativo.

**3. Cronograma assume acesso não verificado.** As 8 semanas pressupõem acesso aos sistemas de
ticket para instrumentar eventos, o que o case não menciona. Deve aparecer como dependência
explícita, não como premissa silenciosa.

## Decisão de método adotada

A espinha dorsal da entrega deixa de ser "aqui está a automação que economiza X" e passa a ser:
**a operação não tem instrumento para saber se qualquer automação funcionou; aqui está o que
instrumentar, em que ordem, e qual marco autoriza automatizar o quê.**

Fundamento: automatizar sem baseline pode reduzir custo e piorar a experiência sem que ninguém
perceba. É tratar o paciente sem pedir exame. O executor concordou com a tese e acrescentou um
ponto que incorporei: antes-e-depois sozinho não basta — sem grupo de controle ou implantação
escalonada, o efeito da automação se confunde com sazonalidade, mix de tickets e evolução da
equipe.
