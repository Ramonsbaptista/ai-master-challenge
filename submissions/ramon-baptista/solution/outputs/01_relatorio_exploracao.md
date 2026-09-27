# Exploração dos datasets — etapa 2

## Escopo e separação metodológica

Os datasets foram analisados separadamente. O Dataset 2 é a única fonte indicada para treinar e medir o classificador de tickets internos. O Dataset 1 serve apenas ao diagnóstico operacional de suporte ao consumidor, com sua taxonomia própria. Não foi feita fusão de rótulos, correspondência registro a registro ou criação de uma taxonomia comum.

## Dataset 1 — suporte ao consumidor

Arquivo: `data\customer_support_tickets.csv`. Contém **8,469 linhas e 17 colunas**: identificador do ticket, dados demográficos e de contato, produto e data de compra, tipo/assunto do chamado, descrição, status, resolução, prioridade, canal, tempos e satisfação.

### Faltantes e cardinalidade

| coluna | faltantes | faltantes_pct | valores_unicos_incluindo_na |
|---|---|---|---|
| Ticket ID | 0 | 0.00 | 8469 |
| Customer Name | 0 | 0.00 | 8028 |
| Customer Email | 0 | 0.00 | 8320 |
| Customer Age | 0 | 0.00 | 53 |
| Customer Gender | 0 | 0.00 | 3 |
| Product Purchased | 0 | 0.00 | 42 |
| Date of Purchase | 0 | 0.00 | 730 |
| Ticket Type | 0 | 0.00 | 5 |
| Ticket Subject | 0 | 0.00 | 16 |
| Ticket Description | 0 | 0.00 | 8077 |
| Ticket Status | 0 | 0.00 | 3 |
| Resolution | 5700 | 67.30 | 2770 |
| Ticket Priority | 0 | 0.00 | 4 |
| Ticket Channel | 0 | 0.00 | 4 |
| First Response Time | 2819 | 33.29 | 5471 |
| Time to Resolution | 5700 | 67.30 | 2729 |
| Customer Satisfaction Rating | 5700 | 67.30 | 6 |

### Distribuições categóricas

