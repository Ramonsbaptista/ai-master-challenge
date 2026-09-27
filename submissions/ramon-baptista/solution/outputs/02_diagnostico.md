# Diagnóstico operacional do Dataset 1

## Conclusão executiva

A base mostra um problema de mensuração antes de mostrar um problema operacional comparável. Dos **8.469 tickets**, apenas **1.404 (16,6%)** permitem medir de forma cronologicamente válida o intervalo entre primeira resposta e resolução. Outros **1.365 fechados (49,3% dos fechados)** registram resolução antes da primeira resposta e foram excluídos do cálculo de tempo. Os **5.700 abertos (67,3%)** também foram excluídos porque ainda não têm resolução; tratá-los como zero reduziria artificialmente os tempos.

Nos registros válidos, a resolução leva **6,3 horas na mediana**, **11,4 horas no P75** e **16,0 horas no P90**. A mediana é a medida central principal porque a distribuição tem cauda e valores extremos; a média de **7,6 horas** é mantida apenas para auditoria e não representa o ticket típico.

Não apareceu um fator confiável de satisfação a 5% no modelo multivariado (**0 de 8 variáveis testadas**). Mesmo a maior amplitude ajustada foi de apenas **0,67 ponto** na escala de 1 a 5, em **Product Purchased**. O modelo explica **2,0%** da variação das notas; portanto, a base não sustenta priorizar canal, prioridade, tipo, assunto, produto, gênero ou idade como alavanca de satisfação.

Nos **1.404 tickets válidos**, há **381 ticket-horas de tempo corrido excedente acima do P90 do respectivo tipo**. O P90 foi escolhido como limite de cauda para não selecionar metade dos casos por construção. A medida localiza casos extremos; não mede trabalho de agentes nem economia.

## 1. Onde a operação trava

### Critério de inclusão

- Volume: todos os 8.469 tickets.
- Tempo: somente os 1.404 fechados com primeira resposta e resolução presentes e resolução igual ou posterior à primeira resposta.
- Excluídos do tempo: 5.700 abertos sem desfecho e 1.365 fechados com duração negativa.
- O arquivo não contém data de abertura do ticket. `Date of Purchase` é data da compra e não foi usada como início do atendimento. Logo, não é possível medir espera até a primeira resposta.

### Segmentos com maior mediana

| Recorte | Segmento | Volume total | N válido | Mediana (h) | P90 (h) |
|---|---|---|---|---|---|
| Ticket Channel | Chat | 2073 | 355 | 6,52 | 16,07 |
| Ticket Channel | Social media | 2121 | 348 | 6,43 | 16,92 |
| Ticket Channel | Email | 2143 | 374 | 6,41 | 15,79 |
| Ticket Priority | High | 2085 | 355 | 7,12 | 17,11 |
| Ticket Priority | Low | 2063 | 334 | 7,08 | 16,82 |
| Ticket Priority | Critical | 2129 | 374 | 5,98 | 15,21 |
| Ticket Type | Product inquiry | 1641 | 257 | 6,98 | 15,86 |
| Ticket Type | Refund request | 1752 | 304 | 6,71 | 17,24 |
| Ticket Type | Technical issue | 1747 | 305 | 6,38 | 15,43 |

A tabela completa, inclusive cobertura e taxa de duração inválida por segmento, está em `02_volume_tempos_segmentos.csv`.

### Combinações com piores tempos

Para reduzir rankings instáveis, o cruzamento foi agregado para **canal × tipo**. Entram na conclusão apenas combinações com pelo menos **30 tickets fechados válidos**; as demais permanecem no CSV marcadas como exploratórias e não são ranqueadas aqui.

| Canal | Tipo | Volume total | N válido | Mediana (h) | P75 (h) | P90 (h) |
|---|---|---|---|---|---|---|
| Chat | Cancellation request | 408 | 75 | 7,32 | 11,72 | 15,19 |
| Social media | Refund request | 444 | 66 | 7,26 | 15,19 | 18,92 |
| Email | Refund request | 455 | 95 | 7,12 | 11,46 | 15,70 |
| Email | Product inquiry | 427 | 57 | 7,12 | 10,58 | 12,87 |
| Chat | Product inquiry | 388 | 57 | 7,10 | 9,58 | 14,93 |
| Social media | Technical issue | 465 | 83 | 6,85 | 11,76 | 15,45 |
| Phone | Refund request | 427 | 68 | 6,71 | 11,55 | 15,45 |
| Social media | Product inquiry | 402 | 76 | 6,71 | 10,99 | 16,82 |
| Phone | Technical issue | 421 | 78 | 6,53 | 9,93 | 13,80 |
| Email | Cancellation request | 448 | 85 | 6,28 | 12,05 | 17,36 |

