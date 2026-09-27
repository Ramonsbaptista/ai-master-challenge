-- Verificação independente dos achados da exploração
-- Auditor: Ramon Baptista | Base: Supabase, tabelas g4_customer_support_tickets e g4_it_tickets
-- Cada consulta prova (ou derruba) uma afirmação feita pelo executor.
-- Resultados obtidos em 2026-09-19 anotados como comentário ao lado de cada bloco.

-- ============================================================
-- DATASET 1 — customer_support_tickets (consumidor final)
-- ============================================================

-- 1) Quantos tickets existem de fato?
-- RESULTADO: 8.469 (e não os ~30.000 do enunciado; o arquivo tem 29.807 LINHAS
-- porque o texto das descrições contém quebras de linha)
select count(*) as total_tickets from g4_customer_support_tickets;

-- 2) Os 67,3% de campos vazios
-- RESULTADO: 67.3% em resolution, time_to_resolution e customer_satisfaction_rating
select
  round(100.0*count(*) filter (where resolution is null)/count(*),1)                     as pct_sem_resolucao,
  round(100.0*count(*) filter (where time_to_resolution is null)/count(*),1)             as pct_sem_tempo,
  round(100.0*count(*) filter (where customer_satisfaction_rating is null)/count(*),1)   as pct_sem_nota
from g4_customer_support_tickets;

-- 3) O vazio é estrutural, não bagunça?
-- RESULTADO: 2.769 fechados, todos completos; nenhum ticket aberto tem resolução.
-- Ou seja: o campo só existe depois que o ticket fecha.
select ticket_status,
       count(*)                                                        as tickets,
       count(*) filter (where resolution is not null)                  as com_resolucao,
       count(*) filter (where customer_satisfaction_rating is not null) as com_nota
from g4_customer_support_tickets
group by 1 order by 2 desc;

-- 4) Dado impossível: resolvido ANTES da primeira resposta
-- RESULTADO: 1.365 registros (16,1% do total)
select count(*) as resolucao_antes_da_1a_resposta
from g4_customer_support_tickets
where time_to_resolution < first_response_time;

-- 5) O texto é gerado, não real: placeholder nunca substituído
-- RESULTADO: 8.469 de 8.469 (100%)
select count(*) filter (where ticket_description like '%{product_purchased}%') as com_placeholder,
       count(*) as total
from g4_customer_support_tickets;

-- 6) E-mails de domínio reservado
-- RESULTADO: 8.469 de 8.469 (100%) em example.com / example.net / example.org
select count(*) filter (where customer_email ~ '@example\.(com|net|org)$') as emails_example,
       count(*) as total
from g4_customer_support_tickets;

-- 7) Quantos produtos distintos
-- RESULTADO: 42
select count(distinct product_purchased) as produtos_distintos from g4_customer_support_tickets;

-- 8) A nota de satisfação tem sinal ou é sorteio?
-- RESULTADO: 553 / 549 / 580 / 543 / 544 sobre 2.769 avaliações — distribuição
-- praticamente uniforme, compatível com valor aleatório.
select customer_satisfaction_rating as nota, count(*) as qtd
from g4_customer_support_tickets
where customer_satisfaction_rating is not null
group by 1 order by 1;

-- 9) A nota muda por canal? E por prioridade?
-- Se todas as médias ficarem coladas em 3,0, nenhuma das duas variáveis explica satisfação.
select ticket_channel,
       count(*) filter (where customer_satisfaction_rating is not null) as avaliados,
       round(avg(customer_satisfaction_rating),2)                        as nota_media
from g4_customer_support_tickets group by 1 order by 1;

select ticket_priority,
       count(*) filter (where customer_satisfaction_rating is not null) as avaliados,
       round(avg(customer_satisfaction_rating),2)                        as nota_media
from g4_customer_support_tickets group by 1 order by 1;

-- ============================================================
-- DATASET 2 — it_tickets (helpdesk de TI, rotulado)
-- ============================================================

-- 10) Total, nulos, duplicatas e conflitos de rótulo
-- RESULTADO: 47.837 textos; 0 nulos; 0 duplicatas; 0 textos com rótulos divergentes
with norm as (select lower(btrim(document)) as doc, topic_group from g4_it_tickets)
select
  (select count(*) from g4_it_tickets)                                                    as total,
  (select count(*) from g4_it_tickets where document is null or btrim(document)='')       as vazios,
  (select count(*) from g4_it_tickets where topic_group is null)                          as sem_rotulo,
  (select count(*) from (select doc from norm group by doc having count(*)>1) a)          as duplicatas,
  (select count(*) from (select doc from norm group by doc
                          having count(distinct topic_group)>1) b)                        as rotulos_conflitantes;

-- 11) Desbalanceamento entre categorias
-- RESULTADO: Hardware 28,47% (13.617) até Administrative rights 3,68% (1.760) — 7,7x de diferença
select topic_group,
       count(*)                                              as tickets,
       round(100.0*count(*)/sum(count(*)) over (),2)         as pct
from g4_it_tickets group by 1 order by 2 desc;

-- 12) Tamanho dos textos
-- RESULTADO: mediana de 26 palavras
select
  round(percentile_cont(0.5) within group (order by array_length(regexp_split_to_array(btrim(document),'\s+'),1))) as mediana_palavras,
  min(array_length(regexp_split_to_array(btrim(document),'\s+'),1))                                                as min_palavras,
  max(array_length(regexp_split_to_array(btrim(document),'\s+'),1))                                                as max_palavras
from g4_it_tickets;

-- 13) A incompatibilidade entre as taxonomias (o motivo de não fundir os datasets)
-- Dataset 2 tem 8 categorias corporativas; dataset 1 tem 5 categorias de consumidor.
-- Nenhuma correspondência direta: HR Support, Access, Internal Project e Administrative rights
-- (21.919 tickets, 45,8% do dataset 2) não têm equivalente do lado do consumidor.
select ticket_type, count(*) from g4_customer_support_tickets group by 1 order by 2 desc;
