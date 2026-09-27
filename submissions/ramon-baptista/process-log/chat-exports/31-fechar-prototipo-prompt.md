Prioridade agora: deixar o protótipo pronto para o avaliador. As correções anteriores foram quase todas aplicadas antes de a sessão cair, mas há pendências e um defeito novo.

## Defeito novo — acentuação corrompida (grave)

Em src/ticket_classifier/cli.py a saída aparece como "DecisÃ£o", "Por quÃª", "seguranÃ§a". O avaliador é executivo, não técnico, e veria esse texto quebrado. Corrija em TODOS os arquivos da solução (código, README, notebook, mensagens de erro). Garanta que os arquivos estejam salvos em UTF-8 e que a saída no terminal do Windows (PowerShell) exiba os acentos corretamente — teste isso de verdade, não suponha.

## Proteção para português (decisão já tomada)

O diagnóstico da causa raiz mostrou que, em português, o modelo reconhece só 28,8% das palavras, e que 26,3% dos erros em português cairiam na faixa automática alta. A decisão é: detectar quando o ticket não está em inglês e mandar para uma pessoa, com uma explicação simples ("O sistema ainda não foi validado para textos em português; um atendente vai analisar"). Implemente sem instalar pacotes novos (uma heurística simples e documentada é aceitável — por exemplo, a fração de palavras do texto reconhecidas pelo vocabulário do TF-IDF, que já está no modelo). Escolha o limiar usando SOMENTE a partição de validação da amostra bilíngue (outputs/jev_evaluation/sample_bilingual.csv), nunca o teste congelado, e reporte com n quantos textos em inglês seriam desviados por engano e quantos em português seriam pegos.

## Pendências das correções anteriores

1. Teste limpo de verdade: copie a solução para uma pasta nova com espaço no nome, apague qualquer ambiente, e siga APENAS o README. Reporte o que aconteceu, com tempo e avisos. Se o sandbox impedir criar o ambiente ou instalar pacotes, PARE e me diga — eu executo o teste fora dele.
2. Notebook do Colab: deixe-o pronto, fino (só instala e chama o mesmo código) e com o passo a passo no README. Não precisa executá-lo; eu rodo.
3. Histórico de testes: confirme que o menu grava cada classificação em outputs/.

## Ao terminar, mostre

- a saída exata do menu, como o avaliador vai ver, para estes três tickets:
  a) "my laptop screen is broken and the keyboard does not work"
  b) "i forgot my password and cannot access the vpn"
  c) "Olá, o status do pedido está como entregue mas o cliente não recebeu a compra e já se passaram 24 horas"
- o resultado do teste limpo, ou o que precisa que eu faça.

Não altere o modelo, o split, o teste congelado nem as métricas. Regras do AGENTS.md valem. Responda em português.
