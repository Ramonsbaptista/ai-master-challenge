Revisei seu plano. Aprovado, com uma correção e uma restrição.

CORREÇÃO — item 3 do seu plano ("construir uma taxonomia comum entre métricas operacionais e textos"):

Está reprovado e contradiz o seu próprio item 2. Os dois datasets usam conjuntos de rótulos incompatíveis:

- Dataset 2 (TI interna): Hardware 13.617, HR Support 10.915, Access 7.125, Miscellaneous 7.060, Storage 2.777, Purchase 2.464, Internal Project 2.119, Administrative rights 1.760.
- Dataset 1 (consumidor final): Refund request 1.752, Technical issue 1.747, Cancellation request 1.695, Product inquiry 1.641, Billing inquiry 1.634. Os produtos são Canon EOS, GoPro Hero, Nest Thermostat, Amazon Echo.

Quatro categorias do dataset 2 (HR Support, Access, Internal Project, Administrative rights = 21.919 tickets, 46% do total) não têm equivalente no dataset 1. E Refund/Cancellation request (3.447 tickets do dataset 1) não existem no dataset 2. Fundir as listas geraria um classificador treinado em chamados corporativos aplicado a reclamações de consumidor: respostas confiantes e erradas.

RESTRIÇÃO que passa a valer:
- Dataset 2 = treinar e medir o classificador (é o único com rótulo confiável).
- Dataset 1 = diagnóstico operacional, com as categorias próprias dele.
- A ponte entre os dois é metodológica, nunca registro a registro nem por fusão de rótulos. Se você quiser relacionar os dois de alguma forma, apresente a proposta antes de executar.

PRÓXIMA ETAPA — execute agora o item 2 do seu plano (exploração dos dois datasets) e pare ao final.

Entregue:
1. O que cada dataset contém de fato: distribuições das colunas relevantes, faltantes, duplicatas.
2. Problemas de qualidade que você encontrou. Seja específico e mostre o número que sustenta cada afirmação.
3. Uma lista do que estes dados PERMITEM concluir e do que NÃO permitem.

Salve o script em submissions/ramon-baptista/solution/scripts/ e as saídas em submissions/ramon-baptista/solution/outputs/. Responda em português.

RESTRIÇÃO DE AMBIENTE (importante): esta máquina tem pouca RAM e iniciar o Python custa ~17 segundos por chamada. Não execute vários comandos Python pequenos. Escreva UM script único, completo, em submissions/ramon-baptista/solution/scripts/01_exploracao.py, que faça toda a exploração de uma vez e grave os resultados em arquivos dentro de submissions/ramon-baptista/solution/outputs/. Rode esse script UMA vez. Se precisar corrigir, corrija o script e rode de novo, sem comandos avulsos.
