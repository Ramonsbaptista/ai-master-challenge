# Proposta de instrumentação antes da automação

## Decisão recomendada

**Aprovar agora a instrumentação e o modo sombra; não liberar ainda automação com efeito direto no cliente.** A operação tem **8.469 tickets (n=8.469)**, mas não dispõe de um “antes” confiável para provar melhora ou piora. A única nota existente aparece em **2.769 tickets, ou 32,7% do total (n=8.469)**, e nenhuma das **8 variáveis testadas** apresentou associação estatística com ela; o menor p-valor foi **0,29**. Além disso, **1.365 dos 2.769 fechados, ou 49,3% (n=2.769)**, registram resolução antes da primeira resposta.

**Método e fundamento dos números acima:** contagem de tickets e checagem cronológica na Base 1; para satisfação, regressão multivariada com testes de Wald e erros robustos HC3, porque era necessário separar o efeito de cada variável observada. O corte de significância foi **5% (premissa metodológica convencional)**. A nota tem **n=2.769**; o teste de tempo usa apenas cronologias válidas, **n=1.404**. Isso mede associação, não causalidade. A Base 2, com **n=47.837 textos**, serve para treinar e medir classificação; não mede a operação e não foi fundida à Base 1.

A decisão proposta é simples:

1. corrigir os eventos e validações do atendimento;
2. formar baseline de CSAT, CES, IQS e NPS;
3. executar as três faixas de automação em modo sombra, sem ação autônoma;
4. liberar cada faixa somente quando seus marcos forem comprovados.

Os prazos, amostras e limites futuros abaixo são **premissas de governança propostas**, não resultados das bases. Devem ser ratificados pelo Diretor de Operações e pelos responsáveis por Risco, CX e Dados.

## Onde entra LLM e onde não

**LLM para compreensão e assistência; modelo supervisionado para classificação; regras para decisões determinísticas; humano para risco e julgamento.**

Na prática, o ticket passa primeiro por proteções fixas. O classificador escolhe a fila. Uma LLM pode resumir o relato, extrair campos e rascunhar uma resposta para o atendente. Segurança, fraude, jurídico, financeiro, ambiguidade e qualquer ação irreversível continuam com uma pessoa.

O achado principal vem dos tickets da Base 1, de outro domínio (atendimento ao consumidor). Sem a barreira, **2.718/8.469 = 32,1% (n=8.469; IC95% de Wilson 31,1%–33,1%)** iriam direto. Com a barreira ligada, sem nenhum ajuste, ainda vão **2.651/8.469 = 31,3% (n=8.469; IC95% 30,3%–32,3%)**. Ela bloqueia **67/2.718 = 2,5% dos encaminhamentos anteriores (n=2.718)**. Método: proporção do serviço completo antes/depois dos cinco padrões congelados; Wilson foi escolhido por manter limites válidos. Fundamento: mede exposição operacional, não acurácia, pois não há rótulos compatíveis; pressupõe tickets independentes. **A barreira não generaliza para a Base 1** e não será recalibrada com ela. O modelo é bom no domínio em que foi treinado e se desvia fora dele. Por isso a proposta não liga a automação direto: começa em modo sombra, com tickets da operação, e só automatiza depois de medir.

