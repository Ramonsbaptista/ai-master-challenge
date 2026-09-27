# INTENÇÃO

Executar a etapa 3 do plano: o diagnóstico operacional do Dataset 1, que é a primeira das três entregas obrigatórias do case. O Diretor de Operações precisa saber onde a operação perde tempo e quanto isso custa, com números que sustentem decisão.

# INFORMAÇÃO

## O que já foi estabelecido nas etapas anteriores

Resultado da sua exploração, que eu conferi de forma independente em SQL e confirmei:

- O Dataset 1 tem 8.469 tickets (não os ~30.000 que o enunciado do desafio afirma; o arquivo tem 29.807 linhas porque as descrições contêm quebras de parágrafo).
- 67,3% dos tickets não têm resolução, tempo de resolução nem nota. Isso é estrutural: os 2.769 tickets fechados estão todos completos e nenhum ticket aberto tem esses campos.
- 1.365 tickets (16%) têm tempo de resolução ANTERIOR à primeira resposta — dado inválido.
- 100% das descrições contêm o placeholder {product_purchased} e 100% dos e-mails são de domínio example.*. O conteúdo textual do Dataset 1 é gerado, não real.
- O Dataset 2 está íntegro: 47.837 textos, sem nulos, duplicatas ou rótulos conflitantes. Desbalanceado (Hardware 28,47% até Administrative rights 3,68%). Mediana de 26 palavras.

## Restrições que continuam valendo

- Dataset 2 = treinar e medir o classificador. Dataset 1 = diagnóstico operacional.
- Proibido fundir taxonomias ou cruzar registro a registro.
- Nenhuma afirmação numérica sem código que a produza.
- Ambiente com pouca RAM: um script único por etapa, rodado uma vez. Nada de comandos avulsos.

# INSTRUÇÃO

Produza o diagnóstico operacional do Dataset 1 respondendo às três perguntas do case:

1. ONDE A OPERAÇÃO TRAVA
   - Volume e tempos por canal, prioridade e tipo de ticket.
   - Quais combinações concentram os piores tempos.
   - Decida e justifique quais registros você inclui ou exclui do cálculo de tempo, considerando os 1.365 inválidos e os 67,3% incompletos.
   - Use a medida de tendência central que você julgar correta para esta distribuição, e justifique a escolha.

2. O QUE IMPACTA A SATISFAÇÃO DO CLIENTE
   - Identifique quais variáveis influenciam a nota e em que magnitude.
   - Sustente a resposta com evidência estatística, não com diferença de médias observada a olho.

3. QUANTO SE DESPERDIÇA
   - Quantifique em horas.
   - Se converter em dinheiro, declare cada premissa numa tabela separada (custo/hora, jornada, volume considerado) e deixe claro que são premissas, não dados.

Formato da entrega:
- Script único em submissions/ramon-baptista/solution/scripts/02_diagnostico.py
- Saídas em submissions/ramon-baptista/solution/outputs/
- Um relatório em 02_diagnostico.md escrito para um Diretor de Operações não técnico: conclusão primeiro, número junto, e o detalhe metodológico depois.
- Ao final, liste separadamente: o que estes dados permitem concluir com segurança e o que não permitem.

Pare ao terminar. Eu vou revisar antes de seguir para o protótipo.