| dataset | coluna | valor | quantidade | percentual |
|---|---|---|---|---|
| dataset_1 | Customer Gender | Male | 2896 | 34.20 |
| dataset_1 | Customer Gender | Female | 2887 | 34.09 |
| dataset_1 | Customer Gender | Other | 2686 | 31.72 |
| dataset_1 | Product Purchased | Canon EOS | 240 | 2.83 |
| dataset_1 | Product Purchased | GoPro Hero | 228 | 2.69 |
| dataset_1 | Product Purchased | Nest Thermostat | 225 | 2.66 |
| dataset_1 | Product Purchased | Philips Hue Lights | 221 | 2.61 |
| dataset_1 | Product Purchased | Amazon Echo | 221 | 2.61 |
| dataset_1 | Product Purchased | LG Smart TV | 219 | 2.59 |
| dataset_1 | Product Purchased | Sony Xperia | 217 | 2.56 |
| dataset_1 | Product Purchased | Roomba Robot Vacuum | 216 | 2.55 |
| dataset_1 | Product Purchased | LG OLED | 213 | 2.52 |
| dataset_1 | Product Purchased | Apple AirPods | 213 | 2.52 |
| dataset_1 | Product Purchased | iPhone | 212 | 2.50 |
| dataset_1 | Product Purchased | Sony 4K HDR TV | 210 | 2.48 |
| dataset_1 | Product Purchased | LG Washing Machine | 208 | 2.46 |
| dataset_1 | Product Purchased | Garmin Forerunner | 208 | 2.46 |
| dataset_1 | Product Purchased | Canon DSLR Camera | 206 | 2.43 |
| dataset_1 | Product Purchased | Nikon D | 204 | 2.41 |
| dataset_1 | Product Purchased | Nintendo Switch Pro Controller | 203 | 2.40 |
| dataset_1 | Product Purchased | Google Pixel | 203 | 2.40 |
| dataset_1 | Product Purchased | Sony PlayStation | 202 | 2.39 |
| dataset_1 | Product Purchased | Fitbit Charge | 202 | 2.39 |
| dataset_1 | Product Purchased | Microsoft Office | 200 | 2.36 |
| dataset_1 | Product Purchased | HP Pavilion | 200 | 2.36 |
| dataset_1 | Product Purchased | Dyson Vacuum Cleaner | 198 | 2.34 |
| dataset_1 | Product Purchased | Amazon Kindle | 198 | 2.34 |
| dataset_1 | Product Purchased | Google Nest | 198 | 2.34 |
| dataset_1 | Product Purchased | Bose SoundLink Speaker | 197 | 2.33 |
| dataset_1 | Product Purchased | Autodesk AutoCAD | 196 | 2.31 |
| dataset_1 | Product Purchased | Microsoft Xbox Controller | 196 | 2.31 |
| dataset_1 | Product Purchased | Samsung Galaxy | 194 | 2.29 |
| dataset_1 | Product Purchased | PlayStation | 192 | 2.27 |
| dataset_1 | Product Purchased | Fitbit Versa Smartwatch | 191 | 2.26 |
| dataset_1 | Product Purchased | Microsoft Surface | 190 | 2.24 |
| dataset_1 | Product Purchased | Bose QuietComfort | 190 | 2.24 |
| dataset_1 | Product Purchased | Samsung Soundbar | 188 | 2.22 |
| dataset_1 | Product Purchased | Xbox | 187 | 2.21 |
| dataset_1 | Product Purchased | Asus ROG | 187 | 2.21 |
| dataset_1 | Product Purchased | MacBook Pro | 186 | 2.20 |
| dataset_1 | Product Purchased | Dell XPS | 185 | 2.18 |
| dataset_1 | Product Purchased | GoPro Action Camera | 183 | 2.16 |
| dataset_1 | Product Purchased | Lenovo ThinkPad | 183 | 2.16 |
| dataset_1 | Product Purchased | Adobe Photoshop | 181 | 2.14 |
| dataset_1 | Product Purchased | Nintendo Switch | 178 | 2.10 |
| dataset_1 | Ticket Type | Refund request | 1752 | 20.69 |
| dataset_1 | Ticket Type | Technical issue | 1747 | 20.63 |
| dataset_1 | Ticket Type | Cancellation request | 1695 | 20.01 |
| dataset_1 | Ticket Type | Product inquiry | 1641 | 19.38 |
| dataset_1 | Ticket Type | Billing inquiry | 1634 | 19.29 |
| dataset_1 | Ticket Subject | Refund request | 576 | 6.80 |
| dataset_1 | Ticket Subject | Software bug | 574 | 6.78 |
| dataset_1 | Ticket Subject | Product compatibility | 567 | 6.70 |
| dataset_1 | Ticket Subject | Delivery problem | 561 | 6.62 |
| dataset_1 | Ticket Subject | Hardware issue | 547 | 6.46 |
| dataset_1 | Ticket Subject | Battery life | 542 | 6.40 |
| dataset_1 | Ticket Subject | Network problem | 539 | 6.36 |
| dataset_1 | Ticket Subject | Installation support | 530 | 6.26 |
| dataset_1 | Ticket Subject | Product setup | 529 | 6.25 |
| dataset_1 | Ticket Subject | Payment issue | 526 | 6.21 |
| dataset_1 | Ticket Subject | Product recommendation | 517 | 6.10 |
| dataset_1 | Ticket Subject | Account access | 509 | 6.01 |
| dataset_1 | Ticket Subject | Peripheral compatibility | 496 | 5.86 |
| dataset_1 | Ticket Subject | Data loss | 491 | 5.80 |
| dataset_1 | Ticket Subject | Cancellation request | 487 | 5.75 |
| dataset_1 | Ticket Subject | Display issue | 478 | 5.64 |
| dataset_1 | Ticket Status | Pending Customer Response | 2881 | 34.02 |
| dataset_1 | Ticket Status | Open | 2819 | 33.29 |
| dataset_1 | Ticket Status | Closed | 2769 | 32.70 |
| dataset_1 | Ticket Priority | Medium | 2192 | 25.88 |
| dataset_1 | Ticket Priority | Critical | 2129 | 25.14 |
| dataset_1 | Ticket Priority | High | 2085 | 24.62 |
| dataset_1 | Ticket Priority | Low | 2063 | 24.36 |
| dataset_1 | Ticket Channel | Email | 2143 | 25.30 |
| dataset_1 | Ticket Channel | Phone | 2132 | 25.17 |
| dataset_1 | Ticket Channel | Social media | 2121 | 25.04 |
| dataset_1 | Ticket Channel | Chat | 2073 | 24.48 |
| dataset_1 | Customer Satisfaction Rating | <FALTANTE> | 5700 | 67.30 |
| dataset_1 | Customer Satisfaction Rating | 3.0 | 580 | 6.85 |
| dataset_1 | Customer Satisfaction Rating | 1.0 | 553 | 6.53 |
| dataset_1 | Customer Satisfaction Rating | 2.0 | 549 | 6.48 |
| dataset_1 | Customer Satisfaction Rating | 5.0 | 544 | 6.42 |
| dataset_1 | Customer Satisfaction Rating | 4.0 | 543 | 6.41 |

