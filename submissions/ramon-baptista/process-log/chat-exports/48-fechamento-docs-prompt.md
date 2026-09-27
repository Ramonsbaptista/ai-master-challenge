Rodada de fechamento aprovada pelo Ramon. Três tarefas, só texto. Faça sozinho, sem agentes paralelos. Regras do AGENTS.md valem. PROIBIDO alterar modelo, split, teste congelado, limiares, números oficiais ou a lógica do sistema. A barreira "fora do escopo" continua DESLIGADA.

## 1. README principal (`submissions/ramon-baptista/README.md`)

Na rodada 47 você atualizou `solution/README.md` e a proposta, mas não o README principal, que é o primeiro arquivo que o avaliador lê. Leve para ele, de forma curta e no tom já aprovado (frases curtas, cena concreta, sem jargão):
- a robustez fora do domínio: Base 1 como prova principal (2.718/8.469 = 32,1% iriam direto; tickets reais, outro domínio; mede exposição, não acurácia); os sintéticos como complemento exploratório (erro entre os encaminhados de 40% a 61% contra 6,15% no teste oficial);
- a barreira "fora do escopo": testada, reduziu só 67/2.718 = 2,5% na Base 1, não generaliza, por isso ficou desligada. Apresente como decisão, não como falha;
- a conclusão: o modelo é bom no domínio em que foi treinado e se desvia fora dele; por isso a proposta começa em modo sombra e só automatiza depois de medir, com os critérios go/no-go;
- confira se a seção "Onde entra LLM e onde não" está no README principal e coerente com a proposta;
- a interface: `run.ps1`/`run.sh` abrem a interface no navegador; `--cli` mantém o terminal; as 3 telas em uma linha cada; a demo online será publicada pelo Ramon no Render (deixe um marcador `[LINK DA DEMO]` e o aviso de que o plano gratuito pode levar cerca de 1 minuto para acordar na primeira visita);
- simplifique a coluna de premissas da tabela de cenários econômicos, hoje ilegível (`10%/55%/35%; 12/20/35→4/16/35; R$ 40`): escreva as premissas em palavras, uma por linha ou em nota abaixo da tabela, sem mudar nenhum número.
Mantenha o README enxuto: se precisar de detalhe, link para o relatório.

## 2. Tela de Avaliação (textos)

Duas frases a corrigir nos templates:
- o título "O resultado se repetiu sem mudar a prova" é confuso; troque por algo como "A IA acertou 86 de cada 100 tickets que nunca tinha visto" (número vindo do núcleo, não digitado);
- "avaliado em tickets separados antes do treinamento" sugere que a avaliação veio antes do treino; o correto é "tickets separados antes do treino e nunca usados nele".
Se a tela de Avaliação ou de Controles tiver espaço natural, mencione em uma frase o limite fora do domínio, com link para o relatório de robustez.

## 3. Process log (`process-log/diario.md`)

Acrescente as entradas das rodadas 40 a 48, no mesmo formato das anteriores, com o que foi pedido, o que o GPT fez, o que o Claude auditou e o que o Ramon decidiu. Pontos obrigatórios:
- 40–42: a interface (decisão do Ramon: "uma empresa do nível do G4 não vai aceitar um sistema cru desse jeito no terminal"), o desenho, a construção e a reescrita didática dos textos;
- 43: o bug de inicialização (navegador abria antes do servidor) e a demo online preparada;
- 44: a pergunta do Ramon sobre LLM, em palavras dele;
- 45–47: a pergunta do Ramon sobre texto livre em produção, em palavras dele; o defeito encontrado pelo Claude (frases repetidas com sufixo numérico: 12 a 16 frases distintas em três grupos); a refação; a barreira que parecia 0% nos sintéticos e só pegou 2,5% na Base 1.
Arquivos das rodadas estão em `process-log/chat-exports/40-*` a `48-*`.

## Testes
Rode a suíte completa ao final (script único) e reporte a saída real. Se algum teste depender dos textos alterados, ajuste só o texto esperado.

## Ao final, em até 20 linhas
O que mudou em cada arquivo, o texto novo do título da Avaliação, e o resultado real dos testes.
