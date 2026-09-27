Rodada de correções aprovada pelo Ramon, a partir de uma avaliação independente (uma sessão nova do Codex atuando como avaliador final, só leitura). A avaliação completa está em `bastidores/avaliador-final/02-avaliacao-final.md` — leia antes. Faça sozinho, sem agentes paralelos. Regras do AGENTS.md valem. PROIBIDO alterar modelo, split, teste congelado, limiares ou números de origem. A barreira "fora do escopo" continua desligada.

Corrija os itens abaixo (numeração da seção 4 da avaliação). Confira cada achado no arquivo antes de corrigir; se discordar de algum, diga por quê em vez de corrigir.

1. **Acurácia × macro-F1:** onde estiver "acurácia de 86,51%" (README, proposta e qualquer outro lugar), corrigir para "acurácia de 86,40% (6.200/7.176); macro-F1 de 86,51%". Busque em todos os .md, templates e no diário.
2. **Interface: cobertura efetiva.** Na tela de Avaliação, separar "faixa alta do modelo" (5.527) de "encaminhamento efetivo após as barreiras" (5.510, com os 17 barrados explicados), e mostrar o acerto também sobre os efetivamente automatizados. Os números vêm do núcleo, nunca digitados. Ajuste testes se preciso.
3. **Idioma sem promessa absoluta:** trocar "sempre vai para uma pessoa" por "quando a barreira detecta idioma não validado, envia para uma pessoa", citando a falha observada (14 de 812 textos em português não detectados na validação) em README, `controls.html`, `classify.html` e onde mais aparecer.
4. **Diagnóstico final:** remover "rascunho"/"a ser lapidado" de `solution/diagnostico.md`; trocar n=2.769 por n=1.404 onde se fala de tempos válidos; retirar generalizações categóricas da abertura ("a nota não varia com nada", "numa operação real, cliente que espera mais avalia pior").
5. **Regra do CSAT:** unificar com a decisão da auditoria 03 (evento `Resolved`, separado do fechamento administrativo, janela declarada como premissa) em `proposta-instrumentacao.md`.
6. **"Tickets reais":** onde a Base 1 aparecer como "tickets reais de clientes", trocar por "tickets da Base 1, de outro domínio (atendimento ao consumidor)"; nunca "reais".
7. **Construído × proposto:** no README, após a seção de abordagem, uma tabela curta "Construído agora" × "Proposto para o piloto". Marque as faixas A/B/C do diagnóstico e a LLM assistida como processo futuro.
8. **Respostas brutas no PR:** converta para Markdown, em `process-log/chat-exports/`, só as interações decisivas (ambiente limpo, português/causa raiz, robustez e refação, barreira na Base 1, correções do avaliador final): o prompt e a resposta final do Codex, sem os diffs e logs gigantes. Não altere o `.gitignore` para incluir os .txt brutos inteiros. Nenhuma chave pode entrar (o Claude Code fará a varredura depois).
10. **Cenário financeiro único:** 924,5 horas em todos os documentos (valor do cálculo sem arredondamento intermediário); confira as demais linhas dos cenários com a mesma convenção.

Também: remova a pasta temporária `solution/outputs/tmpk7caw19o` se ela for lixo de execução (confira antes).

Não faça o item 9 (prints): o Claude Code cuida dele.

Rode a suíte completa ao final e reporte a saída real.

Ao final, em até 20 linhas: o que mudou por item, qualquer discordância, e o resultado dos testes.
