Decisão do Ramon: duas entregas nesta rodada — (A) inicialização à prova de falha e (B) demo online. Motivo: se o avaliador abrir e vir "Não é possível acessar esse site", a entrega perde na primeira impressão.

Faça sozinho, sem agentes paralelos. Regras do AGENTS.md valem. PROIBIDO alterar modelo, split, teste congelado, limiares, métricas ou números.

## A) Inicialização à prova de falha

Problema encontrado pelo Claude em `src/ticket_classifier/web.py:147`: o navegador abre com `Timer(1.0, ...)` fixo, antes de o modelo carregar e os hashes serem conferidos. Numa máquina lenta, o avaliador vê ERR_CONNECTION_REFUSED. Além disso, a porta 5000 costuma estar ocupada no macOS (AirPlay).

1. Abrir o navegador só depois que o servidor responder de fato (checagem ativa, com tempo máximo e mensagem clara se estourar).
2. Se a porta 5000 estiver ocupada, escolher automaticamente uma porta livre e abrir nela.
3. Terminal com mensagens claras em português: "Carregando o modelo, aguarde…", depois o endereço, "Não feche esta janela" e "Para encerrar, Ctrl+C".
4. Se o navegador não abrir sozinho, o endereço fica bem visível para copiar.
5. Testes automáticos: porta ocupada → usa outra; navegador só abre após resposta; falha de inicialização mostra mensagem legível, sem stack trace.

## B) Demo online

Objetivo: um link público que o avaliador abre sem instalar nada. Você decide a plataforma (ex.: Hugging Face Spaces, Render ou outra) e justifica: custo zero, RAM suficiente, tempo de "acordar" do plano gratuito, estabilidade, facilidade para o Ramon publicar sozinho.

1. Prepare todos os arquivos de deploy dentro de `submissions/ramon-baptista/solution/` (ex.: Dockerfile ou equivalente, comando de start), reaproveitando o mesmo núcleo e a mesma verificação de hashes. Nenhuma lógica duplicada.
2. Modo público seguro: escutar em 0.0.0.0 SÓ no modo deploy (localmente continua 127.0.0.1); limite de tamanho do texto mantido; nada de texto de ticket gravado; sem modo debug; sem chaves nem `.env` no pacote; a reprodução da avaliação não pode derrubar o servidor com vários acessos simultâneos (cache do resultado ou equivalente — explique).
3. Aviso visível na demo: "Demonstração pública — não envie dados reais de clientes."
4. Escreva `solution/DEPLOY.md` com o passo a passo para o Ramon publicar sozinho, em linguagem simples, com numeração e o que ele vai ver em cada passo. O Claude NÃO cria contas nem publica; quem faz é o Ramon.
5. Teste localmente o modo deploy (sem publicar) e reporte o resultado real.

## Testes
Os 14 atuais devem continuar passando, mais os novos. Rode a suíte completa ao final em um script único. Se pip ou Docker forem bloqueados pelo sandbox, não contorne: diga o comando exato para o Claude rodar fora.

## Ao final, em até 20 linhas
Arquivos criados/alterados, plataforma escolhida e por quê, resultado real dos testes, o que o Ramon precisa fazer para publicar, pendências.
