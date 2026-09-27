# Resposta final do Codex — robustez e refação

Concluído sem alterar modelo, split, teste congelado, limiares ou números oficiais.

- Método dos grupos: contagem de decisões por frase normalizada distinta, com IC95% de Wilson; pressupõe casos independentes.
- Reformulações: **21/160 erradas = 13,1% (n=160 distintos; IC95% 8,7%–19,2%)**.
- Erros de digitação: **30/160 = 18,8% (n=160; IC95% 13,5%–25,5%)**.
- Textos curtos: **34/104 = 32,7% (n=104; IC95% 24,4%–42,2%)**.
- Mistura de idiomas: **4/104 = 3,8% (n=104; IC95% 1,5%–9,5%)**.
- Fora do escopo: **84/640 = 13,1% (n=640; IC95% 10,7%–16,0%)**.
- Fora do escopo EN: **84/400 = 21,0% (n=400)**; PT: **0/240 = 0,0% (n=240)**, protegido pelo idioma.
- Correção calibrada em **n=308** e medida separadamente: EN caiu de **44/204 = 21,6% para 0/204 = 0,0% (n=204)**; PT permaneceu **0/128 (n=128)**.
- Custo no teste congelado: serviço de **5.510 para 5.460/7.176**, queda de **50 casos e 0,70 p.p. (n=7.176)**.
- A divergência é legítima: **5.527/7.176 = 77,02%** conta a faixa alta do modelo; o serviço exclui **7** textos acima de 5.000 caracteres e **10** pela proteção de idioma, logo `5.527 − 7 − 10 = 5.510`.
- Na Base 1, **2.718/8.469 = 32,1% (n=8.469; IC95% 31,1%–33,1%)** seriam automatizados; isso mede exposição, não acurácia.
- README e proposta foram atualizados; sintéticos ficaram como evidência complementar. A suíte real daquela rodada aprovou **20/20 testes (n=20)** via `unittest`, em **26,654 s**.

Prompt correspondente: [`46-robustez-correcao-prompt.md`](46-robustez-correcao-prompt.md).
