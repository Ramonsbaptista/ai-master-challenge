# Diagnóstico — Suporte ao Cliente

> Toda afirmação aqui tem uma consulta correspondente em `scripts/00_verificacao_auditoria.sql`.

---

## Abertura (versão para falar, não para ler)

Antes de analisar, eu conferi a base. Duas coisas apareceram.

Primeiro, o desafio fala em 30 mil atendimentos, mas são 8.469. A diferença vem de contar as
linhas do arquivo em vez dos atendimentos: cada texto de cliente tem parágrafos, então um único
ticket ocupa várias linhas.

Segundo, nenhuma das oito variáveis testadas apresentou associação estatisticamente significativa
com a nota nesta base (menor p-valor 0,29; n=2.769 e n=1.404 quando entra o tempo). Isso não prova
efeito zero: mostra que estes dados não sustentam escolher uma alavanca de satisfação, por isso eu
não construí recomendação em cima da nota.

O que a base sustenta é volume, tipo de problema e tempo, e foi com isso que dimensionei o
problema. Para a parte de automação, usei a segunda base, que é íntegra e tem 47 mil chamados
já classificados.

---

## 1. O tamanho real da operação

| O que o brief diz | O que a base tem |
|---|---|
| ~30.000 registros | **8.469 tickets** |
| "texto real de descrição e resolução" | 100% das descrições contêm o placeholder `{product_purchased}` |

O arquivo tem 29.807 linhas de texto, mas cada ticket ocupa várias linhas porque a descrição
escrita pelo cliente tem quebras de parágrafo. Quem conta linha vê 30 mil; quem conta registro
vê 8.469.

Não é má-fé de ninguém — é contagem de linha em vez de contagem de registro. Mas muda a
ordem de grandeza de qualquer cálculo de volume, custo ou economia.

---

## 2. Sobre a satisfação do cliente

A base traz 2.769 avaliações, de 1 a 5, e a média geral é 2,99. O problema é que **essa média
é a mesma em todo lugar**. Testei nove recortes diferentes e a maior variação encontrada foi de
0,2 ponto:

| Recorte | Notas médias |
|---|---|
| **Canal** | chat 3,08 · e-mail 2,96 · telefone 2,95 · redes sociais 2,97 |
| **Prioridade** | crítica 2,96 · alta 2,98 · média 2,98 · baixa 3,05 |
| **Tipo de problema** | reembolso 2,93 · cobrança 3,03 · cancelamento 3,03 · técnico 2,96 · dúvida 3,02 |
| **Tempo de espera** | até 6h 3,00 · 6–12h 3,12 · 12–18h 3,00 · +18h 2,91 |
| **Perfil do cliente** | idade 2,99 a 3,01 · gênero 2,97 a 3,03 |

O que mais chama atenção é o tempo de espera. **O cliente que esperou mais de 18 horas avalia
praticamente igual ao que foi atendido em menos de 6.** Em qualquer operação real, tempo de
espera é o fator que mais derruba nota — e aqui ele não derruba nada.

A distribuição confirma: 553 notas 1, 549 notas 2, 580 notas 3, 543 notas 4 e 544 notas 5.
Quase o mesmo número de clientes furiosos e encantados.

### O que isso impede

Com os dados disponíveis, **não é possível isolar o que gera uma nota alta ou baixa**. Nenhuma
variável puxa a nota para cima ou para baixo. Recomendar "invista no chat porque tem a melhor
nota" seria decidir com base em 0,13 ponto de diferença — ruído. A empresa gastaria dinheiro
atrás de nada.

### A recomendação que vem antes de qualquer outra

O processo de pesquisa de satisfação precisa ser redesenhado antes de virar base de decisão.
Hoje ele produz um número que não reflete a experiência de ninguém. Três ajustes resolveriam:

1. **Pesquisar no momento certo** — logo após o encerramento, enquanto o cliente ainda lembra
   do atendimento.
2. **Perguntar o porquê** — um campo aberto ou motivo escolhido pelo cliente. Nota sozinha não
   diz o que corrigir.
3. **Garantir volume e representatividade** — hoje só 33% dos tickets têm avaliação, e ela só
   aparece depois que o ticket fecha.

Com isso, em um ou dois ciclos a empresa passa a ter uma nota que se move quando o atendimento
melhora ou piora. Aí sim dá para cruzar com canal, tempo e tipo de problema e descobrir onde
agir. **Enquanto a pesquisa não medir nada, qualquer análise de satisfação vai ser um exercício
de encontrar padrão onde não existe.**

---

## 3. Outros problemas de integridade encontrados

| Achado | Número | O que significa |
|---|---|---|
| Resolução registrada antes da primeira resposta | 1.365 tickets (16%) | Impossível na prática: o ticket teria sido resolvido antes de alguém responder |
| Campos vazios de resolução, tempo e nota | 67,3% | **Não é bagunça:** todos os 2.769 tickets fechados estão completos e nenhum ticket aberto tem esses campos. Eles só nascem quando o ticket fecha |
| E-mails de clientes | 100% em `example.com/net/org` | Domínios reservados para documentação |
| Produtos distintos | 42 | — |