Esses são pontos de investigação, não prova causal. A base não informa equipe responsável, complexidade, escalonamentos, fila nem esforço ativo.

## 2. O que impacta a satisfação do cliente

Foi ajustada uma regressão multivariada da nota de 1 a 5 com canal, prioridade, tipo, assunto, produto, gênero e idade nos 2.769 tickets avaliados. Cada variável categórica foi submetida a teste conjunto de Wald com erros robustos HC3. O tempo foi testado à parte nos 1.404 tickets com cronologia válida, usando `log(1 + horas)` para reduzir a influência da cauda.

| Variável | N | p-valor | Magnitude ajustada (pontos) | Significativo a 5% |
|---|---|---|---|---|
| Ticket Channel | 2769 | 0,29 | 0,13 | False |
| Ticket Priority | 2769 | 0,58 | 0,10 | False |
| Product Purchased | 2769 | 0,66 | 0,67 | False |
| Customer Gender | 2769 | 0,66 | 0,06 | False |
| Ticket Type | 2769 | 0,72 | 0,10 | False |
| Ticket Subject | 2769 | 0,74 | 0,40 | False |
| Customer Age | 2769 | 0,82 | 0,01 | False |
| Tempo entre primeira resposta e resolução | 1404 | 0,91 | -0,01 | False |

Conclusão: **não há evidência estatística suficiente de influência** entre as variáveis observadas e a nota. “Não significativo” não prova efeito zero; indica que, com esta base e este desenho, não há sinal confiável para decisão. As magnitudes ajustadas também são pequenas, e o baixo R² mostra que quase toda a variação permanece sem explicação.

## 3. Tempo corrido excedente

Como não existe tempo de trabalho ativo, a medida defensável é de **tempo corrido excedente**. Para cada tipo de ticket, foi usado o P90 dos casos válidos como limite de cauda; somou-se somente a parcela que o ultrapassa: **381 ticket-horas (n=1.404)**. O arquivo `02_tempo_corrido_excedente.csv` abre o total por tipo. O método pressupõe que o P90 seja uma referência operacional útil; ele identifica extremos relativos, não prova ineficiência.

Horas simultâneas de tickets diferentes se somam como ticket-horas, e parte do intervalo pode ser espera sem trabalho humano. Por isso, esse total não é convertido em horas de trabalho ou reais.

## O que os dados permitem concluir com segurança

- O volume é de 8.469 tickets, distribuível por canal, prioridade e tipo.
- Somente 1.404 tickets sustentam cálculo válido do intervalo entre primeira resposta e resolução.
- Entre esses casos, a mediana é 6,3 horas e o P90 é 16,0 horas.
- As combinações de canal × tipo listadas concentram as maiores medianas observadas sob o corte mínimo de 30 casos válidos; grupos menores são exploratórios.
- As variáveis testadas não apresentam associação estatística confiável com satisfação a 5% neste conjunto.
- Existem 381 ticket-horas acima do P90 do respectivo tipo (n=1.404), uma medida de cauda e não de esforço humano.

## O que os dados não permitem concluir

- Tempo até a primeira resposta, porque não há data de abertura do ticket.
- SLA global dos tickets abertos ou tempo final dos casos ainda não encerrados.
- Causalidade: o desenho é observacional e não controla equipe, fila, complexidade ou escalonamento.
- Horas de trabalho evitáveis, capacidade de equipe ou economia real, porque não há esforço ativo nem custos.
- Que melhorar um canal, prioridade ou tipo elevará satisfação; a nota não mostrou sinal estatístico útil.
- Que o texto descreve clientes reais: descrições têm placeholder e os e-mails usam domínios `example.*`.

## Arquivos produzidos

- `02_volume_tempos_segmentos.csv`: volume, cobertura, inválidos e tempos por canal, prioridade e tipo.
- `02_combinacoes_gargalo.csv`: combinações de canal × tipo, status exploratório e critério de elegibilidade do ranking.
- `02_satisfacao_testes.csv`: testes, p-valores e magnitudes ajustadas.
- `02_tempo_corrido_excedente.csv`: ticket-horas acima do P90 por tipo.
- `02_resumo.json`: indicadores principais para auditoria.
