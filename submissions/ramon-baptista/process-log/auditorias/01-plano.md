# Auditoria 1 — o plano de ataque do executor

**Data:** 2026-09-19
**Executor:** Codex (modelo GPT-5.6 sol), raciocínio baixo
**Auditor:** Ramon Baptista

## O que ele propôs

Plano em 10 linhas, antes de escrever qualquer código. Resumo dos pontos relevantes:

- Auditar os dois datasets separadamente (esquema, duplicatas, distribuições).
- Não inventar join registro a registro, por não haver chave comum.
- **"Construir uma taxonomia comum entre métricas operacionais e textos."**
- Diagnosticar gargalos por canal, prioridade e tipo.
- Quantificar desperdício com premissas rastreáveis.
- Fluxo com triagem por IA, confiança mínima e escalonamento humano.
- Validar com divisão treino/teste, métricas por classe e análise de erros.

## O que aprovei

Percebeu sozinho que os datasets não têm chave comum e se recusou a forçar o cruzamento
registro a registro. Esse é o erro mais comum nesse case, já que o enunciado sugere que
"o poder está no cruzamento". Também trouxe treino/teste e métricas por classe sem eu pedir.

## O que reprovei — a taxonomia comum

Contradiz a própria recusa do join. Taxonomia é o conjunto de rótulos usados para classificar,
e os dois datasets têm conjuntos incompatíveis:

| Dataset 2 (TI interna, 47.837) | Dataset 1 (consumidor final, 29.807) |
|---|---|
| Hardware (13.617), HR Support (10.915), Access (7.125), Miscellaneous (7.060), Storage (2.777), Purchase (2.464), Internal Project (2.119), Administrative rights (1.760) | Refund request (1.752), Technical issue (1.747), Cancellation request (1.695), Product inquiry (1.641), Billing inquiry (1.634) |

Quatro das oito categorias do dataset 2 (HR Support, Access, Internal Project, Administrative
rights = 21.919 tickets, 46% do total) não têm equivalente nenhum no dataset 1, que trata de
clientes que compraram Canon EOS, GoPro e Amazon Echo. E Refund/Cancellation request, 3.447
tickets do dataset 1, não existem no dataset 2.

Fundir as duas listas produziria um classificador treinado para reconhecer pedidos de acesso
corporativo sendo aplicado a pedidos de reembolso de consumidor. O modelo não ficaria sem
resposta: daria respostas confiantes e erradas, porque todo ticket cai em alguma categoria.
É o problema conhecido como *data distribution shift* (domain shift).

## Decisão

Bloqueei apenas este ponto e deixei o restante do plano seguir como está, para observar quais
erros ele comete sozinho. Os demais riscos que identifiquei e decidi não avisar de antemão:

1. Separa treino/teste, mas não menciona um terceiro conjunto para ajuste — risco de ajustar
   olhando o mesmo conjunto em que mede.
2. Não cita baseline simples de comparação — sem isso não dá para saber se o modelo complexo
   compensa.
3. Vai medir satisfação do cliente sem questionar se a coluna tem sinal real.
4. Usa "risco" como critério de automação sem definir custo de erro.

Regra que impus no lugar da taxonomia comum:
- Dataset 2 → treinar e medir o classificador (é o único com rótulo confiável).
- Dataset 1 → diagnóstico operacional, com as categorias próprias dele.
- A ponte entre os dois é metodológica, não registro a registro.