O item dos 67,3% merece destaque: à primeira vista parece falha de preenchimento, mas é
comportamento do sistema. Confundir uma coisa com a outra levaria a um plano de ação inútil
("cobrar o time a preencher os campos").

---

## 4. O que esta base permite e não permite

**Permite:**
- Dimensionar volume por canal, tipo de problema e prioridade.
- Medir distribuição de tempos entre os 1.404 tickets fechados com cronologia válida (n=1.404).
- Estimar potencial de automação por categoria de assunto.

**Não permite:**
- Explicar satisfação do cliente (não há sinal).
- Análise de texto que dependa do conteúdo real (as descrições são template).
- Medir reincidência ou retrabalho por cliente (e-mails são fictícios e não há histórico).

---

## 5. Onde o trabalho de automação se apoia

Por causa das limitações acima, o protótipo foi construído e medido sobre a **segunda base**
(47.837 chamados classificados em 8 categorias), que está íntegra: sem nulos, sem duplicatas e
sem rótulos conflitantes.

As duas bases não foram fundidas. Elas são de mundos diferentes — uma é helpdesk interno de TI
(Hardware, Acessos, RH), a outra é consumidor final (reembolso, cancelamento, cobrança). Quatro
das oito categorias da segunda base não existem na primeira, e reembolso/cancelamento não
existem na segunda. Cruzar registro a registro produziria um classificador confiante e errado.

A ponte entre as duas é metodológica: o método validado na base íntegra é o que proponho para o
fluxo real.

---

## 6. Decisão de automação: o que a máquina faz, o que ela recomenda e o que continua humano

A decisão não deve ser tomada apenas pelo nome da categoria do ticket. Um mesmo pedido de
reembolso pode ser simples e totalmente aderente à política ou envolver fraude, exceção e alto
valor. Por isso, a unidade de automação é a **etapa do processo**, combinada com risco,
reversibilidade e confiança.

### Faixa A — automação de ponta a ponta

O sistema executa sem aprovação individual, registra a justificativa e oferece rota de saída para
um atendente.

| Processo | Escopo autorizado | Controle obrigatório |
|---|---|---|
| Receber e validar o ticket | Conferir campos, normalizar texto, detectar idioma e pedir informação ausente | Nunca recusar atendimento por falha do modelo |
| Classificar, priorizar e rotear | Aplicar taxonomia, identificar urgência e encaminhar para a fila correta | Confiança mínima calibrada; abaixo dela, fila humana |
| Consultar e entregar informação padronizada | Status, segunda via, política publicada, instrução conhecida e pergunta frequente | Resposta ancorada em fonte aprovada e atualizada |
| Executar solicitação simples e reversível | Cancelamento ou reembolso dentro de regras objetivas, limite de valor e prazo definidos | Motor de regras determinístico; IA não decide política nem limite |
| Atualizações operacionais | Confirmação de recebimento, pedido de dados, aviso de andamento e pesquisa pós-atendimento | Opt-out e histórico completo no ticket |
| Controle de qualidade dos dados | Impedir datas impossíveis, campos incompatíveis e fechamento incompleto | Validação no momento da gravação |

### Faixa B — colaborador assistido por agentes de IA

A IA prepara o trabalho; o colaborador continua responsável pela decisão e pelo envio ou execução.

| Processo | O que o agente de IA faz | O que o colaborador faz |
|---|---|---|
| Diagnóstico técnico | Resume o caso, busca artigos, propõe testes e próxima melhor ação | Confirma o diagnóstico, adapta a orientação e acompanha o resultado |
| Cobrança fora do padrão | Reconcilia informações, destaca divergências e redige resposta | Valida valores, decide ajuste e autoriza qualquer impacto financeiro |
| Reembolso ou cancelamento com exceção | Verifica critérios, reúne evidências e estima opções | Decide a exceção e autoriza a transação |
| Resposta a reclamação | Resume histórico, identifica sentimento e sugere texto | Aplica contexto, empatia e responsabilidade; envia a resposta |
| Escalonamento | Gera resumo estruturado, linha do tempo e itens pendentes | Confirma gravidade, destino e prioridade |
| Encerramento e documentação | Sugere classificação final, resumo e artigo de conhecimento | Revisa, corrige e aprova o registro |

### Faixa C — execução 100% humana

Permanecem humanas as decisões em que o custo do erro é alto, a política não cobre o caso ou a
relação com o cliente é parte central do trabalho:

- suspeita de fraude, incidente de segurança, privacidade ou exposição de dados;
- ameaça, assédio, risco à integridade, cliente vulnerável ou crise reputacional;
- decisão jurídica, regulatória ou contratual;
- exceção de alto valor ou ação irreversível fora dos limites predefinidos;
- reclamação executiva ou cliente estratégico que exige negociação;
- qualquer caso de baixa confiança, evidência conflitante ou ausência de fonte confiável;
- definição de políticas, limites, base de conhecimento e auditoria do próprio sistema de IA.