| Etapa | Ferramenta | Por quê | Evidência |
|---|---|---|---|
| Classificar e escolher a fila | TF-IDF + classificador supervisionado | Foi treinado nos rótulos da Base 2 e tem avaliação reproduzível. Seu score atual **não é calibrado**: serve como força relativa, não como probabilidade real de acerto. | **Acurácia de 86,40% (6.200/7.176; n=7.176); macro-F1 de 86,51% (n=7.176)**. Método: acertos/casos rotulados para acurácia e média simples do F1 das oito classes para macro-F1, em avaliação separada do ajuste; fundamento: mede generalização dentro da taxonomia da Base 2 sem apagar classes menores. Sem premissa externa. O Jev teve **38,6% em inglês (n=800)**; como os `n` diferem, é contraste descritivo, não teste pareado. |
| Proteger idioma, acionar kill switch e barrar fora do escopo | Regras fixas, como contenção; não como prova de segurança | Precisam ser auditáveis e fáceis de desligar. A barreira de escopo está construída, mas falhou no teste real de generalização e permanece desligada. | Na Base 1, ela reduziu o envio direto apenas de **2.718 para 2.651 casos (n=8.469)**. Método e fundamento: avaliação antes/depois acima. Sintéticos são apenas complemento e não autorizam automação. |
| Resumir, extrair informações e redigir resposta sugerida | LLM assistida, proposta e não construída | Reduz trabalho de leitura e escrita, mas a pessoa revisa antes de usar. Para tickets em português, a proposta combina LLM com embeddings multilíngues e exige validação em português brasileiro real. | O Jev foi reprovado para triagem em inglês, e o teste traduzido expôs risco de idioma. Não há resultado medido para resumo ou redação nesta rodada; benefício permanece hipótese. |
| Segurança, fraude, jurídico, financeiro, casos ambíguos e ações irreversíveis | Humano obrigatório | Exigem responsabilidade, contexto e julgamento; o custo de erro não é aceitável para decisão autônoma. | Premissa de governança de risco. Mesmo com a barreira, **2.651/8.469 = 31,3% da Base 1 (n=8.469; IC95% 30,3%–32,3%)** iriam direto. Método: serviço completo com a regra congelada; fundamento: mede exposição em outro domínio, não acurácia. |

A barreira foi escolhida em **308 sintéticos (n=308; 196 EN e 112 PT)** e medida em outra metade. A queda de **44/204 = 21,6% para 0/204 = 0,0% em inglês (n=204; IC95% após a regra 0,0%–1,8%)** veio do mesmo gerador e vocabulário; é complemento, não prova de generalização. Método: selecionar padrões apenas na calibração; fundamento: separar escolha e medição naquele conjunto. A Base 1 é a prova principal e contradiz a generalização.

Entre os sintéticos encaminhados automaticamente com a barreira, `errado ÷ (errado + certo)` foi **21/53 = 39,6% nas reformulações (n=53; IC95% 27,6%–53,1%)**, **30/64 = 46,9% com digitação (n=64; IC95% 35,2%–58,9%)**, **34/56 = 60,7% nos curtos (n=56; IC95% 47,6%–72,4%)** e **4/9 = 44,4% nos mistos (n=9; IC95% 18,9%–73,3%)**; fora do escopo não é estimável porque nenhum passou direto (**n=0**). Método: Wilson sobre a taxa condicional entre encaminhados; fundamento: comparar o risco onde há automação. Premissa: sintéticos; todos os grupos têm **n<100** e são exploratórios, e o misto tem **n<30**. No teste congelado, são **340/5.527 = 6,15% de erro e 5.187/5.527 = 93,85% de acerto (n=5.527; IC95% do erro 5,5%–6,8%)** pelo mesmo cálculo.

O número oficial é e permanece **5.527/7.176 = 77,02% na faixa alta (n=7.176)**. A decisão final do serviço é **5.510/7.176 = 76,8% (n=7.176)** porque, entre os casos de faixa alta, **7 excedem o limite de 5.000 caracteres (n=5.527)** e **10 dos 5.520 elegíveis são desviados por idioma (n=5.520)**: `5.527 − 7 − 10 = 5.510`. Com a correção, o serviço cai para **5.460/7.176 = 76,1% (n=7.176)**, custo de **50 casos e 0,70 p.p.** Método: decomposição exata das barreiras e aplicação da regra ao teste congelado; fundamento: distinguir cobertura técnica de decisão operacional. A opção `TICKET_CLASSIFIER_ROBUSTNESS_GUARD` permanece desligada para decisão do Ramon.

## 1. Diagnóstico do instrumento de medição

Hoje a empresa não consegue responder, com evidência, se uma mudança melhorou o atendimento:

