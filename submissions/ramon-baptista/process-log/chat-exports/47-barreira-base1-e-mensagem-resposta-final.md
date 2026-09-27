# Resposta final do Codex — barreira na Base 1

Concluído sem alterar modelo, split, teste congelado, limiares, número oficial ou calibração.

- Base 1: **2.718/8.469 = 32,1%** antes (IC95% 31,1%–33,1%) contra **2.651/8.469 = 31,3%** depois (IC95% 30,3%–32,3%). Método: serviço completo antes/depois; Wilson; n=8.469.
- A barreira bloqueou apenas **67/2.718 = 2,5%**. **Não generaliza.** A Base 1 não foi usada para recalibração.
- Padrões: `refund` 155 disparos/36 bloqueios; `billing` 56/22; `delivery` 37/8; cancelamento 0/0; `complaint` 12/3. São 69 acionamentos e 67 tickets únicos devido a duas sobreposições.
- Erro entre encaminhados: reformulações **21/53 = 39,6%**; digitação **30/64 = 46,9%**; curtos **34/56 = 60,7%**; mistos **4/9 = 44,4%**. Método: errado ÷ (errado + certo), Wilson; todos exploratórios por n<100.
- Teste congelado: **340/5.527 = 6,15% de erro**, equivalente a **5.187/5.527 = 93,85% de acerto**; IC95% do erro 5,5%–6,8%.
- O relatório passou a conter os disparos e dez exemplos que ainda seguem direto. README e proposta passaram a afirmar que o modelo se desvia fora do domínio e exige modo sombra; os sintéticos foram rebaixados a complemento.
- LLM ficou apenas como assistência, sem autonomia antes de medição na operação. A suíte real daquela rodada aprovou **20/20 testes (n=20)** via `unittest`.

Prompt correspondente: [`47-barreira-base1-e-mensagem-prompt.md`](47-barreira-base1-e-mensagem-prompt.md).