“100% humano” significa que a IA não recomenda a decisão nem redige a comunicação. Ela pode,
no máximo, transportar dados e registrar o resultado, sem interpretar o caso.

### Regra de roteamento

Um ticket só entra na Faixa A quando **todas** as condições forem verdadeiras: política explícita,
dados suficientes, ação reversível ou dentro de limite aprovado, fonte vigente, confiança acima do
limiar e nenhum sinal de risco. Se uma condição falhar, vai para a Faixa B. Se houver alto impacto,
exceção relevante, tema sensível ou obrigação legal, vai para a Faixa C.

---

## 7. Benefícios tangíveis e business case

### Benefício comprovável imediatamente: qualidade do dado

Dos 2.769 tickets fechados, **1.365 (49,3%) têm resolução registrada antes da primeira resposta**.
Uma validação determinística no momento da gravação é automação de baixo risco. Se ela prevenir
90% dessas inconsistências, evita **1.229 registros inválidos** e eleva a cobertura de tempos
cronologicamente utilizáveis de **50,7% para 95,1%** dos tickets fechados. Isso não é uma promessa
de IA: é um controle de sistema mensurável sobre um erro observado na base.

### Cenário ilustrativo de capacidade

Como a base não informa tempo ativo por etapa, custo da equipe nem período do volume, o cálculo
abaixo é um **cenário sobre os 8.469 tickets da base**, e não uma economia anual comprovada.

| Faixa | Participação assumida | Tickets | Minutos humanos atuais por ticket | Minutos humanos futuros | Horas economizadas |
|---|---:|---:|---:|---:|---:|
| A — automação de ponta a ponta | 20% | 1.694 | 12 | 2 | 282,3 |
| B — colaborador assistido | 65% | 5.505 | 20 | 13 | 642,3 |
| C — 100% humano | 15% | 1.270 | 35 | 35 | 0,0 |
| **Total** | **100%** | **8.469** | — | — | **924,5** |

Nesse cenário, o esforço cai de **2.914,7 para 1.990,2 horas**, liberando **924,5 horas**, ou
**31,7% da capacidade atual**. Com custo carregado de **R$ 50 por hora**, o benefício bruto é de
**R$ 46,2 mil por ciclo de 8.469 tickets**. O valor líquido é:

`benefício líquido = horas liberadas × custo/hora + perdas evitadas − custo da solução`

Logo, não se deve chamar R$ 46,2 mil de ROI antes de levantar implantação, licenças, inferência,
integração, manutenção e supervisão. O ponto de equilíbrio desse cenário é custo total de solução
igual a R$ 46,2 mil por ciclo.

### Redução de erros humanos

Erros devem ser medidos como ocorrências, e não como percepção. Para cada processo automatizado,
o piloto precisa registrar a taxa atual e a taxa futura na mesma amostra:

`erros evitados = volume elegível × (taxa de erro atual − taxa de erro futura)`

`benefício do erro = erros evitados × (minutos de retrabalho/60 × custo/hora + perda média por erro)`

Exemplo estritamente ilustrativo: em 7.199 tickets das Faixas A e B, reduzir erros de 5% para 2%
evita cerca de **216 erros**. Se cada erro gera 20 minutos de retrabalho a R$ 50/h, são mais
**72 horas** ou **R$ 3,6 mil** preservados. Esse valor deve ficar fora do caso financeiro até que
as duas taxas e o custo médio do erro sejam medidos; também não pode ser somado se o retrabalho já
estiver incluído nos minutos de atendimento, para evitar dupla contagem.

### Indicadores que validam ou derrubam o projeto

O piloto deve comparar grupo assistido/automatizado com grupo de controle durante o mesmo período:

| Indicador | Cálculo | Critério inicial de sucesso |
|---|---|---|
| Horas humanas por 100 tickets | minutos ativos registrados / 60 | redução sem piorar qualidade |
| Taxa de erro | tickets com correção, reabertura ou violação / tickets tratados | menor que o controle |
| Resolução sem humano | tickets concluídos na Faixa A / tickets elegíveis | crescer com taxa de escape estável |
| Taxa de escape | automações que deveriam ter sido escaladas / automações concluídas | abaixo do limite de risco definido |
| Reabertura em 7 dias | tickets reabertos / tickets encerrados | não superior ao controle |
| Tempo de ciclo | encerramento − abertura | redução por faixa e categoria |
| Benefício líquido | economia de trabalho + perdas evitadas − custo total | positivo após estabilização |

Antes do rollout, quatro números precisam ser medidos na operação real: minutos ativos por tipo de
processo, taxa e custo dos erros, percentual elegível em cada faixa e custo total da solução. Uma
amostra de duas a quatro semanas com apontamento simples já transforma este cenário em business
case auditável.