| Problema de negócio | Evidência observada | Consequência para a decisão |
|---|---|---|
| A nota existente não reage às condições do atendimento | Nenhuma das **8 variáveis** foi significativa; menor p-valor **0,29**. Método: testes de Wald HC3 em **n=2.769**, salvo tempo em **n=1.404**; fundamento: testar associação ajustada, sem alegar causalidade. | Uma nota maior ou menor não pode ser atribuída com segurança a canal, prioridade, tipo ou tempo. |
| A cobertura da nota é parcial | **2.769 avaliações em 8.469 tickets: 32,7% (n=8.469)**. Método: proporção simples; fundamento: medir cobertura do instrumento. | Não se conhece o viés de quem responde versus quem não responde. |
| O relógio operacional está quebrado | **1.365 cronologias inválidas entre 2.769 fechados: 49,3% (n=2.769)**. Método: resolução anterior à primeira resposta; fundamento: essa sequência é impossível no processo descrito. | Quase metade dos fechados não sustenta comparação de tempo. |
| Falta o início do atendimento | A Base 1 não contém data/hora de abertura; **n=8.469 inspecionados**. Método: auditoria de campos; fundamento: sem o evento inicial não há tempo até primeira resposta nem ciclo completo. | SLA de primeira resposta e tempo total de ciclo não são mensuráveis. |
| O texto não permite medir qualidade real da conversa | **100% das descrições contêm `{product_purchased}` (n=8.469)** e **100% dos e-mails usam domínio `example.*` (n=8.469)**. Método: varredura de conteúdo; fundamento: placeholders e domínios reservados indicam conteúdo não utilizável para inferência sobre clientes reais. | Não é possível validar empatia, aderência textual ou reincidência de clientes com essa base. |
| Não existem CES, IQS ou NPS | **0 campos dedicados às três métricas nos esquemas inspecionados (n=2 bases)**. Método: auditoria de schema; fundamento: uma métrica ausente não pode ser reconstruída de outra nota. | Eficiência pode subir enquanto esforço, qualidade ou lealdade pioram sem que a empresa perceba. |

Conclusão de negócio: automatizar agora permitiria medir execução, mas não efeito. O tratamento começaria sem exame de entrada.

## 2. Plano das quatro métricas

### Desenho de coleta

| Métrica | Evento e momento | Pergunta ou regra exata | Registro obrigatório | Amostra mínima e baseline | Dono |
|---|---|---|---|---|---|
| **CSAT — satisfação com o atendimento** | Disparo no evento `Resolved`, separado de `Closed`; envio entre **15 minutos e 2 horas** depois. **Premissa operacional:** essa janela busca reduzir esquecimento sem confundir resolução com fechamento administrativo; deve ser validada no piloto e não elimina viés. | “De **1 a 5**, quão satisfeito(a) você ficou com a solução deste atendimento?” + “Qual foi o principal motivo da sua nota?” | `ticket_id`, `customer_id_hash`, `resolved_at`, `closed_at`, envio, resposta, nota **1–5**, motivo, comentário, canal, tipo, prioridade, faixa de automação, houve humano, reabertura em **7 dias**, versão da pesquisa. | **≥100 respostas por segmento principal e ≥4 semanas**, o que ocorrer por último. **Premissa:** canal e tipo serão analisados separadamente, não em cruzamento; **n=100** é política de estabilidade e dá margem conservadora de **±9,8 p.p.** para proporções a **95%**, não para a média CSAT. | Head de CX; operação garante o disparo; Dados audita. |
| **CES — esforço para resolver** | Mesmo convite do CSAT, após solução; não coletar em ticket apenas “fechado administrativamente”. | “De **1 a 7**, quanto você concorda: foi fácil resolver meu problema neste atendimento?” + motivo. | Campos do CSAT, nota **1–7**, número de contatos, transferências, reaberturas, tempo ativo do cliente quando disponível, abandono e motivo. | **≥100 respostas por segmento principal e ≥4 semanas**. **Premissa e fundamento:** mesmo piso do CSAT para comparação consistente; recortes com **n<30** ficam exploratórios e não autorizam decisão. | Head de CX com Operações. |
| **IQS — Índice de Qualidade do Serviço** | Auditoria após encerramento, antes de qualquer comunicação automática ganhar autonomia; amostra aleatória semanal, estratificada por faixa. | Checklist binário: “diagnóstico correto?”, “política correta?”, “resposta completa?”, “tom adequado?”, “registro completo?”, “escalou quando deveria?”. **IQS = itens conformes / itens aplicáveis × 100.** | `ticket_id`, auditor, data, faixa, etapa, itens aplicáveis, resultado por item, falha crítica, evidência, versão da rubrica, concordância entre auditores e correção exigida. | **≥100 tickets auditados por faixa candidata e ≥4 semanas**. **Premissa:** checklist com **6 itens** de igual peso; fundamento: taxa de conformidade não melhora automaticamente numa operação perfeita — tende a **100%** por aderência real, e falha crítica permanece visível. | Qualidade/Compliance, independente do time que constrói a automação. |
| **NPS — lealdade relacional** | Pesquisa relacional separada, enviada **30 dias** após o encerramento ou em onda trimestral; no máximo um convite por cliente por trimestre. | “Em uma escala de **0 a 10**, qual a probabilidade de você recomendar a empresa a um amigo ou colega?” + “Qual o principal motivo da sua nota?” | `customer_id_hash`, elegibilidade, envio, resposta, nota **0–10**, motivo, produto, segmento de cliente, histórico agregado de contatos, exposição à automação e versão da pesquisa. | **≥400 respostas no total e ≥6 semanas**; segmentos só são publicados com **n≥100**. **Premissa:** **n=400** dá margem conservadora de **±4,9 p.p.** a **95%** para uma proporção; a incerteza do NPS deve ser calculada por bootstrap. | Diretor de CX/Marketing; Dados calcula e Operações recebe o corte por exposição. |