### Variáveis numéricas

| dataset | coluna | contagem | media | desvio_padrao | minimo | p25 | mediana | p75 | maximo |
|---|---|---|---|---|---|---|---|---|---|
| dataset_1 | Customer Age | 8469 | 44.03 | 15.30 | 18.00 | 31.00 | 44.00 | 57.00 | 70.00 |
| dataset_1 | Customer Satisfaction Rating | 2769 | 2.99 | 1.41 | 1.00 | 2.00 | 3.00 | 4.00 | 5.00 |

### Datas

| coluna | validos | invalidos_nao_faltantes | minimo | maximo |
|---|---|---|---|---|
| Date of Purchase | 8469 | 0 | 2020-01-01 00:00:00 | 2021-12-30 00:00:00 |
| First Response Time | 5650 | 0 | 2023-05-31 21:55:39 | 2023-06-02 00:54:21 |
| Time to Resolution | 2769 | 0 | 2023-05-31 21:53:30 | 2023-06-02 00:55:33 |

### Faltantes por status

| Ticket Status | tickets | Resolution | First Response Time | Time to Resolution | Customer Satisfaction Rating |
|---|---|---|---|---|---|
| Pending Customer Response | 2881 | 2881 | 0 | 2881 | 2881 |
| Open | 2819 | 2819 | 2819 | 2819 | 2819 |
| Closed | 2769 | 0 | 0 | 0 | 0 |

### Duplicatas e qualidade

- Há **0 linhas excedentes exatamente duplicadas** (0 linhas envolvidas) e **0 IDs excedentes duplicados** (0 linhas envolvidas).
- Após normalizar caixa e espaços, há **403 descrições excedentes repetidas**, envolvendo **457 linhas**. Isso limita qualquer interpretação da descrição como relato espontâneo independente.
- **8,469 de 8,469 e-mails (100.00%)** usam os domínios reservados `example.com`, `example.net` ou `example.org` (desses, **2,904** são `example.com`); **0** não passam numa validação sintática simples. Os contatos, portanto, não devem ser tratados como contatos reais.
- Existem **8,469 descrições** e **0 resoluções** com placeholders literais entre chaves (por exemplo, `{product_purchased}`), evidência de texto template não totalmente interpolado.
- Foram encontrados **0 valores de idade fora de 0–120**, **0 avaliações preenchidas fora de 1–5**, **0 datas preenchidas mas não parseáveis**, **0 primeiras respostas anteriores à compra** e **1,365 resoluções anteriores à primeira resposta**.
- A tabela “faltantes por status” mostra se resolução, tempos e satisfação ausentes são estruturais ao ciclo do ticket ou falhas aleatórias; isso deve ser considerado antes de calcular SLAs ou satisfação.

## Dataset 2 — tickets internos de TI

Arquivo: `data\all_tickets_processed_improved_v3.csv`. Contém **47,837 linhas e 2 colunas**: `Document` (texto já processado) e `Topic_group` (rótulo supervisionado).

### Faltantes e cardinalidade

| coluna | faltantes | faltantes_pct | valores_unicos_incluindo_na |
|---|---|---|---|
| Document | 0 | 0.00 | 47837 |
| Topic_group | 0 | 0.00 | 8 |

### Distribuição dos rótulos

| dataset | coluna | valor | quantidade | percentual |
|---|---|---|---|---|
| dataset_2 | Topic_group | Hardware | 13617 | 28.47 |
| dataset_2 | Topic_group | HR Support | 10915 | 22.82 |
| dataset_2 | Topic_group | Access | 7125 | 14.89 |
| dataset_2 | Topic_group | Miscellaneous | 7060 | 14.76 |
| dataset_2 | Topic_group | Storage | 2777 | 5.81 |
| dataset_2 | Topic_group | Purchase | 2464 | 5.15 |
| dataset_2 | Topic_group | Internal Project | 2119 | 4.43 |
| dataset_2 | Topic_group | Administrative rights | 1760 | 3.68 |

