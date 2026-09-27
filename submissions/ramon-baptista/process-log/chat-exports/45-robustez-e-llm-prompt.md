Decisão do Ramon: duas entregas nesta rodada, nesta ordem. Faça sozinho, sem agentes paralelos. Regras do AGENTS.md valem integralmente.

PROIBIDO: alterar o modelo, o split, o teste congelado, os limiares ou os números já publicados. Os 20 testes atuais devem continuar passando.

## Parte 1 — Teste de robustez com texto livre (experimento novo)

Pergunta do Ramon: "quem garante que o avaliador só irá testar o modelo com exemplos prontos? Em produção, nenhum cliente abre o ticket falando exatamente a mesma frase que o banco de dados tem."

1. Conjunto novo de tickets escritos do zero, que NÃO vêm da Base 2, em grupos:
   - reformulações de assuntos das 8 filas;
   - erros de digitação;
   - textos curtos;
   - fora do escopo (reembolso, cobrança, reclamação, entrega, cancelamento etc.);
   - mistura de idiomas.
   Pelo menos 100 casos por grupo. Cada caso tem o rótulo esperado ("fila X" ou "fora do escopo → pessoa") definido ANTES de rodar o modelo, salvo em arquivo com hash. Declare com honestidade que os textos foram gerados por IA (premissa e limitação: não são tickets reais).
2. Métrica principal: taxa de "direto para a fila errada" (encaminhado automaticamente e errado), por grupo, com n e intervalo de confiança (diga qual método e por quê). Reporte também: direto e certo; desviado para pessoa. A acurácia é secundária.
3. Prova extra com a Base 1 (tickets de clientes, outro domínio, fora das 8 filas de TI): qual proporção o sistema mandaria direto com confiança? Lembre que 100% das descrições têm o placeholder `{product_purchased}`; decida como tratar e declare.
4. Se o erro confiante for alto, proponha uma correção (ex.: camada "fora do escopo" que manda para uma pessoa). Regras:
   - calibre em uma parte e meça em outra parte nunca usada para calibrar (ou use a validação); nunca ajuste olhando o resultado final;
   - meça o custo: quanto a cobertura automática cai no teste congelado;
   - NÃO ative a correção no produto. Deixe-a implementada atrás de uma opção desligada, documentada, para o Ramon decidir.
5. Um script único em `solution/scripts/` e saídas em `solution/outputs/robustez/`, com um relatório `.md` em linguagem de negócio primeiro e os números com cálculo depois.

## Parte 2 — Seção "Onde entra LLM e onde não" (só documento)

Escreva essa seção no README e em `solution/proposta-instrumentacao.md` (ou no documento da proposta mais adequado), com a arquitetura que você mesmo defendeu na rodada 44:
- TF-IDF/classificador supervisionado: classificar e escolher a fila;
- regras fixas: o que precisa ser exato (proteção de idioma, kill switch, e a camada fora do escopo se for aprovada);
- LLM assistida (proposta, não construída): resumir, extrair informações, redigir resposta sugerida, sempre com revisão humana; e ticket em português, junto com os embeddings multilíngues;
- humano obrigatório: segurança, fraude, jurídico, financeiro, casos ambíguos, ações irreversíveis.

Inclua uma tabela: etapa | ferramenta | por quê | evidência. Use as evidências reais: o Jev (LLM) foi testado e reprovado na triagem (38,6% em inglês, n=800, contra 86,51% do TF-IDF), e os resultados da Parte 1. Correção do Claude: o score do sistema NÃO é calibrado; não escreva que ele "produz confiança calibrável" sem dizer que hoje não está calibrado.

Linguagem: mesmo tom do README aprovado (frases curtas, sem jargão, cena concreta). Frase-resumo: "LLM para compreensão e assistência; modelo supervisionado para classificação; regras para decisões determinísticas; humano para risco e julgamento."

## Ao final, em até 25 linhas
Os números reais por grupo (com n), a Base 1, a correção proposta com seu custo, o que foi escrito no README e na proposta, o resultado da suíte de testes e as pendências. Se algo for bloqueado pelo sandbox, não contorne: diga o comando exato para o Claude rodar.