**Regra comum:** baseline só é utilizável quando o piso de amostra e o prazo forem atingidos. Se não forem, a coleta continua. Todo agregado mostra seu **n**; recorte com **n<30** é exploratório, e nenhum ranking ou liberação será baseado nele. Para CSAT e CES, a métrica principal será a média da escala original com intervalo de confiança; converter a nota em faixas seria perda de informação e não a transforma em NPS.

### Como a comparação será feita

Cada mudança será comparada a um controle contemporâneo, por etapa e população elegível. O método preferido é sorteio entre controle e tratamento; quando isso não for operacionalmente possível, usa-se implantação escalonada com ajuste pelas características registradas. O fundamento é separar efeito da mudança de sazonalidade, mix de tickets e evolução da equipe. A unidade de análise é o ticket; respostas repetidas do mesmo cliente serão identificadas pelo `customer_id_hash`.

## 3. Camada de dados a corrigir antes

| Campo/evento obrigatório | Validação no momento da gravação | Por que é necessário |
|---|---|---|
| `ticket_created_at` | UTC, obrigatório, imutável e anterior aos eventos seguintes | Inicia o relógio de espera e de ciclo. |
| `first_response_at` | Não pode anteceder `ticket_created_at`; distinguir resposta automática de humana | Evita chamar confirmação automática de atendimento real. |
| `resolved_at` e `closed_at` | `resolved_at ≥ first_response_at ≥ ticket_created_at`; fechamento exige motivo e solução registrada | Impede duração negativa e fechamento vazio. |
| `reopened_at` | Deve suceder fechamento; preservar todas as ocorrências | Mede solução que não se sustentou. |
| `agent_work_started_at` / `agent_work_ended_at` | Pares completos, sem sobreposição para o mesmo agente; pausas classificadas | Separa tempo ativo de tempo corrido. |
| `queue_id`, `agent_id`, transferências e escalonamentos | Identificadores válidos e histórico append-only | Localiza fila, retrabalho e passagem de bastão. |
| tipo, assunto, prioridade e motivo final | Vocabulário versionado; motivo final obrigatório; guardar rótulo sugerido e aprovado | Permite medir erro de classificação e mudança de taxonomia. |
| `automation_band`, `model_version`, confiança, fontes e regra aplicada | Obrigatório para toda recomendação ou execução; log imutável | Torna cada decisão auditável e reversível. |
| consentimento, envio e resposta das pesquisas | Idempotência por evento; opt-out; versão da pergunta | Evita duplicidade e permite calcular taxa de resposta. |
| `customer_id_hash` | Chave pseudonimizada estável; acesso controlado | Mede recorrência sem expor identidade na análise. |

