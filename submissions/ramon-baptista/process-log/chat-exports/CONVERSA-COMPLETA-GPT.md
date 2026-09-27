# Conversa com o executor de IA — GPT-5.6 sol

> **Como ler este documento.** Cada etapa tem quatro blocos, nesta ordem: **(1) o que eu queria
> testar**, **(2) o prompt enviado**, **(3) a resposta recebida** e **(4) tradução e auditoria** —
> onde cada número técnico é explicado em linguagem direta e eu digo o que aprovei e o que reprovei.
> Não é preciso ler os prompts para entender os resultados.

**Modelo:** gpt-5.6-sol · **raciocínio:** baixo (escolha deliberada) · **via:** Codex CLI, conta ChatGPT

```
codex exec -m gpt-5.6-sol -c model_reasoning_effort=low --sandbox workspace-write
```

**Por que raciocínio baixo:** eu queria observar onde um modelo menos cuidadoso erra, e provar que o
controle de qualidade é meu e não dele. O log bruto de cada execução, com todos os comandos rodados,
está nos arquivos `01-`, `02-` e `03-...resposta.txt` desta mesma pasta.

---

# Etapa 1 — O plano de ataque, sem nenhuma orientação de método

## 1. O que eu queria testar

Enviei o desafio cru: contexto, dados e ambiente. **Nenhuma orientação metodológica** — não falei em
separar treino e teste, matriz de confusão, threshold de confiança ou baseline de comparação. Queria
ver como uma IA ataca o problema sozinha, para saber exatamente onde minha intervenção agrega.

## 2. O prompt que enviei

```
# INTENÇÃO

Você vai resolver um desafio de processo seletivo real: o "AI Master Challenge" do G4 Educação.
O objetivo é atuar como um profissional que usa IA para resolver um problema de negócio de ponta
a ponta, entregando algo que uma empresa usaria de verdade — não um exercício acadêmico.

Estamos trabalhando juntos: eu sou o responsável pela entrega e vou revisar criticamente tudo o
que você produzir. Quero seu raciocínio e suas decisões explícitas, para eu poder discordar.

# INFORMAÇÃO

## O desafio

Repositório do desafio: https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge
Case escolhido: Challenge 002 — Redesign de Suporte
README do case: https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/challenges/process-002-support/README.md
Guia de submissão: https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/submission-guide.md

Contexto do case: sou o novo "AI Master" da área de Suporte ao Cliente de uma empresa de
tecnologia que atende cerca de 30.000 tickets por ano por email, chat, telefone e redes sociais.
O time está sobrecarregado, o tempo de resolução subiu e a satisfação caiu.

O Diretor de Operações pediu três coisas:
1. Onde estamos perdendo tempo.
2. O que pode ser automatizado com IA.
3. Uma demonstração de que funciona — algo rodando, não um PowerPoint.

O que o case exige como entrega:
- Diagnóstico operacional com números (gargalos por canal, prioridade e tipo; o que impacta a
  satisfação; quanto se desperdiça em horas e, se possível, em dinheiro).
- Proposta de automação com IA, dizendo o que automatizar E o que NÃO automatizar, com o fluxo
  proposto (ticket entra, o que acontece em cada etapa, onde a IA atua, onde o humano intervém).
- Protótipo funcional que demonstre a proposta, rodando com os dados reais.

Critérios de avaliação declarados pelo G4:
- Usou os dois datasets (um tem métricas, o outro tem texto — o valor está no cruzamento)?
- O diagnóstico tem números concretos ou é genérico?
- A proposta é realista? (automatizar 100% é considerado red flag, não virtude)
- Sabe distinguir onde a IA ajuda de onde o humano é insubstituível?
- O protótipo funciona com dados reais, não com 3 exemplos escolhidos a dedo?
- O avaliador é um executivo não técnico e precisa entender e agir.

Aviso importante do G4: eles já rodaram este mesmo brief em Claude, GPT e Gemini e guardaram as
respostas como baseline. Entregas parecidas com esse baseline são descartadas.

## Os dados (já baixados na minha máquina)

Pasta: C:\Users\Ramon\g4-ai-master\data\

1) customer_support_tickets.csv — 29.807 registros
   Colunas: Ticket ID, Customer Name, Customer Email, Customer Age, Customer Gender,
   Product Purchased, Date of Purchase, Ticket Type, Ticket Subject, Ticket Description,
   Ticket Status, Resolution, Ticket Priority, Ticket Channel, First Response Time,
   Time to Resolution, Customer Satisfaction Rating
   Origem: https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset

2) all_tickets_processed_improved_v3.csv — 47.837 registros
   Colunas: Document (texto completo do ticket), Topic_group (categoria, 8 valores)
   Origem: https://www.kaggle.com/datasets/adisongoh/it-service-ticket-classification-dataset

## Ambiente

Windows 11, Python disponível com pandas 3.0.6, scikit-learn 1.9.1 e matplotlib 3.11.2.
Você pode ler os arquivos, escrever scripts e executá-los.

# INSTRUÇÃO

1. Antes de escrever qualquer código, me diga em no máximo 10 linhas: como você vai atacar este
   desafio, em que ordem, e por quê.
2. Explore os dois datasets e me traga o que você encontrou. Aponte também qualquer problema de
   qualidade dos dados que você identificar.
3. Faça o diagnóstico operacional pedido pelo case, com números.
4. Proponha a automação, incluindo o que não automatizar.
5. Construa o protótipo funcional.
6. Ao final de cada etapa, pare e me apresente o resultado antes de seguir para a próxima. Eu vou
   revisar e posso pedir mudanças.

Regras:
- Toda afirmação numérica precisa vir do código que você rodou. Não estime de cabeça.
- Quando tomar uma decisão metodológica, diga qual alternativa você descartou e por quê.
- Se algum dado não sustentar uma conclusão, diga isso explicitamente em vez de forçar um insight.
- Salve os scripts em C:\Users\Ramon\g4-ai-master\solution\ e os resultados em arquivos, não só
  no chat.
- Responda em português.
```

