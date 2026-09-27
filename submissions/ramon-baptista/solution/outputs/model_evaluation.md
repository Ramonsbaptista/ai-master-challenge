# Avaliação congelada do protótipo

Método: TF-IDF + regressão logística; hiperparâmetros escolhidos por macro-F1 na validação. Teste n=7176, usado uma única vez e reproduzido por IDs congelados.

## Matriz de confusão

Linhas = classe real; colunas = classe prevista. Ordem: Access, Administrative rights, HR Support, Hardware, Internal Project, Miscellaneous, Purchase, Storage.

```text
937	5	35	50	7	30	2	3
0	226	6	27	0	2	0	3
28	7	1408	86	19	68	4	17
36	44	89	1721	19	94	17	23
2	0	11	12	285	8	0	0
8	5	42	65	16	914	4	5
3	4	7	17	1	6	332	0
5	5	6	12	1	9	1	377
```

Checagem: a soma total da matriz é 7176 e bate com n=7176; cada linha foi validada contra o n real da classe.

## Métricas por classe

| Classe | n | VP | FP | FN | VN | Precisão = VP/(VP+FP) | Recall = VP/(VP+FN) | Especificidade = VN/(VN+FP) | F1 = 2PR/(P+R) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Access | 1069 | 937 | 82 | 132 | 6025 | 937/(937+82)=91,95% | 937/(937+132)=87,65% | 6025/(6025+82)=98,66% | 2×0.919529×0.876520/(0.919529+0.876520)=89,75% |
| Administrative rights | 264 | 226 | 70 | 38 | 6842 | 226/(226+70)=76,35% | 226/(226+38)=85,61% | 6842/(6842+70)=98,99% | 2×0.763514×0.856061/(0.763514+0.856061)=80,71% |
| HR Support | 1637 | 1408 | 196 | 229 | 5343 | 1408/(1408+196)=87,78% | 1408/(1408+229)=86,01% | 5343/(5343+196)=96,46% | 2×0.877805×0.860110/(0.877805+0.860110)=86,89% |
| Hardware | 2043 | 1721 | 269 | 322 | 4864 | 1721/(1721+269)=86,48% | 1721/(1721+322)=84,24% | 4864/(4864+269)=94,76% | 2×0.864824×0.842389/(0.864824+0.842389)=85,35% |
| Internal Project | 318 | 285 | 63 | 33 | 6795 | 285/(285+63)=81,90% | 285/(285+33)=89,62% | 6795/(6795+63)=99,08% | 2×0.818966×0.896226/(0.818966+0.896226)=85,59% |
| Miscellaneous | 1059 | 914 | 217 | 145 | 5900 | 914/(914+217)=80,81% | 914/(914+145)=86,31% | 5900/(5900+217)=96,45% | 2×0.808134×0.863078/(0.808134+0.863078)=83,47% |
| Purchase | 370 | 332 | 28 | 38 | 6778 | 332/(332+28)=92,22% | 332/(332+38)=89,73% | 6778/(6778+28)=99,59% | 2×0.922222×0.897297/(0.922222+0.897297)=90,96% |
| Storage | 416 | 377 | 51 | 39 | 6709 | 377/(377+51)=88,08% | 377/(377+39)=90,62% | 6709/(6709+51)=99,25% | 2×0.880841×0.906250/(0.880841+0.906250)=89,34% |

Fundamento: métricas one-vs-rest por classe; macro-F1 dá peso igual a cada classe, F1 ponderado usa o n real de cada classe e acurácia é a diagonal sobre o total.

## Modelo versus baseline

| Método | n | Macro-F1 | F1 ponderado | Acurácia |
|---|---:|---:|---:|---:|
| Modelo | 7176 | 86,51% | 86,44% | 86,40% |
| Baseline (classe majoritária: Hardware) | 7176 | 5,54% | 12,62% | 28,47% |

## Roteamento por score do modelo

Cortes escolhidos apenas na validação: baixa < 0.522100; média de 0.522100 a < 0.539603; alta >= 0.539603.

Premissas operacionais: n>=100 por faixa, alta com acerto >=90%, média >=75%, monotonicidade; maximização da cobertura alta e depois média. O score não é calibrado.

| Faixa | n | Cobertura | Taxa de acerto |
|---|---:|---:|---:|
| baixa | 1511 | 21,06% | 60,36% |
| media | 138 | 1,92% | 73,19% |
| alta | 5527 | 77,02% | 93,85% |

Fundamento: cobertura é n da faixa/n do teste; taxa de acerto é predições corretas/n da faixa. Os cortes não foram ajustados no teste.