A validação cronológica sozinha já entrega ganho mensurável: ela passa a **bloquear** um erro observado, conta tentativas rejeitadas e mostra a taxa residual. No cenário em que previne pelo menos **90% das 1.365 inconsistências (premissa de eficácia; n=1.365)**, evita **1.229 registros inválidos** e eleva a cobertura cronologicamente utilizável de **50,7% para 95,1% dos fechados (n=2.769)**. Método: contagem antes/depois sobre os mesmos campos, com arredondamento para cima para cumprir “pelo menos 90%”; fundamento: é um controle determinístico, não uma inferência de IA. O benefício comprovável hoje é a existência de **1.365 erros**; os **1.229 evitados** são cenário e precisam ser confirmados em produção.

## 4. O que anda em paralelo: modo sombra

No modo sombra, o sistema lê o caso e registra o que faria, mas não envia mensagem, altera cadastro, movimenta dinheiro nem encerra ticket. A comparação usa a decisão humana real como referência e auditoria independente para casos em que o humano também pode errar.

| Faixa | Etapas do processo | Atuação em sombra | O que será medido |
|---|---|---|---|
| **A — ponta a ponta** | Receber/validar; classificar/priorizar/rotear; responder informação padronizada; executar solicitação simples e reversível; atualizar cliente; validar dados | Simular decisão e execução, registrar fontes, regra, confiança e rota de saída; nenhuma ação chega ao cliente | Elegibilidade; acerto de rota e resposta; cobertura; falso fechamento; falha crítica; taxa de escape; reabertura em **7 dias**; tempo humano evitável; CSAT, CES e IQS do controle. **Premissa:** janela de reabertura de 7 dias. |
| **B — colaborador assistido** | Diagnóstico técnico; cobrança fora do padrão; exceção de reembolso/cancelamento; reclamação; escalonamento; encerramento/documentação | Gerar sugestão invisível ao agente na primeira fase; depois medir aceite e edição quando a assistência for habilitada sem execução autônoma | Precisão e completude; aceitação; percentual editado; tempo ativo; erro/retrabalho; escalonamento correto; IQS; CSAT e CES. |
| **C — 100% humano** | Fraude, segurança, privacidade, ameaça, vulnerabilidade, jurídico/regulatório, alto valor, ação irreversível, crise e baixa confiança | Apenas detectar e encaminhar; não recomendar decisão nem redigir comunicação | Sensibilidade de detecção de risco; falso negativo; tempo até fila especializada; completude do registro; aderência ao protocolo e IQS. |

As faixas são decididas por **etapa**, não pelo assunto do ticket. Um reembolso aderente a regra objetiva pode ter uma etapa automatizável; uma exceção financeira continua humana. Isso evita autorizar um ticket inteiro apenas porque sua categoria parece simples.

## 5. Marcos que autorizam automatizar

Os limites abaixo são **premissas de governança iniciais**. Foram escolhidos para tornar a decisão verificável; não vêm das bases e devem ser recalibrados depois do baseline.

### Marco comum — dados aptos

Liberar piloto somente quando, por **4 semanas consecutivas**:

- campos obrigatórios estiverem completos em **≥95% dos tickets elegíveis** e cronologias inválidas forem **<1% (n informado em cada semana)**;
- CSAT, CES e IQS tiverem atingido seus pisos de amostra; NPS não bloqueia o primeiro piloto transacional, porque é relacional e requer janela maior;
- versão de regra/modelo, fontes, confiança e trilha de auditoria estiverem presentes em **100% das decisões automatizadas (n de decisões)**;
- rollback, fila humana e responsável de plantão tiverem sido testados.

### Liberação por faixa

O desvio observado fora do domínio torna estes marcos obrigatórios, não burocráticos. A taxa sintética alta não substitui a sombra: o go/no-go da Faixa A será calculado em tickets da operação e só haverá automação se **n≥100 por etapa**, acerto auditado **≥95%**, taxa de escape **≤1%** e **0 falhas críticas observadas**, durante **4 semanas**. Esses valores são premissas de governança, não resultados das bases; o fundamento é impedir que o desempenho no domínio de treino seja tratado como desempenho na operação.