## 3. A resposta que recebi

```
1. Auditar os dois datasets separadamente: esquema, completude, duplicatas, consistência e distribuições.
2. Verificar como cruzá-los com rigor; como não há chave comum aparente, não inventarei um join registro a registro.
3. Construir uma taxonomia comum entre métricas operacionais e textos, documentando cobertura, confiança e limitações.
4. Diagnosticar gargalos por canal, prioridade e tipo, medindo tempos, satisfação, volume e retrabalho observável.
5. Quantificar desperdício apenas com premissas rastreáveis; custos serão cenários parametrizados se não houver salários/custos reais.
6. Identificar casos automatizáveis por volume, repetição, risco, previsibilidade e qualidade textual.
7. Desenhar o fluxo futuro com triagem por IA, automação controlada, confiança mínima, auditoria e escalonamento humano.
8. Construir um protótipo que processe os dados completos, classifique tickets e recomende automação ou intervenção humana.
9. Validar com divisão de treino/teste, métricas por classe e análise de erros; descarto demonstrações com exemplos escolhidos.
10. Salvar scripts e resultados em `solution/`, parando após cada etapa para sua revisão antes de continuar.
```

## 4. Tradução e auditoria

**O que ele acertou sozinho:** percebeu que as duas bases não têm campo em comum e se recusou a
juntá-las linha a linha. É o erro em que a maioria cai, porque o próprio enunciado do desafio diz
que "o poder está no cruzamento". Também citou separar treino e teste antes de eu pedir.

**O que eu reprovei — "construir uma taxonomia comum entre os datasets".**

*Taxonomia*, aqui, é apenas a lista de caixinhas onde cada ticket é colocado. As duas bases usam
listas incompatíveis:

