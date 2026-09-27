Decisão do Ramon: o visual da interface ficou bom, mas o TEXTO ainda fala como estatístico. Aplique à interface os mesmos princípios de copywriting usados no README e nas propostas, e torne tudo muito mais didático — principalmente a tela "Avaliação reproduzível" (métricas por classe, fórmulas, matriz de confusão).

Objetivo: transformar os diferenciais técnicos em comunicação que mostre o diferencial do Ramon, segundo o que o avaliador do G4 avalia.

Faça sozinho, sem agentes paralelos. Regras do AGENTS.md valem.

LEIA ANTES DE ESCREVER (só leitura):
- `bastidores/readme/04-conhecimento-propostas.md` — princípios de copywriting.
- `bastidores/readme/05-auditoria-ramon-v1.md` — os 13 julgamentos do Ramon sobre linguagem (frases curtas, sem jargão, "métrica" e não "instrumento", achado = cena concreta).
- `bastidores/concorrentes/avaliacoes-do-g4.md` — o que o avaliador elogiou de fato: auditoria antes de calcular, validação em conjunto separado com abstenção, guardrails e kill switch, reprodutibilidade, separar medido de premissa.
- `submissions/ramon-baptista/README.md` — o tom aprovado ("esse ficou muito bom").

PRINCÍPIOS PARA CADA BLOCO DA INTERFACE:
- Primeiro "o que isso significa para a operação", depois o número, depois (expansível) o cálculo.
- Cada métrica ganha uma explicação em 1 frase com exemplo concreto de ticket. Ex.: precisão de Equipamentos = "de cada 100 tickets que a IA mandou para Equipamentos, 86 eram mesmo de Equipamentos"; recall = "de cada 100 tickets que eram de Equipamentos, a IA encontrou 84".
- VP/FP/FN/VN traduzidos em linguagem de fila ("mandou certo", "mandou para a fila errada", "deixou escapar", "corretamente não mandou").
- Matriz de confusão: explicar como ler (linha = assunto real, coluna = para onde a IA mandou, diagonal = acertos), destacar a diagonal com cor e apontar as 2–3 confusões mais frequentes em linguagem de negócio (números vindos do retorno real, não digitados).
- Por que cada verificação existe e qual risco ela evita (ex.: hashes = "prova de que ninguém trocou o modelo ou o teste depois de ver o resultado").
- Mostrar explicitamente o diferencial: teste congelado nunca usado para treinar; a IA para quando não tem segurança; números reproduzíveis por qualquer pessoa com um clique.
- Continuar honesto: score não calibrado, 86% não é 100%, português não validado. Nada de exagero de marketing.

AJUSTES VISUAIS JÁ APROVADOS:
1. Remover o logo "G4" (não usar marca de terceiros); ícone neutro + "Triagem assistida".
2. Números no padrão brasileiro: 86,40%, 7.176, 0,92.
3. Conclusão para o gestor com 3 cartões grandes: acerto geral, % automatizado, acerto na faixa automatizada; e 1 frase do que acontece com o resto. Valores vindos do retorno real.
4. Detalhes (fórmulas, matriz, hashes) fechados por padrão, abrindo ao clicar.
5. Variável `TICKET_CLASSIFIER_KILL_SWITCH` numa nota pequena no rodapé do cartão.
6. Tela Classificar: score com vírgula; quando o idioma é recusado, não exibir "categoria sugerida".
7. Tela Classificar também ganha a explicação didática: o que significa "vai direto" vs "vai para uma pessoa", e o que o score quer dizer.

PROIBIDO: alterar modelo, split, teste congelado, limiares, métricas ou qualquer número. Nenhum número digitado à mão no template — tudo vem do núcleo.

TESTES: os 14 atuais devem passar; ajuste só o que for texto. Se o pip ou algo for bloqueado pelo sandbox, não contorne — diga o comando para o Claude rodar.

AO FINAL, em até 20 linhas: o que mudou em cada tela, 3 exemplos de antes→depois de texto, resultado real dos testes, pendências.