| Faixa | Marco objetivo proposto | Decisão autorizada |
|---|---|---|
| **A — ponta a ponta** | No mínimo **4 semanas e n≥100 casos por etapa** em sombra; **0 falhas críticas observadas (n≥100)**; acerto auditado **≥95%**; taxa de escape **≤1%**; reabertura em **7 dias** não pior que controle por mais de **2 p.p.**; CSAT e CES sem piora estatisticamente detectável; IQS não inferior ao controle. | Piloto restrito a **10% do volume elegível por 2 semanas**; ampliar somente se os critérios permanecerem verdadeiros. Todas as quantidades são premissas. “0 observado” não prova risco zero na população. |
| **B — assistido** | No mínimo **4 semanas e n≥100 casos por etapa**; IQS não inferior ao controle; falha crítica não superior ao controle; tempo ativo mediano reduzido em **≥15%**; aceitação da sugestão **≥80%**, sem aumento de reabertura superior a **2 p.p.** | Mostrar sugestão ao colaborador, mantendo aprovação humana obrigatória. Limiares são premissas; mediana é usada para tempo por resistência a caudas. |
| **C — humano** | Detector de risco avaliado em **n≥100 casos rotulados**, incluindo todos os casos críticos disponíveis; **100% dos críticos da amostra detectados** e protocolo de encaminhamento aprovado por Risco/Compliance. | Somente triagem e transporte de dados; decisão e comunicação permanecem humanas. O resultado da amostra não prova sensibilidade perfeita futura. |

Todo contraste terá intervalo de confiança e amostra declarada. “Não piorou” será avaliado por teste de não inferioridade com margens acima, em vez de aceitar ausência de significância como prova de equivalência. Se qualquer falha crítica ocorrer, a etapa retorna ao modo sombra até análise de causa e nova validação.

## 6. Cronograma

**Premissa de implantação:** plano de **8 semanas**, condicionado a acesso aos sistemas e volume suficiente; se a amostra mínima não chegar, o marco desloca, não o critério.

| Semana | Trabalho | Entregável verificável |
|---|---|---|
| **1** | Aprovar definições, donos, taxonomia, rubrica do IQS, eventos e riscos | Dicionário de métricas; RACI; mapa de eventos; limites assinados |
| **2** | Implementar timestamps, IDs, logs e validações cronológicas em ambiente de teste | Contrato de dados; testes automatizados; painel de rejeições |
| **3** | Ativar eventos em produção e iniciar CSAT/CES; treinar auditores de IQS | Coleta versionada; relatório diário de completude; concordância entre auditores |
| **4** | Iniciar NPS relacional e modo sombra das faixas A, B e C | Primeira coorte; painel de sombra; registro de elegibilidade e falhas |
| **5** | Auditar amostra, corrigir regras e testar rollback/escalonamento | Relatório de erros por etapa; plano de correção; evidência de rollback |
| **6** | Fechar primeira janela de CSAT/CES/IQS onde houver amostra; manter NPS | Baseline preliminar com `n`, intervalos e recortes válidos |
| **7** | Avaliar marcos de dados e desempenho; comitê independente decide | Go/no-go por etapa e faixa; exceções documentadas |
| **8** | Se aprovado, piloto restrito da Faixa A e assistência da Faixa B; Faixa C segue humana | Relatório do piloto e plano de expansão ou retorno à sombra |

O prazo mínimo para baseline é, portanto, **4 semanas para CSAT, CES e IQS** e **6 semanas para NPS**, sempre condicionado às amostras definidas. Esses prazos são premissas operacionais, não garantias de volume.

## 7. Benefícios esperados

### Já comprovável com os dados atuais

