# Resposta final do Codex — correções do avaliador final

- Item 1: corrigi a métrica para acurácia de **86,40% (6.200/7.176; n=7.176)** e macro-F1 de **86,51% (n=7.176)** no README e na proposta.
- Item 2: a Avaliação agora separa faixa alta (**5.527/7.176**) de encaminhamento efetivo (**5.510/7.176**) e deriva do núcleo os 7 bloqueios por tamanho, 10 por idioma e o acerto efetivo de **5.174/5.510 = 93,90% (n=5.510)**.
- Item 3: removi a promessa absoluta de idioma e registrei os **14/812 escapes em PT (n=812)** no README e nas duas telas.
- Item 4: finalizei o diagnóstico, troquei tempos válidos para **n=1.404** e retirei as duas generalizações categóricas.
- Item 5: unifiquei o CSAT no evento `Resolved`, separado de `Closed`, com janela de 15 minutos a 2 horas declarada como premissa operacional.
- Item 6: a Base 1 passou a ser descrita como outro domínio, de atendimento ao consumidor, sem chamá-la de “real”.
- Item 7: o README ganhou a tabela “Construído agora” × “Proposto para o piloto”; A/B/C e LLM assistida ficaram marcadas como futuras.
- Item 8: preservei em Markdown os cinco prompts e apenas as respostas finais decisivas; os `.txt` brutos continuam ignorados e nenhuma chave foi copiada.
- Item 9: não executado, conforme solicitado.
- Item 10: unifiquei **924,5 h**; a memória de cálculo confirma 423,4 h, 924,5 h e 1.566,8 h sem arredondamento intermediário.
- Não houve discordância com os achados.
- `tmpk7caw19o` tem perfil de temporário, mas o sandbox/ACL bloqueou inspeção e remoção; ele permanece e isso está explicitamente reportado.
- Suíte completa no estado final: `Ran 21 tests in 17.181s` e `OK` (n=21), incluindo o novo teste da cobertura efetiva.

Prompt correspondente: [`52-correcoes-avaliador-final-prompt.md`](52-correcoes-avaliador-final-prompt.md).
