Uma questão de negócio antes das próximas etapas: a empresa do case opera no Brasil. O sistema precisa entender tickets em português. Mas o classificador foi treinado e avaliado na Base 2, que está em inglês, e não existe nenhuma base rotulada em português no desafio.

Testei com um ticket em português ("o status do pedido está como entregue mas o cliente não recebeu a compra e já se passaram 24 horas") e o sistema mandou para a faixa baixa, com score 0.2754 — correto como decisão de roteamento, mas o sistema simplesmente não entende português.

O conflito: a tese central da entrega é "medir antes de automatizar". Aceitar português sem conseguir medir se o sistema acerta em português contradiria essa tese.

Avalie e recomende. Considere pelo menos estas opções, e acrescente outras se houver:
A) traduzir a entrada do português para o inglês antes de classificar;
B) traduzir a base de treino para português e retreinar;
C) usar um modelo multilíngue (embeddings ou similar);
D) o Jev como desafiante, se ele for multilíngue — verifique na documentação que você já leu;
E) não suportar português nesta entrega e documentar como próximo passo, com o plano de medição pronto.

Para cada opção: como mediríamos a qualidade em português sem ter base rotulada em português? (Uma ideia a avaliar: traduzir uma amostra do teste congelado para português, rodar pelo sistema e comparar o macro-F1 com os 86,51% do inglês. Diga se essa medida é válida, quais vieses ela tem — por exemplo, tradução de máquina não é igual a um cliente real escrevendo — e qual tamanho de amostra seria suficiente.)

Considere também: RAM limitada nesta máquina, reprodutibilidade para o avaliador (que pode rodar offline), custo, e o prazo de 4 a 6 horas do case.

Termine com uma recomendação clara e o que exatamente seria feito. Não escreva código nem crie arquivos. Regras do AGENTS.md valem. Responda em português.
