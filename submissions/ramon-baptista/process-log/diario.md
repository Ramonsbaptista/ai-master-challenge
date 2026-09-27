# Diário de processo — AI Master Challenge (G4) — Challenge 002

Registro cronológico do trabalho. Cada entrada: o que foi feito, quem fez (eu / Claude Code (modelo Claude Opus) / Codex (modelo GPT-5.6 sol)),
o que deu errado e o que eu decidi.

**Arquitetura de trabalho adotada**
- **Eu (Ramon):** auditor e decisor. Reviso cada saída, aponto erro e tomo as decisões de negócio.
- **Claude Code:** guia. Explica os conceitos, prepara os prompts e verifica os números.
- **Codex (raciocínio baixo):** executor. Escreve o código e roda as análises.

Escolhi raciocínio baixo de propósito: quero observar onde um modelo mais fraco erra e provar que o
controle de qualidade é meu, não do modelo.

---

## 2026-09-19 — Sessão 1

### 1. Leitura do desafio e escolha do case
- Li os 4 READMEs do repositório `Gestao-Quatro-Ponto-Zero/ai-master-challenge`.
- Levantei quantas submissões cada case já tinha (últimos 100 PRs/issues via API do GitHub):
  003 Lead Scorer = 44, 001 Churn = 24, 002 Suporte = 22, 004 Social = 5.
- **Decisão:** Challenge 002 (Redesign de Suporte). Motivo: é o terreno onde tenho execução real
  (agentes de atendimento em produção), exige julgamento sobre o que NÃO automatizar, e tem
  metade da concorrência do 003.

