Decisão do Ramon: aprovado o seu desenho completo (as 3 telas), em versão de produção. Pode construir.

Faça sozinho, sem abrir agentes paralelos. Regras do AGENTS.md valem.

O QUE CONSTRUIR (conforme o seu desenho):
1. Interface web em Flask + HTML/CSS/JS mínimos, consumindo `src/ticket_classifier/` sem duplicar regra nenhuma. Modelo carregado uma única vez, com verificação de hashes como hoje.
2. Tela "Classificar": campo de texto, exemplos prontos com um clique (use os 10 abaixo), botão "Analisar ticket", cartão verde "Vai direto para a fila" ou âmbar/vermelho "Vai para uma pessoa" com o motivo, categoria em português, score com o rótulo "score do modelo (não calibrado)", e o bloco permanente "Onde a IA para".
3. Tela "Avaliação reproduzível": conclusão para o gestor primeiro; detalhes expansíveis (métricas por classe, matriz de confusão, fórmulas com números substituídos, hashes). Executa `evaluate.reproduce()` e só apresenta o retorno. Deixe claro que leva alguns segundos (mostre "carregando").
4. Tela "Controles e limites": kill switch, proteção de idioma e integridade dos artefatos, com o significado operacional de cada um. Estados sempre visíveis no cabeçalho.
5. `run.ps1` e `run.sh` passam a abrir a interface no navegador por padrão; `--cli` mantém o menu do terminal atual intacto. Colab continua funcionando (pode expor a interface ou seguir pelo núcleo — explique a escolha).
6. Flask com versão fixa em `requirements.txt`. Servidor só em 127.0.0.1.

PADRÃO DE PRODUÇÃO (o avaliador é executivo, não técnico):
- Visual limpo e profissional: tipografia legível, espaçamento generoso, uma cor de destaque, sem aparência de protótipo. Nada de dependência externa de CDN: tudo local, para funcionar offline.
- Todo texto em português, linguagem de negócio, acentos corretos (UTF-8).
- Erros tratados com mensagem clara (texto vazio, texto muito longo, kill switch ligado, falha de integridade) — nunca stack trace na tela.
- O histórico continua sem gravar o texto do ticket (hash, tamanho, decisão, categoria, score, faixa).
- Funciona bem em tela de notebook; celular não é requisito.

PROIBIDO: alterar modelo, split, teste congelado, limiares, métricas ou números já publicados.

TESTES:
- Os 10 testes atuais devem continuar passando.
- Adicione testes da camada web (rotas respondem, decisão da web == decisão do núcleo para os 10 exemplos, kill switch bloqueia na web, texto não é gravado no histórico).
- Rode a suíte completa ao final (um script único) e reporte a saída real.

EXEMPLOS PARA OS BOTÕES (texto exato):
1. my laptop screen is broken and the keyboard does not work
2. i forgot my password and cannot log in to the vpn
3. i need administrator rights to install software on my computer
4. my mailbox is full and i cannot receive new emails, please increase the storage quota
5. please create a new project code and add the team members to the internal project
6. please order a new headset for me, the purchase request is attached
7. my monitor keeps flickering and the docking station does not detect the second screen
8. question about my payslip and the number of vacation days left
9. hello thanks
10. Olá, o status do pedido está como entregue mas o cliente não recebeu a compra e já se passaram 24 horas

Se pip for bloqueado pelo sandbox, NÃO contorne: pare, deixe o código pronto e diga exatamente o comando que o Claude precisa rodar fora do sandbox.

AO FINAL, responda em até 20 linhas: arquivos criados/alterados, como abrir, resultado real dos testes, o que ficou pendente.
