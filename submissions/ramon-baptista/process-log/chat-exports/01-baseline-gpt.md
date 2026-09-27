# Prompt 1 — disparo inicial para o GPT-5.6 sol (raciocínio baixo)

Enviado em 2026-09-19 via Codex CLI (conta ChatGPT, sem API paga):

```
codex exec -m gpt-5.6-sol -c model_reasoning_effort=low --sandbox workspace-write "<prompt abaixo>"
```

**Por que assim:** o executor recebe apenas o desafio e os dados. Nenhuma orientação de método
(separação treino/teste, matriz de confusão, threshold de confiança, baseline de comparação) foi
dada de propósito. Quero ver como uma IA sem esse contexto ataca o problema, para auditar as
escolhas dela.

---

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
