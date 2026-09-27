Rodada 2 de 2 das correções antes do PR. Faça sozinho, sem abrir agentes paralelos (limite de uso curto).

## 1. Kill switch

Um modo global que manda TODO ticket para uma pessoa, ativável por configuração (variável de ambiente ou arquivo de configuração, o que for mais simples e documentável), sem precisar mexer em código. Quando ativo, o menu mostra isso claramente em linguagem de negócio ("Modo de segurança ativo: todos os tickets vão para análise humana"). Documente no README da solução como ligar e desligar, em duas linhas.

## 2. Defeito real encontrado na proteção de idioma (textos curtos)

O Ramon e o Claude testaram tickets reais no modelo:
- "i forgot my password and cannot log in to the vpn" (inglês normal) foi desviado pela proteção de idioma como se não fosse inglês — alarme falso.
- "a tela do meu notebook quebrou e o teclado nao funciona" (português) ESCAPOU da proteção; só foi para pessoa porque o score estava baixo.
A proteção foi calibrada na validação bilíngue, cujos textos são mais longos. Em textos curtos ela erra nos dois sentidos.

Investigue a causa (provavelmente a regra de mínimo de tokens e a cobertura calculada em poucas palavras), corrija de forma que funcione também em textos curtos, e recalibre usando SOMENTE a validação (nunca o teste congelado). Se necessário, crie um pequeno conjunto adicional de textos curtos de validação, marcando-o como tal. Reporte, com n, os erros nos dois sentidos antes e depois.

Também registrado: "the printer on the third floor is jammed and shows an error light" foi para HR Support com score 0,605, na faixa automática. Não corrija o modelo — é um erro esperado dentro dos ~6% da faixa alta —, mas cite-o como exemplo honesto de erro na documentação de limitações da solução.

## 3. Testes dos controles críticos

Hoje há 2 testes. Não persiga quantidade: teste os controles que a narrativa da entrega promete. No mínimo:
- manifesto e hashes: um artefato alterado é detectado e a avaliação se recusa a rodar;
- consistência da matriz: soma das linhas = n de cada classe, soma total = n do teste;
- cortes de roteamento: vêm do manifesto (escolhidos na validação), e casos exatamente no limite caem na faixa certa;
- proteção de idioma: casos curtos e longos, nos dois sentidos, incluindo os três tickets acima;
- kill switch: ativo, nada é encaminhado automaticamente;
- falha segura: entrada vazia ou só espaços vai para pessoa, sem erro técnico.

## 4. Histórico sem guardar o texto do ticket

outputs/classification_history.csv hoje grava o texto inteiro digitado. Numa operação real seria dado de cliente guardado sem necessidade. Grave só o necessário para auditoria: data e hora, um hash do texto, o tamanho, a decisão, a categoria, o score e a faixa. Atualize a documentação.

## Regras

- Não altere o modelo, o split, o teste congelado nem as métricas.
- Rode a suíte completa ao final e reporte o resultado real.
- Regras do AGENTS.md valem.
- Ao terminar, liste em no máximo 15 linhas: o que mudou, quantos testes e o resultado, e os erros da proteção de idioma antes e depois.

Responda em português.
