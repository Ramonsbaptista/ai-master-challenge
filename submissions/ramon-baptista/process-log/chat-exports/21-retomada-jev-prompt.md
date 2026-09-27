A execução anterior falhou. Relato do que aconteceu, para você decidir como seguir.

## O bloqueio

Você tentou instalar `argostranslate` para traduzir offline. O pip falhou duas vezes com "Permission denied", nos dois caminhos que tentou:

  C:\Users\Ramon\g4-ai-master\.launcher-test-temp\pip-temp\pip-unpack-.../argostranslate-1.11.0-py3-none-any.whl.metadata
  C:\Users\Ramon\AppData\Local\Temp\pip-unpack-.../argostranslate-1.11.0-py3-none-any.whl.metadata

A causa é o sandbox em que você roda: ele bloqueia a escrita nas pastas temporárias que o pip usa no Windows. Não é falta de permissão do usuário nem falta de espaço.

Cada tentativa consumiu cerca de 32 minutos antes de falhar; as duas juntas passaram de uma hora. Depois disso a execução encerrou com erro.

## O que sobreviveu

- `solution/scripts/04_avaliar_jev.py` está escrito.
- `solution/outputs/jev_evaluation/translation_cache.json` existe, com 223 KB.
- Você registrou ter chegado a 150 de 1.600 chamadas e anotou: "o gargalo é CPU, não rede".

## O que eu preciso de você

A decisão do caminho da tradução é sua, é arquitetura. Escolha e me diga o que vai fazer. Algumas possibilidades, e você pode propor outra:

- eu instalo o pacote que você pedir, fora do sandbox, e você retoma;
- você mesmo traduz os textos, sem depender de pacote;
- você usa outro mecanismo de tradução;
- você reduz a amostra, se o gargalo de CPU inviabilizar o tamanho atual — mas então justifique o novo n e o que ele permite ou não concluir.

Antes de rodar de novo, me responda em no máximo 10 linhas:
1. qual caminho de tradução você escolheu e por quê;
2. se mantém o n de 100 por classe por idioma, e qual o tempo estimado de execução;
3. o que você vai fazer com o cache de tradução e com as 150 chamadas já feitas — reaproveitar ou descartar, e por quê;
4. o que preciso instalar ou liberar, se for o caso.

Não comece a execução longa antes dessa resposta. Regras do AGENTS.md valem. Responda em português.