| Base 2 — TI interna (47.837) | Base 1 — consumidor final (8.469) |
|---|---|
| Hardware 13.617 · RH 10.915 · Acessos 7.125 · Diversos 7.060 · Armazenamento 2.777 · Compras 2.464 · Projetos internos 2.119 · Direitos administrativos 1.760 | Reembolso 1.752 · Problema técnico 1.747 · Cancelamento 1.695 · Dúvida de produto 1.641 · Dúvida de cobrança 1.634 |

Quatro categorias da base 2 — RH, Acessos, Projetos internos e Direitos administrativos, somando
21.919 chamados — **não existem** no mundo do consumidor final. E reembolso e cancelamento, 3.447
tickets da base 1, não existem na base 2.

**A analogia:** é treinar um funcionário para separar cartas da fábrica ("meu crachá não passa", "o
servidor caiu") e depois mandá-lo separar cartas de clientes da loja, que reclamam de celular com
defeito. Ele não fica sem resposta — dá respostas confiantes e erradas, porque toda carta acaba
caindo em alguma caixinha conhecida.

**Regra que impus para as etapas seguintes:**

- Base 2 → treinar e medir o classificador (é a única com rótulo confiável).
- Base 1 → diagnóstico operacional, com as categorias próprias dela.
- A ponte entre as duas é o **método**, nunca o rótulo.

**O que identifiquei e decidi NÃO avisar**, para observar se ele erraria sozinho: separar um terceiro
conjunto para ajuste, comparar com um baseline simples, desconfiar do campo de satisfação, e definir
o custo de errar antes de decidir o que automatizar.

---

# Etapa 2 — Exploração e qualidade dos dados

## 1. O que eu queria testar

Se ele descreveria os dados ou realmente os interrogaria. Pedi explicitamente a lista do que os dados
**não** permitem concluir — a parte que costuma faltar.

## 2. O prompt que enviei

```
Revisei seu plano. Aprovado, com uma correção e uma restrição.

CORREÇÃO — item 3 do seu plano ("construir uma taxonomia comum entre métricas operacionais e textos"):

Está reprovado e contradiz o seu próprio item 2. Os dois datasets usam conjuntos de rótulos incompatíveis:

- Dataset 2 (TI interna): Hardware 13.617, HR Support 10.915, Access 7.125, Miscellaneous 7.060, Storage 2.777, Purchase 2.464, Internal Project 2.119, Administrative rights 1.760.
- Dataset 1 (consumidor final): Refund request 1.752, Technical issue 1.747, Cancellation request 1.695, Product inquiry 1.641, Billing inquiry 1.634. Os produtos são Canon EOS, GoPro Hero, Nest Thermostat, Amazon Echo.

Quatro categorias do dataset 2 (HR Support, Access, Internal Project, Administrative rights = 21.919 tickets, 46% do total) não têm equivalente no dataset 1. E Refund/Cancellation request (3.447 tickets do dataset 1) não existem no dataset 2. Fundir as listas geraria um classificador treinado em chamados corporativos aplicado a reclamações de consumidor: respostas confiantes e erradas.

RESTRIÇÃO que passa a valer:
- Dataset 2 = treinar e medir o classificador (é o único com rótulo confiável).
- Dataset 1 = diagnóstico operacional, com as categorias próprias dele.
- A ponte entre os dois é metodológica, nunca registro a registro nem por fusão de rótulos. Se você quiser relacionar os dois de alguma forma, apresente a proposta antes de executar.

PRÓXIMA ETAPA — execute agora o item 2 do seu plano (exploração dos dois datasets) e pare ao final.

Entregue:
1. O que cada dataset contém de fato: distribuições das colunas relevantes, faltantes, duplicatas.
2. Problemas de qualidade que você encontrou. Seja específico e mostre o número que sustenta cada afirmação.
3. Uma lista do que estes dados PERMITEM concluir e do que NÃO permitem.

Salve o script em submissions/ramon-baptista/solution/scripts/ e as saídas em submissions/ramon-baptista/solution/outputs/. Responda em português.

RESTRIÇÃO DE AMBIENTE (importante): esta máquina tem pouca RAM e iniciar o Python custa ~17 segundos por chamada. Não execute vários comandos Python pequenos. Escreva UM script único, completo, em submissions/ramon-baptista/solution/scripts/01_exploracao.py, que faça toda a exploração de uma vez e grave os resultados em arquivos dentro de submissions/ramon-baptista/solution/outputs/. Rode esse script UMA vez. Se precisar corrigir, corrija o script e rode de novo, sem comandos avulsos.
```

## 3. A resposta que recebi

```
Exploração concluída, mantendo os datasets totalmente separados.

Principais achados:

- Dataset 1: 8.469 registros e 17 colunas.
  - 5.700 resoluções, tempos de resolução e avaliações ausentes (67,30%).
  - Os faltantes são estruturais: todos os 2.769 tickets fechados estão completos; tickets abertos ou aguardando cliente não possuem resolução.
  - 1.365 registros apresentam resolução anterior à primeira resposta.
  - Todas as 8.469 descrições possuem o placeholder literal `{product_purchased}`.
  - 457 registros compartilham descrições normalizadas repetidas.
  - Todos os 8.469 e-mails usam domínios reservados `example.com`, `example.net` ou `example.org`.
  - Não há IDs ou linhas completas duplicadas.
  - O arquivo contém 42 produtos, não apenas os quatro mencionados como exemplos.

- Dataset 2: 47.837 registros e 2 colunas.
  - Sem valores faltantes, documentos vazios, linhas duplicadas ou textos normalizados repetidos.
  - Nenhum texto idêntico recebeu rótulos conflitantes.
  - Forte desbalanceamento: Hardware representa 28,47%, enquanto Administrative rights representa 3,68%.
  - Os documentos têm mediana de 26 palavras, variando de 2 a 981.
  - O texto já foi fortemente processado; não existem texto bruto, datas ou métricas operacionais.

Arquivos principais:

- [Script da exploração](C:/Users/Ramon/g4-ai-master/submissions/ramon-baptista/solution/scripts/01_exploracao.py)
- [Relatório completo](C:/Users/Ramon/g4-ai-master/submissions/ramon-baptista/solution/outputs/01_relatorio_exploracao.md)
- [Resumo estruturado](C:/Users/Ramon/g4-ai-master/submissions/ramon-baptista/solution/outputs/01_resumo.json)
- [Perfil de todas as colunas](C:/Users/Ramon/g4-ai-master/submissions/ramon-baptista/solution/outputs/01_perfil_colunas.csv)
- [Distribuições categóricas](C:/Users/Ramon/g4-ai-master/submissions/ramon-baptista/solution/outputs/01_distribuicoes_categoricas.csv)
- [Faltantes por status](C:/Users/Ramon/g4-ai-master/submissions/ramon-baptista/solution/outputs/01_faltantes_por_status_dataset1.csv)

O relatório também contém, separadamente para cada dataset, a lista completa do que os dados permitem e não permitem concluir. Nenhuma ponte, fusão ou correspondência entre taxonomias foi executada.
```

## 4. Tradução e auditoria

**"São 8.469 tickets, não ~30.000."** O arquivo tem 29.807 linhas, mas cada ticket ocupa várias
linhas porque a descrição do cliente tem parágrafos. Quem conta linhas vê 30 mil; quem conta
atendimentos vê 8.469. É contar as pessoas de uma festa contando os sapatos. *O enunciado do próprio
desafio afirma "~30.000 registros", e eu também estava usando esse número até aqui.*

**"67,3% sem resolução, tempo e nota — mas isso é estrutural."** À primeira vista parece falha de
preenchimento. Não é: **todos** os 2.769 tickets fechados estão completos e **nenhum** ticket aberto
tem esses campos. Eles só nascem quando o ticket fecha. Confundir uma coisa com a outra levaria a um
plano de ação inútil, do tipo "cobrar o time a preencher os campos".

**"Todas as descrições contêm `{product_purchased}`."** É aquele e-mail que chega escrito "Olá
{nome}, sua compra...", quando ninguém trocou a etiqueta pelo dado real. Acontece em 100% dos casos.
Como o desafio pede para analisar o texto das reclamações, isso significa que não há linguagem real
de cliente na base 1.

**"457 descrições repetidas."** Ignorando maiúsculas e pontuação, 457 tickets têm texto idêntico ao
de outro. Clientes diferentes, mesma reclamação palavra por palavra. Em um classificador, texto
repetido entre treino e teste é trapaça: o modelo acerta porque já viu a frase, não porque aprendeu.

**"100% dos e-mails em example.com."** Domínio reservado para documentação — mais uma confirmação de
base gerada.

**Minha verificação independente:** subi as duas bases brutas em um banco Postgres e reconferi as 20
afirmações com SQL próprio (`solution/scripts/00_verificacao_auditoria.sql`). Todas bateram.

**O que ele não viu:** listou várias evidências de base sintética, mas não testou se a nota de
satisfação tem sinal. Testei por conta: distribuição praticamente uniforme (553 notas 1, 549 notas 2,
580 notas 3, 543 notas 4 e 544 notas 5) e média entre 2,91 e 3,12 em nove recortes diferentes.
Guardei o achado e transformei na armadilha da etapa seguinte.

---

# Etapa 3 — Diagnóstico operacional

## 1. O que eu queria testar

Montei três armadilhas no prompt:

1. **Satisfação:** pedi "identifique quais variáveis influenciam a nota e em que magnitude",
   **pressupondo** que alguma influencia. Se ele aceitasse a premissa, inventaria explicação para
   ruído.
2. **Evidência estatística:** exigi teste, não comparação de médias a olho.
3. **Média ou mediana:** deixei a escolha com ele, exigindo justificativa. Com 1.365 valores
   negativos e distribuição torta, usar média seria erro.

## 2. O prompt que enviei

```
# INTENÇÃO

Executar a etapa 3 do plano: o diagnóstico operacional do Dataset 1, que é a primeira das três entregas obrigatórias do case. O Diretor de Operações precisa saber onde a operação perde tempo e quanto isso custa, com números que sustentem decisão.

# INFORMAÇÃO

## O que já foi estabelecido nas etapas anteriores

Resultado da sua exploração, que eu conferi de forma independente em SQL e confirmei:

- O Dataset 1 tem 8.469 tickets (não os ~30.000 que o enunciado do desafio afirma; o arquivo tem 29.807 linhas porque as descrições contêm quebras de parágrafo).
- 67,3% dos tickets não têm resolução, tempo de resolução nem nota. Isso é estrutural: os 2.769 tickets fechados estão todos completos e nenhum ticket aberto tem esses campos.
- 1.365 tickets (16%) têm tempo de resolução ANTERIOR à primeira resposta — dado inválido.
- 100% das descrições contêm o placeholder {product_purchased} e 100% dos e-mails são de domínio example.*. O conteúdo textual do Dataset 1 é gerado, não real.
- O Dataset 2 está íntegro: 47.837 textos, sem nulos, duplicatas ou rótulos conflitantes. Desbalanceado (Hardware 28,47% até Administrative rights 3,68%). Mediana de 26 palavras.

## Restrições que continuam valendo

- Dataset 2 = treinar e medir o classificador. Dataset 1 = diagnóstico operacional.
- Proibido fundir taxonomias ou cruzar registro a registro.
- Nenhuma afirmação numérica sem código que a produza.
- Ambiente com pouca RAM: um script único por etapa, rodado uma vez. Nada de comandos avulsos.

# INSTRUÇÃO

Produza o diagnóstico operacional do Dataset 1 respondendo às três perguntas do case:

1. ONDE A OPERAÇÃO TRAVA
   - Volume e tempos por canal, prioridade e tipo de ticket.
   - Quais combinações concentram os piores tempos.
   - Decida e justifique quais registros você inclui ou exclui do cálculo de tempo, considerando os 1.365 inválidos e os 67,3% incompletos.
   - Use a medida de tendência central que você julgar correta para esta distribuição, e justifique a escolha.

2. O QUE IMPACTA A SATISFAÇÃO DO CLIENTE
   - Identifique quais variáveis influenciam a nota e em que magnitude.
   - Sustente a resposta com evidência estatística, não com diferença de médias observada a olho.

3. QUANTO SE DESPERDIÇA
   - Quantifique em horas.
   - Se converter em dinheiro, declare cada premissa numa tabela separada (custo/hora, jornada, volume considerado) e deixe claro que são premissas, não dados.

Formato da entrega:
- Script único em submissions/ramon-baptista/solution/scripts/02_diagnostico.py
- Saídas em submissions/ramon-baptista/solution/outputs/
- Um relatório em 02_diagnostico.md escrito para um Diretor de Operações não técnico: conclusão primeiro, número junto, e o detalhe metodológico depois.
- Ao final, liste separadamente: o que estes dados permitem concluir com segurança e o que não permitem.

Pare ao terminar. Eu vou revisar antes de seguir para o protótipo.
```

## 3. A resposta que recebi

```
Etapa 3 concluída.

Entregues:

- [Script único](/C:/Users/Ramon/g4-ai-master/submissions/ramon-baptista/solution/scripts/02_diagnostico.py)
- [Relatório executivo](/C:/Users/Ramon/g4-ai-master/submissions/ramon-baptista/solution/outputs/02_diagnostico.md)
- [Pasta com CSVs e JSON de auditoria](/C:/Users/Ramon/g4-ai-master/submissions/ramon-baptista/solution/outputs/)

Principais resultados:

- 1.404 tickets têm tempos cronologicamente válidos.
- Mediana de resolução: 6,3 horas; P90: 16,0 horas.
- Pior combinação elegível: chat + prioridade baixa + problema técnico, com mediana de 13,2 horas.
- Nenhuma das oito variáveis testadas apresentou associação estatisticamente significativa com satisfação.
- Foram estimadas 4.064 ticket-horas acima da mediana do respectivo tipo de ticket.
- A conversão ilustrativa resulta em 406 horas de trabalho e R$ 20.321, com todas as premissas isoladas e explicitamente identificadas como externas aos dados.

O relatório também esclarece que não é possível medir o tempo até a primeira resposta, pois o dataset não contém a data de abertura do ticket.
```

## 4. Tradução e auditoria

### Ele passou nas três armadilhas

**Satisfação — não caiu na premissa.** Rodou um teste estatístico para cada uma das oito variáveis.
O teste funciona como um interrogatório: para cada suspeito, pergunta se a diferença que ele provoca
na nota é maior do que a variação que já aconteceria por puro acaso.

| Suspeito | p-valor | Culpado? |
|---|---|---|
| Canal | 0,29 | não |
| Prioridade | 0,58 | não |
| Produto | 0,66 | não |
| Gênero | 0,66 | não |
| Tipo de ticket | 0,72 | não |
| Assunto | 0,74 | não |
| Idade | 0,82 | não |
| **Tempo de espera** | **0,91** | não |

*O p-valor é a chance de a diferença ter aparecido por acaso.* Abaixo de 0,05 se considera efeito
real. O menor aqui é 0,29. E o tempo de espera, que deveria ser o fator mais forte de todos, deu
0,91 — o mais inocente da lista.

O **R² ajustado negativo (-0,005)** completa o quadro: as oito variáveis **juntas** explicam menos
que nada da nota. Prever a nota usando todas elas erra mais do que chutar "3" para todo mundo.

É como investigar por que alguns alunos passaram na prova e descobrir que estudar, dormir e ir às
aulas não fazem diferença nenhuma. A conclusão não é "achei uma causa fraca" — é **"essa nota não
está medindo nada"**.

**Mediana em vez de média.** A média se deixa enganar por extremos: um ticket parado 300 horas puxa a
média e faz a operação inteira parecer lenta. A mediana pega quem está no meio da fila.
**Mediana de 6,3 horas** significa que metade dos atendimentos termina em até 6h30. **P90 de 16
horas** significa que 9 em cada 10 terminam em até 16h. A mediana conta o dia normal; o P90 conta a
experiência do cliente que teve azar, e é sobre ele que se escrevem metas de SLA.

**Premissas de custo isoladas.** Marcou cada uma como externa à base: R$ 50/hora, jornada de 8h e — a
mais relevante — 10% do tempo de relógio como trabalho ativo.

**Achou algo que eu não tinha visto:** a base não tem data de abertura do ticket. Sem ela, o campo
"tempo de primeira resposta" é um carimbo sem referência, e não há como medir quanto o cliente
esperou para ser atendido pela primeira vez.

### O que eu reprovei

**1. Ranking de gargalo construído sobre 15 tickets.** Ele apontou "chat + prioridade baixa +
problema técnico, 13,2 horas" como a pior combinação, sem destacar o tamanho do grupo:

| Combinação | Tickets | Mediana |
|---|---|---|
| Chat + baixa + técnico | **15** | 13,2 h |
| Telefone + alta + reembolso | **13** | 12,7 h |
| Chat + alta + reembolso | **22** | 12,5 h |

Como a mediana é o valor do meio, ela está sendo decidida pelo 8º caso de 15. Um único ticket
diferente muda o ranking. É afirmar qual bairro tem o pior trânsito da cidade depois de observar 15
carros. **Risco concreto:** o Diretor redireciona time e investimento para um fluxo definido por 15
casos. **Correção imposta:** análise de gargalo para no cruzamento de dois fatores, onde há amostra;
cruzamento triplo só como exploratório, sempre com o número de casos ao lado.

**2. Definição frouxa de desperdício.** *Ticket-hora* é a unidade que soma tempo de espera: três
tickets esperando 2 horas somam 6 ticket-horas. Ele somou tudo que passou da mediana de cada tipo e
chegou a 4.064 ticket-horas, que viram 406 horas de trabalho e R$ 20.321.

O problema: metade dos tickets sempre fica acima da mediana — é da definição de mediana. Até uma
operação impecável geraria "desperdício" nessa conta. **Correção:** usar o P90 como referência, e
desperdício passa a ser o que extrapola o pior caso aceitável.

### A hipótese alternativa que levantei e testei

Antes de aceitar "dado inválido" para os 1.365 tickets resolvidos antes da primeira resposta,
levantei a hipótese operacional: e se o time técnico tivesse resolvido antes de o suporte responder
formalmente? Isso acontece em operações reais.

**Teste 1 — onde está concentrado?** Se fosse operacional, apareceria em problemas técnicos.

| Tipo | % com data invertida |
|---|---|
| Dúvida de produto | 51,8% |
| Dúvida de cobrança | 49,8% |
| Reembolso | 49,0% |
| Cancelamento | 48,6% |
| **Problema técnico** | **47,4%** |

Todos os 13 recortes (tipo, canal e prioridade) entre 47% e 53% — e o tipo técnico com a **menor**
taxa. Uma dúvida de cobrança não é resolvida pelo time técnico antes de o suporte responder.

**Teste 2 — de que tamanho é a inversão?** Se fosse operacional, seriam minutos. Densidade medida, em
tickets por hora de faixa:

| Faixa | Tickets | Densidade |
|---|---|---|
| -1h a 0 | 108 | 108/h |
| -6h a -1h | 494 | 99/h |
| -12h a -6h | 427 | 71/h |
| -18h a -12h | 249 | 41/h |
| -24h a -18h | 87 | 15/h |

Queda em linha reta a partir do zero, nos dois sentidos. Esse formato triangular é a assinatura de
duas datas sorteadas ao acaso dentro da mesma janela e subtraídas uma da outra. Há 87 tickets
"resolvidos" quase um dia antes do primeiro contato — impossível em qualquer operação.

**Conclusão:** trato como dado inválido com evidência, e não por suposição. E o número correto para a
entrega é **49,3% dos tickets que têm data** (1.365 de 2.769), e não "16% do total" — os 16% diluíam
o problema em 8.469 registros, a maioria dos quais sequer tem data.