- **Qualidade de dados:** existem **1.365 cronologias impossíveis, 49,3% dos 2.769 fechados (n=2.769)**. Método: validação `resolved_at < first_response_at`; fundamento: sequência incompatível com o processo. Corrigir o controle elimina a criação de novos erros desse tipo e torna a taxa de rejeição diretamente mensurável.
- **Escopo real conhecido:** a Base 1 tem **8.469 tickets (n=8.469)**, não cerca de 30 mil registros operacionais. Método: parser CSV e contagem de registros; fundamento: quebras de parágrafo não são tickets adicionais.
- **Corpus de classificação disponível:** a Base 2 contém **47.837 textos rotulados (n=47.837)**, sem nulos, duplicatas ou rótulos conflitantes na auditoria executada. Método: contagens de integridade; fundamento: sustenta experimento de classificação dentro de sua própria taxonomia, não desempenho na operação da Base 1.

Isso ainda não prova economia, aumento de satisfação nem redução de esforço.

### Estimável, com premissas declaradas

**Cenários ilustrativos, não previsão:** método = `volume × participação × diferença de minutos / 60`, aplicado aos **8.469 tickets (n=8.469)**; fundamento: converte esforço ativo evitado em capacidade somente se participação e tempos forem confirmados na operação. Todas as participações, minutos e custos abaixo são **premissas externas às bases**.

| Cenário | Premissas: A/B/C; minutos atuais→futuros; custo/h | Horas liberadas (n=8.469) | Benefício bruto (n=8.469) |
|---|---|---:|---:|
| Conservador | 10%/55%/35%; 12/20/35→4/16/35; R$ 40 | 423,4 | R$ 16,9 mil |
| Base | 20%/65%/15%; 12/20/35→2/13/35; R$ 50 | 924,5 | R$ 46,2 mil |
| Favorável | 30%/60%/10%; 14/22/35→1/10/35; R$ 60 | 1.566,8 | R$ 94,0 mil |

Na sensibilidade de **um fator por vez** ao redor do cenário-base, minutos por ticket têm a maior amplitude no benefício bruto: **R$ 43,8 mil (n=8.469)**, ante **R$ 18,5 mil (n=8.469)** para custo/hora e **R$ 16,6 mil (n=8.469)** para participação. O fundamento é isolar cada família de premissas; a conclusão pressupõe os extremos declarados. Benefício bruto não é ROI: ainda faltam implantação, licenças, inferência, integrações, manutenção, supervisão e perdas por erro.

O cenário de controle cronológico também é estimável: prevenir pelo menos **90% das 1.365 inconsistências (premissa; n=1.365)** evitaria **1.229 registros inválidos** e levaria a cobertura utilizável a **95,1% dos fechados (n=2.769)**. A produção deve confirmar a eficácia real.

### Só mensurável após a instrumentação

- variação causal de CSAT, CES, IQS e NPS entre controle e tratamento;
- horas humanas efetivamente liberadas, pois hoje não existe tempo ativo por etapa;
- erros evitados, retrabalho, transferências, reabertura e perda financeira por erro;
- taxa real de elegibilidade de cada etapa para as faixas A, B e C;
- benefício líquido e ROI, porque custo total da solução e perdas evitadas não estão nas bases;
- efeito sobre retenção ou receita, porque não há vínculo confiável com histórico do cliente.

## Recomendação final

Autorizar a instrumentação imediatamente e conduzir automação apenas em sombra até os marcos. O primeiro ganho não é “usar IA”: é transformar decisões antes opinativas em decisões reversíveis, comparáveis e auditáveis. A empresa passa a saber o que mudou, para quem mudou, quanto custou e se o cliente ficou melhor ou pior — antes de escalar.

---

### Nota metodológica e rastreabilidade

Os números observados foram recalculados nesta sessão pelos scripts `02_diagnostico.py` e `03_instrumentacao.py`; o segundo grava `outputs/03_instrumentacao_numeros.json`. As duas bases têm papéis separados: Base 1 para diagnóstico operacional (**n=8.469**) e Base 2 para classificação (**n=47.837**). Não houve fusão registro a registro. Prazos, limiares, tamanhos mínimos futuros, janelas e cenário financeiro estão explicitamente marcados como premissas. Resultados com **n<30** são exploratórios; métricas por segmento exigem **n≥100**.
