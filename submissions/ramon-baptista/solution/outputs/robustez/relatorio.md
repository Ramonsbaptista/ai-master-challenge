# Robustez com texto livre

## Teste principal: Base 1

Antes da barreira, **2718/8469 = 32,1% (n=8469; IC95% de Wilson 31,1%–33,1%)** iriam direto. Com a mesma barreira, sem ajuste, ainda vão direto **2651/8469 = 31,3% (n=8469; IC95% 30,3%–32,3%)**.

A barreira **não generaliza** para a Base 1: ela bloqueia apenas uma parcela pequena das decisões automáticas em tickets de outro domínio. A Base 1 não será usada para criar ou recalibrar regra.

Método: remoção literal de `{product_purchased}` nas 8469 descrições e aplicação do serviço completo antes/depois dos cinco padrões congelados. Wilson bilateral de 95% foi escolhido por manter limites válidos; pressupõe tickets independentes. Isto mede exposição, não acurácia, porque a Base 1 não tem rótulos compatíveis com as oito filas.

### Padrões que dispararam

| Padrão congelado | Disparos na Base 1 | Automáticos bloqueados |
|---|---:|---:|
| `\brefund(?:ed|s)?\b` | 155 (n=8469) | 36 (n=2718) |
| `\b(?:billing|charged|chargeback)\b` | 56 (n=8469) | 22 (n=2718) |
| `\b(?:delivery|shipment)\b` | 37 (n=8469) | 8 (n=2718) |
| `\b(?:cancel subscription|cancel my order)\b` | 0 (n=8469) | 0 (n=2718) |
| `\b(?:complaint|complain)\b` | 12 (n=8469) | 3 (n=2718) |

Os bloqueios por padrão somam 69, mas são 67 tickets únicos (n=2.718 antes da barreira), porque dois tickets acionaram mais de um padrão. Método: contagem por padrão e união por ticket; fundamento: evitar dupla contagem.

### Dez tickets que ainda passam direto

| Linha | Fila sugerida | Score não calibrado | Texto |
|---:|---|---:|---|
| 3 | Hardware | 0.636 | I'm facing a problem with my . The is not turning on. It was working fine until yesterday, but now it doesn't respond. 1.8.3 I really I'm using the original charger that came with my , but it's not charging properly. |
| 11 | Hardware | 0.678 | I'm having an issue with the . Please assist. 1-800-799-0808. Product Search: What's New in 2-3-4-5? Report Feedback Customer Service is your best I'm using the original charger that came with my , but it's not charging properly. |
| 12 | Hardware | 0.607 | I'm having an issue with the . Please assist. 4. It is possible that we cannot find some type of text or a product name to identify someone like Mr. Brown. 5. On the I've reviewed the troubleshooting steps on the official support website, but they didn't resolve the problem. |
| 21 | Administrative rights | 0.542 | I'm having an issue with the . Please assist. " -name "Microsoft Surface Pro. " " -version 1.10.2 "1.10.2" " -usage I've checked for any available software updates for my , but there are none. |
| 23 | Administrative rights | 0.632 | I'm having an issue with the . Please assist. (And if need be this time, that could help.) 1.3.2.1 Update my version to 3.0 or more. The issue I'm facing is intermittent. Sometimes it works fine, but other times it acts up unexpectedly. |
| 27 | Administrative rights | 0.675 | I'm encountering a software bug in the . Whenever I try to perform a specific action, the application crashes. Are there any updates or fixes available? On Windows Vista, this is not possible. If you are I've performed a factory reset on my , hoping it would resolve the problem, but it didn't help. |
| 29 | Hardware | 0.625 | I'm having an issue with the . Please assist. Thank you." A statement from the consumer group had been released by Microsoft late on Tuesday afternoon. "The purchase of this product was made using a contract with I'm using the original charger that came with my , but it's not charging properly. |
| 38 | Access | 0.988 | I've forgotten my password for my account, and the password reset option is not working. How can I recover my account? I can reset my password by entering the following: My password still valid: password is expired I've recently updated the firmware of my , and the issue started happening afterward. Could it be related to the update? |
| 40 | Access | 0.612 | I'm having an issue with the . Please assist. I have a new account in the system and a new user. I'm having this issue Error: [System.CollectedMessage.ThrowBack I'm concerned about the security of my and would like to ensure that my data is safe. |
| 43 | Hardware | 0.544 | I'm having an issue with the . Please assist. The product_purchased attribute does not exist on your user's product. This is so that you can configure the I need assistance as soon as possible because it's affecting my work and productivity. |

## Evidência complementar: sintéticos

Os sintéticos são estresse controlado do mesmo gerador, não prova de generalização nem estimativa operacional. Rótulos e hash foram gravados antes da inferência. Como todos os grupos têm menos de 100 encaminhados, as taxas condicionais são exploratórias e não sustentam recomendação; o grupo misto também tem n<30.

No teste congelado, a faixa alta acerta **5187/5527 = 93,85% (n=5527)**; o erro é **340/5527 = 6,15% (IC95% 5,5%–6,8%)**. Método: errado ÷ (errado + certo) apenas na faixa alta; fundamento: mede o risco condicional entre encaminhados.

| Grupo sintético | Errado ÷ encaminhados com barreira | IC95% de Wilson |
|---|---:|---:|
| reformulacoes_8_filas | 21/53 = 39,6% | 27,6%–53,1% (n=53) |
| erros_de_digitacao | 30/64 = 46,9% | 35,2%–58,9% (n=64) |
| textos_curtos | 34/56 = 60,7% | 47,6%–72,4% (n=56) |
| mistura_de_idiomas | 4/9 = 44,4% | 18,9%–73,3% (n=9) |
| fora_do_escopo | não estimável: 0 encaminhados | não aplicável (n=0) |

## Rastreabilidade

- `casos_rotulados.csv`, SHA-256 `6aaa75548afde42f3d876abe6b6f92b56a09821463c11e4f94a1b2aed8a79073`.
- Nenhum modelo, split, teste congelado, limiar, número oficial ou padrão foi alterado.
