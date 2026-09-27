Auditoria do Claude sobre a rodada 46, aprovada pelo Ramon. Duas tarefas. Faça sozinho, sem agentes paralelos. Regras do AGENTS.md valem. PROIBIDO alterar modelo, split, teste congelado, limiares, número oficial ou a barreira calibrada (não recalibre olhando a Base 1).

## 1. Medir a barreira "fora do escopo" na Base 1

A queda de 21,6% para 0% foi medida em frases do mesmo gerador que a calibrou, com o mesmo vocabulário; não prova generalização. O teste real é a Base 1 (tickets de clientes, n=8.469, fora das 8 filas).

- Com a barreira ligada (sem nenhum ajuste), quantos dos 2.718 (32,1%) ainda seriam encaminhados direto? Reporte antes × depois, com n e IC95%.
- Mostre quais padrões dispararam e quantas vezes, e 10 exemplos de tickets que ainda passam direto, para entendermos o que a barreira não pega.
- Diga com clareza se a barreira generaliza ou não. Se não generalizar, diga isso sem suavizar; não proponha nova regra ajustada na Base 1 (isso a transformaria em dado de calibração).

## 2. Reescrever a mensagem no README e na proposta

Dado novo que precisa aparecer com honestidade: com texto livre, a proporção de erros entre os tickets que vão direto sobe muito em relação ao teste oficial. Calcule por grupo, a partir dos resultados reais: errado ÷ (errado + certo) entre os encaminhados automaticamente, com n e IC95%. Compare com o teste congelado (faixa alta: 93,85% de acerto, n=5.527).

Mensagem central, no tom do README aprovado (frases curtas, cena concreta, sem jargão):
"O modelo é bom no domínio em que foi treinado e se desvia fora dele. Por isso a proposta não liga a automação direto: começa em modo sombra, com tickets reais, e só automatiza depois de medir."
- Base 1 como prova principal (dado real); sintéticos como complemento, com a limitação declarada.
- Ligar explicitamente esse achado aos critérios go/no-go do piloto que já existem na proposta.
- Não esconder nem dramatizar. Não mudar números oficiais.
- Atualize também a seção "Onde entra LLM e onde não" se o achado mudar alguma linha da tabela.

## Ao final, em até 20 linhas
Base 1 antes × depois da barreira, se generaliza, a taxa de erro entre automatizados por grupo, o que mudou no README e na proposta, e o resultado real da suíte de testes.