### 2. Preparação do ambiente
- Pasta de trabalho: `C:\Users\Ramon\g4-ai-master\` (`data/`, `solution/`, `process-log/`, `docs/`).
- Instalei pandas, scikit-learn e matplotlib.

### 3. Download dos dados
- Em vez de baixar pelo navegador, testei a API pública do Kaggle: os dois datasets são públicos e
  a API serve o zip **sem autenticação**. Não precisou de token, CLI nem kagglehub.

```bash
curl -sL -o dataset.zip "https://www.kaggle.com/api/v1/datasets/download/<usuario>/<dataset>"
```

| Arquivo | Registros | Colunas |
|---|---|---|
| `all_tickets_processed_improved_v3.csv` | 47.837 | `Document`, `Topic_group` |
| `customer_support_tickets.csv` | 29.807 | 17 (tipo, canal, prioridade, tempos, satisfação, texto, resolução) |

### 4. Uso da assinatura em vez de API paga
- O executor roda pela minha conta ChatGPT via Codex CLI, sem custo de API:
  `codex exec -m gpt-5.6-sol -c model_reasoning_effort=high|low "<prompt>"`
- `gpt-5.6` (sem sufixo) é recusado em conta ChatGPT; só `gpt-5.6-sol` funciona.

---

_Próximo: Exercício 1 — separar treino/dev/teste antes de qualquer análise._

### 5. Baseline do executor: plano sem contexto de método
- Mandei o desafio "cru" para o Codex (raciocínio baixo), sem nenhuma orientação de
  metodologia, para ver como uma IA ataca o problema sozinha. Prompt em
  `chat-exports/01-baseline-gpt.md`.
- Ele acertou mais do que eu esperava (recusou o join sem chave comum; citou treino/teste), mas
  propôs "construir uma taxonomia comum entre os datasets". Bloqueei — ver
  `auditorias/01-plano.md`. Guardei outros 4 riscos sem avisar, de propósito.

### 6. Exploração e conferência independente
- O executor rodou a exploração e devolveu um relatório com 10+ achados.
- **Corrigi um erro meu:** eu vinha usando 29.807 tickets. São 8.469 — o arquivo tem 29.807
  LINHAS porque as descrições contêm quebras de parágrafo. O enunciado do G4 repete o mesmo
  erro ("~30.000 registros").
- Subi as duas bases brutas do Kaggle no Supabase e reconferi cada afirmação com SQL próprio
  (`solution/scripts/00_verificacao_auditoria.sql`). As 20 verificações bateram.

### 7. O achado que o executor não viu
- Ele listou várias evidências de dado sintético, mas não testou se a nota de satisfação tem
  sinal. Testei: distribuição uniforme (553/549/580/543/544) e média ~2,99 em NOVE recortes
  (canal, prioridade, tipo, tempo, idade, gênero, produto). Variação máxima de 0,2 ponto.
- Cliente que esperou +18h avalia 2,91; quem esperou até 6h avalia 3,00.
- Consequência para a entrega: a pergunta central do case ("o que impacta a satisfação") não
  tem resposta nesses dados. A recomendação vira redesenhar a pesquisa de satisfação.

### 8. Restrição de ambiente
- Cada inicialização do Python nesta máquina custava 30-68s (RAM no limite, 5,9 GB utilizáveis).
- Diagnostiquei com Get-MpPreference + uso de memória: não era antivírus, era falta de RAM.
- Adaptei a instrução ao executor: um script único por etapa em vez de comandos avulsos.

_Próximo: etapa 3 — diagnóstico operacional e protótipo no dataset 2._

### 9. Tradução embutida na conversa com o executor
Reestruturei `chat-exports/CONVERSA-COMPLETA-GPT.md`: cada etapa agora tem quatro blocos — o que eu
queria testar, o prompt, a resposta, e tradução + auditoria no mesmo lugar. A explicação em
linguagem simples de cada número (p-valor, mediana, P90, ticket-hora, placeholder, duplicatas,
distribuição triangular, amostra pequena) fica ao lado do resultado a que se refere, não num anexo
no fim. O avaliador entende sem precisar ler o prompt nem procurar glossário.

### 10. Auditoria 2 registrada
Ver `auditorias/02-diagnostico.md`: o executor passou nas três armadilhas do prompt (testou a
satisfação de verdade, escolheu mediana com justificativa, isolou as premissas de custo), e foi
reprovado em dois pontos — ranking de gargalo sobre 15 tickets e definição frouxa de desperdício.
Registrei também a hipótese operacional que levantei sobre as datas invertidas e os dois testes que
a derrubaram.

### 11. Matriz de decisão e benefícios tangíveis
- Acrescentei ao diagnóstico três faixas explícitas: automação de ponta a ponta, colaborador
  assistido por agentes de IA e execução 100% humana.
- A classificação foi feita por etapa, risco e reversibilidade, não apenas pelo assunto do ticket.
- Quantifiquei um benefício diretamente apoiado na base: com prevenção de 90%, a validação de
  datas evita 1.229 dos 1.365 registros cronologicamente inválidos.
- Montei um cenário recalculável de capacidade sobre os 8.469 tickets. Com premissas declaradas de
  elegibilidade e minutos ativos, ele libera 924,5 horas (31,7%) e R$ 46,2 mil brutos a R$ 50/h.
- Mantive economia, redução de erros e ROI como cenário até a operação medir tempo ativo, taxa e
  custo do erro, percentual elegível e custo total da solução.

### 11. O README passou por três versões
O texto final não saiu de uma vez. Houve um rascunho do Claude Code, uma versão do Codex escrita a partir
do enunciado, do template, da conversa completa e de um método de escrita de propostas, e uma
segunda versão do Codex que aplicou a minha auditoria: resumo executivo em 3 a 5 frases, linguagem
de gestor, detalhe técnico movido para os arquivos de apoio, recomendações aplicáveis, e o meu
julgamento com as minhas palavras, separado do que foi achado pelas IAs. A versão final é a segunda
do Codex, com a troca de "instrumento" por "métrica" e o print adicionado.

### 12. Commits
Dois planos de commit foram feitos em separado, um pelo Codex e um pelo Claude Code, e comparados. O do Codex
excluía a base de dados afirmando que a avaliação continuaria funcionando; conferido no código, não
funcionaria, porque o teste congelado guarda só o identificador de cada ticket, não o texto. O plano
final usa a estrutura e o .gitignore do Codex, mantém a base e inclui os scripts de ambiente do
experimento do Jev. Os commits são feitos no dia do envio, sem simular uma evolução no tempo.

### 13. O teste no Linux achou um defeito que o Windows escondia
Testei o protótipo no Google Colab, que roda Linux. O primeiro teste falhou: o Python do
Ubuntu/Debian vem sem o componente que instala o pip dentro do ambiente virtual (é um pacote
separado do sistema, o python3-venv). Um avaliador com Ubuntu cairia nesse erro, receberia uma
mensagem apontando a causa errada ("permissão de escrita") e seria mandado para o Colab, que falhava
igual — ficaria sem saída. O Codex corrigiu o run.sh com caminhos alternativos e mensagem com a causa
real. No segundo teste, a avaliação reproduziu no Linux exatamente a mesma matriz de confusão do
Windows. Pelo caminho, também achei que o zip gerado pelo Compress-Archive do Windows grava os
caminhos com barra invertida, que o Linux não reconhece como pastas.

---

## 2026-09-27 — Rodadas 40 a 48

### 14. Rodada 40 — desenho da interface
- **O que pedi:** “uma empresa do nível do G4 não vai aceitar um sistema cru desse jeito no terminal”. Pedi primeiro o desenho, sem construir.
- **O que o Codex fez:** propôs Flask com HTML, CSS e JavaScript locais, três telas e o mesmo núcleo do terminal.
- **O que o Claude Code auditou:** conferiu se o desenho preservava teste congelado, hashes, idioma, kill switch, pouca RAM e execução por um comando.
- **O que decidi:** aprovei as três telas em versão de produção.

### 15. Rodada 41 — construção
- **O que pedi:** interface completa, navegador aberto por `run.ps1`/`run.sh`, terminal preservado com `--cli` e nenhuma regra duplicada.
- **O que o Codex fez:** construiu Classificar, Avaliação reproduzível e Controles e limites sobre o núcleo existente; manteve o histórico sem texto do cliente.
- **O que o Claude Code auditou:** comparou as decisões da web com as do núcleo e verificou rotas, kill switch e privacidade.
- **O que decidi:** mantive a arquitetura e pedi uma nova rodada apenas para tornar os textos compreensíveis a um executivo.

### 16. Rodada 42 — reescrita didática
- **O que pedi:** trocar a linguagem de estatístico por cenas concretas, sem esconder fórmulas, limites ou incerteza.
- **O que o Codex fez:** colocou a conclusão antes dos detalhes, traduziu VP/FP/FN/VN para linguagem de fila e explicou como ler a matriz.
- **O que o Claude Code auditou:** verificou o tom do README, a origem dinâmica dos números e a honestidade sobre score, português e erro.
- **O que decidi:** aprovei o visual e a comunicação; números técnicos continuaram expansíveis.

### 17. Rodada 43 — inicialização e demo
- **O que pedi:** impedir que a primeira impressão fosse “Não é possível acessar esse site” e preparar uma demo pública.
- **O que o Codex fez:** passou a esperar o servidor responder antes de abrir o navegador, escolheu outra porta quando a 5000 está ocupada e preparou deploy no Render com modo público seguro.
- **O que o Claude Code auditou:** encontrou o defeito original — o navegador abria por um temporizador fixo antes do servidor — e cobrou testes de porta, ordem de abertura e falha legível.
- **O que decidi:** manter execução local em `127.0.0.1`; eu publicaria a demo no Render.

### 18. Rodada 44 — onde entra LLM
- **O que perguntei:** “Uma coisa que reparei usando o sistema, não temos LLM no fluxo de trabalho, sómente o TF-IDF. O enunciado não pediu para identificar os momentos onde usa llm e por que e quando não usar?”
- **O que o Codex fez:** separou classificação supervisionada, regras exatas, assistência por LLM e decisões que continuam humanas.
- **O que o Claude Code auditou:** conferiu a resposta contra o enunciado e contra o teste já feito com o Jev.
- **O que decidi:** documentar essa divisão na proposta e no README, sem inserir LLM só para dizer que existe.

### 19. Rodada 45 — texto livre em produção
- **O que perguntei:** “quem garante que o avaliador só irá testar o modelo com exemplos prontos? Em produção, nenhum cliente abre o ticket falando exatamente a mesma frase que o banco de dados tem.”
- **O que o Codex fez:** criou um teste sintético por grupos, mediu a Base 1 e construiu uma barreira experimental de “fora do escopo”, desligada.
- **O que o Claude Code auditou:** encontrou frases repetidas com sufixos numéricos. A contagem de textos únicos após normalizar minúsculas, pontuação e números deixou três grupos com apenas **12 a 16 frases distintas (n=12 a n=16 por grupo)**. O método é adequado porque mede observações semanticamente distintas; esses grupos são exploratórios por terem **n<30**. Não houve premissa externa.
- **O que decidi:** invalidar esses grupos e refazer o conjunto antes de usar qualquer conclusão.

### 20. Rodada 46 — refação da robustez
- **O que pedi:** frases realmente distintas, verificação automática de duplicidade, rótulo anterior à inferência, maioria em inglês fora do escopo e Base 1 como prova principal.
- **O que o Codex fez:** refez os casos, substituiu os artefatos contaminados, recalibrou só nos sintéticos e explicou a diferença entre a faixa alta oficial e a decisão final do serviço.
- **O que o Claude Code auditou:** confirmou que o aparente 0% da barreira vinha de textos do mesmo gerador e vocabulário usados na calibração; faltava provar generalização.
- **O que decidi:** medir a barreira, sem ajuste, nos **8.469 tickets da Base 1 (n=8.469)**. O método foi aplicar a mesma regra congelada a todos os registros; isso testa generalização sem contaminar a prova. Premissa: tickets independentes.

### 21. Rodada 47 — a prova fora do domínio
- **O que pedi:** comparar a Base 1 antes e depois da barreira e calcular o erro apenas entre tickets que iriam direto.
- **O que o Codex fez:** pela comparação antes/depois no mesmo conjunto, mostrou que a barreira reduziu **67/2.718 = 2,5% dos envios diretos (n=2.718)**. Entre os encaminhados, calculou `erros ÷ encaminhados`; o teste oficial teve **340/5.527 = 6,15% (n=5.527)**. O fundamento é medir risco apenas onde haveria automação; sintéticos gerados por IA são premissa e limitação.
- **O que o Claude Code auditou:** confrontou o **0/204 = 0,0% sintético (n=204)** com os **67/2.718 = 2,5% bloqueados na Base 1 (n=2.718)**. O método comparou a regra congelada dentro e fora do vocabulário gerador; o fundamento foi testar generalização. Premissa: os tickets são independentes. A regra não generalizou.
- **O que decidi:** deixar a barreira desligada, não recalibrar com a Base 1 e começar qualquer piloto em modo sombra, preso aos critérios go/no-go.

### 22. Rodada 48 — fechamento
- **O que pedi:** levar a robustez ao README principal, corrigir duas frases da Avaliação, registrar as rodadas 40–48 e não tocar no sistema.
- **O que o Codex fez:** alinhou README, interface e diário; simplificou as premissas econômicas sem mudar números.
- **O que o Claude Code auditou:** a rodada de fechamento será conferida pela suíte completa e pela revisão dos arquivos alterados.
- **O que decidi:** manter modelo, split, teste congelado, limiares, números oficiais e barreira desligada.

### 23. Rodadas 49 a 52: três perguntas no topo e o avaliador final
- **O que pedi:** as três perguntas do diretor logo no início do README, com respostas diretas; trocar "Claude" e "GPT" por "Claude Code" e "Codex"; depois, uma avaliação independente simulando o revisor do G4.
- **O que o Codex fez:** respondeu às três perguntas com número, n e primeiro passo; uma sessão nova, só de leitura, comparou a entrega com os três concorrentes mais bem avaliados e deu **8,7/10**, apontando dez correções (entre elas, "86,51%" chamado de acurácia quando é macro-F1).
- **O que o Claude Code auditou:** retirou da primeira resposta o ranking "Chat × cancelamento", que os horários sorteados não sustentam; conferiu as correções, a varredura de chaves e os 21 testes; gerou os prints das telas direto do sistema.
- **O que decidi:** aplicar as correções e enviar com a segunda avaliação independente em **8,8/10**, "Forte, muito perto de Excepcional".

### 24. Publicação: a verificação de integridade barrou o próprio deploy
- **O que aconteceu:** no Render, o sistema subiu mas recusou-se a classificar. O git convertera o fim de linha de três arquivos protegidos por SHA-256 (base de treino, divisão treino/teste e proteção de idioma); no Linux o hash deixou de bater e a trava de integridade bloqueou a análise, exatamente como promete.
- **O que o Claude Code fez:** comparou o hash de cada arquivo no git com o do disco, confirmou a causa e adicionou um `.gitattributes` que guarda esses arquivos byte a byte.
- **Resultado:** a demo pública respondeu com `{"status":"ok"}`, classificou os exemplos e reproduziu a avaliação.