### Comprimento do texto processado

| unidade | count | mean | std | min | 25% | 50% | 75% | max |
|---|---|---|---|---|---|---|---|---|
| palavras | 47837.00 | 43.60 | 56.74 | 2.00 | 17.00 | 26.00 | 46.00 | 981.00 |
| caracteres | 47837.00 | 291.88 | 388.17 | 7.00 | 110.00 | 175.00 | 304.00 | 7015.00 |

### Duplicatas e qualidade

- Não foram encontradas linhas exatamente duplicadas (**0 excedentes; 0 envolvidas**).
- Não foram encontrados documentos repetidos após normalizar caixa e espaços (**0 excedentes; 0 linhas envolvidas**). Portanto, não há evidência desse tipo específico de vazamento no arquivo atual.
- Não foram encontrados textos normalizados com mais de um rótulo (**0 textos; 0 linhas afetadas**). Isso não prova que toda anotação esteja correta; apenas afasta conflitos diretamente observáveis entre textos idênticos.
- Há **0 documentos vazios após remover espaços**. Esses registros não carregam sinal textual utilizável.
- O campo `Document` já está fortemente processado (minúsculas/termos separados, sem o ticket bruto nem metadados operacionais). Assim, a análise mede o corpus entregue, não a qualidade ou fidelidade do texto original.

## O que os dados permitem concluir

### Dataset 1

- Descrever volume e composição dos tickets pelas categorias existentes: produto, tipo, assunto, prioridade, canal, status, demografia e satisfação registrada.
- Quantificar faltantes e verificar como eles se distribuem por status.
- Medir intervalos de tempo entre compra, primeira resposta e resolução nos registros em que ambas as datas necessárias existem, ressalvadas as inconsistências apontadas.
- Identificar associações descritivas dentro desta amostra, como diferenças de satisfação ou tempo por produto/canal/tipo. Associação não implica causalidade.

### Dataset 2

- Medir o desbalanceamento das oito classes internas e construir uma avaliação estratificada do classificador.
- Treinar um classificador para **esses oito rótulos**, usando o texto processado disponível.
- Definir uma divisão estratificada de treino e teste; no arquivo atual, não há textos normalizados repetidos que exijam agrupamento especial.
- Comparar modelos sob uma mesma política de validação e métricas adequadas ao desbalanceamento (por exemplo, macro-F1 e métricas por classe).

## O que os dados não permitem concluir

### Dataset 1

- Não permitem inferir desempenho de um classificador para os rótulos do Dataset 2, nem mapear tipos de consumidor para classes internas de TI.
- Não permitem afirmar representatividade de uma população/empresa, tendência temporal real ou causalidade sem informação sobre amostragem, origem e processo de geração.
- Não permitem tratar e-mails como contatos reais; todos usam um dos domínios reservados `example.com`, `example.net` ou `example.org`.
- Não permitem calcular SLA global sem viés ignorando os tempos faltantes e sua relação com status.
- Não permitem assumir que descrições/resoluções são relatos humanos independentes, devido a templates, placeholders e repetições.

### Dataset 2

- Não permitem avaliar atendimento, SLA, resolução, satisfação, prioridade, canal, cliente ou evolução temporal: essas colunas não existem.
- Não permitem medir generalização para chamados de consumidor, para taxonomias diferentes ou para texto bruto fora do pré-processamento fornecido.
- Não permitem concluir que todos os rótulos são corretos; duplicatas conflitantes mostram ambiguidade/inconsistência observável.
- Não permitem estimar desempenho honesto com divisão aleatória ingênua se textos repetidos cruzarem treino e teste.
- Não permitem explicar por que um ticket ocorreu ou inferir relações causais; o dataset contém apenas texto processado e rótulo.

## Arquivos gerados

- `01_relatorio_exploracao.md`: relatório principal.
- `01_resumo.json`: indicadores principais em formato estruturado.
- `01_perfil_colunas.csv`: faltantes, cardinalidade e exemplos de todas as colunas.
- `01_distribuicoes_categoricas.csv`: distribuições completas das categorias relevantes.
- `01_resumo_numerico.csv`: estatísticas numéricas do Dataset 1.
- `01_resumo_datas_dataset1.csv`: validade e intervalos das datas.
- `01_faltantes_por_status_dataset1.csv`: faltantes operacionais por status.
- `01_duplicatas_textuais_dataset2.csv`: linhas repetidas do corpus para auditoria.
