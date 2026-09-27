# Protótipo de classificação de tickets

Classificador reproduzível e auditável. Usa exclusivamente a Base 2; o teste é congelado por IDs e a reprodução nunca refaz o split.

> Limite importante: o modelo foi treinado em **tickets em inglês** e em oito assuntos internos. A proteção de idioma desvia textos com baixa cobertura do vocabulário inglês para análise humana antes de qualquer encaminhamento automático.

## Como testar em 2 minutos

Execute o programa, escolha `1` e copie um exemplo por vez:

1. `My laptop screen is broken and the keyboard does not work`  
   Tradução: *A tela do notebook está quebrada e o teclado não funciona.*  
   Observe: encaminhamento automático para **Equipamentos**, com o risco medido.
2. `I cannot access my account after resetting my password`  
   Tradução: *Não consigo acessar minha conta depois de redefinir a senha.*  
   Observe: encaminhamento automático para **Acesso a sistemas**.
3. `Please grant me administrator rights to install approved software`  
   Tradução: *Conceda permissão de administrador para instalar um software aprovado.*  
   Observe: encaminhamento automático para **Permissões administrativas**.
4. `The order says delivered, but the customer has not received it after 24 hours`  
   Tradução: *O pedido consta como entregue, mas o cliente não o recebeu após 24 horas.*  
   Observe: envio para **uma pessoa analisar**. Entrega não pertence aos oito assuntos de treinamento; evitar uma fila automática é o comportamento desejado.

Cada classificação é acrescentada a `outputs/classification_history.csv` sem guardar o texto do cliente: registra data e hora, SHA-256 do texto, tamanho em caracteres, decisão, categoria, score e faixa. O hash permite correlacionar repetições para auditoria, mas não permite reconstruir o conteúdo. Quando a proteção de idioma atua, a faixa registrada é `protecao_idioma`.

## Executar

Python suportado: 3.11–3.14. Na primeira execução é necessária conexão para baixar dependências.

Windows, a partir da raiz do repositório:

```powershell
.\submissions\ramon-baptista\solution\run.ps1
```

macOS/Linux:

```bash
sh submissions/ramon-baptista/solution/run.sh
```

Os scripts criam `.venv` com `pip` e **sem acesso aos pacotes do sistema**, instalam versões exatas e abrem a interface no endereço mostrado no terminal. O programa prefere `http://127.0.0.1:5000/`, mas escolhe automaticamente outra porta livre se a 5000 estiver ocupada. O navegador só abre depois que o servidor responde. O servidor aceita conexões somente desta máquina. Para manter o menu de terminal anterior, acrescente `--cli` ao comando. Para uma reinstalação limpa, apague somente a `.venv` dentro de `solution/` e execute novamente.

Para publicar a demonstração online, siga [DEPLOY.md](DEPLOY.md). O modo público é separado do modo local e não grava nem mesmo o hash dos textos enviados.

Ligar o kill switch: defina `TICKET_CLASSIFIER_KILL_SWITCH=true` antes de executar; o menu mostrará “Modo de segurança ativo” e todos os tickets irão para análise humana.  
Desligar o kill switch: remova a variável ou defina `TICKET_CLASSIFIER_KILL_SWITCH=false` e execute novamente.

## Testar no Google Colab (Linux)

1. Compacte a raiz `g4-ai-master` como `g4-ai-master.zip`, incluindo `solution/data/` e `solution/artifacts/`.
2. Abra [Google Colab](https://colab.research.google.com/), selecione **Arquivo > Fazer upload de notebook** e envie `solution/colab.ipynb`.
3. Execute as células em ordem e, quando solicitado, envie o ZIP.
4. A célula de teste chama o `run.sh` real com entrada não interativa; o launcher preserva o núcleo/CLI nesse caso, reproduz a avaliação congelada e encerra. Confira `A reprodução passou`. O Colab segue pelo núcleo/CLI porque seu servidor em `127.0.0.1` não é acessível externamente sem adicionar um túnel, dependência que esta entrega offline não usa.
5. Execute a última célula para abrir o menu.

O Colab é temporário. Baixe `outputs/classification_history.csv` antes de encerrar se quiser preservar o histórico.

## Auditoria e reprodução

O `artifacts/manifest.json` registra versões, classes, método, cortes, hashes SHA-256, matriz e métricas. `split_ids.json` guarda os IDs dos conjuntos e `frozen_test.csv`, os resultados esperados. Escolha `2` no menu: primeiro aparece a conclusão executiva; depois, matriz, VP, FP, FN, VN, fórmulas e agregados. Divergências interrompem a avaliação.

## Método e premissas

- Split estratificado 70%/15%/15%, seed `20260922`; preserva prevalências e pressupõe registros independentes.
- Seleção por macro-F1 na validação, em vez de acurácia, porque as classes são desbalanceadas.
- Baseline: classe mais frequente no treino, referência ingênua sem informação do teste.
- Score: maior `predict_proba`; não foi calibrado e aparece somente no detalhe técnico.
- Cortes escolhidos na validação com `n>=100` por faixa, acerto mínimo de 90% na alta e 75% na média e monotonicidade. São premissas operacionais. Apenas a faixa alta encaminha automaticamente; as demais exigem análise humana.
- Todas as classes do teste têm `n>=100`; nenhuma métrica por classe é apenas exploratória.
- Proteção de português: combina marcadores lexicais de inglês/português com cobertura do vocabulário unigram; evidência explícita prevalece sobre cobertura. Os parâmetros (mínimo de 2 marcadores, fallback a partir de 4 tokens e cobertura `<0,85`) foram escolhidos em grade **somente na validação**, minimizando primeiro desvios falsos de inglês e depois português não detectado; esse critério protege o idioma de treinamento. No conjunto total de validação, os erros EN→pessoa passaram de **1 para 0 (n=812 EN)** e os erros PT→fluxo normal de **57 para 14 (n=812 PT)**. Método: contagem exata por rótulo; fundamento: mede diretamente os dois sentidos de falha. Premissas: os rótulos de idioma estão corretos, baixa cobertura é apenas heurística e a amostra balanceada não estima prevalência operacional. O teste congelado não foi usado.
- Validação curta adicional: **12 textos EN e 12 PT (n=12 por idioma)**, portanto resultado **exploratório** por ter n<30. Nela, EN→pessoa caiu de **1 para 0 (n=12)** e PT→fluxo normal de **12 para 0 (n=12)**, pela mesma contagem exata. O conjunto está identificado em `data/language_guard_short_validation.csv` e inclui os exemplos relatados.

## Limitações honestas

O classificador continua sujeito a erros mesmo na faixa alta: “the printer on the third floor is jammed and shows an error light” foi classificado como **HR Support**, com score não calibrado **0,605**. Isso é compatível com o erro observado da faixa alta: acurácia `VP global da faixa/n = 5.187/5.527 = 0,9385`, isto é, cerca de **6,2% de erros (n=5.527)** no teste congelado. O exemplo não foi usado para alterar modelo, split, cortes ou métricas; a premissa operacional permanece que score é confiança relativa, não garantia.

### Proteção experimental de robustez

O teste principal é a Base 1. Sem a barreira, **2.718/8.469 = 32,1% (n=8.469; IC95% de Wilson 31,1%–33,1%)** iriam direto. Com a mesma barreira ligada, sem ajuste, ainda vão **2.651/8.469 = 31,3% (n=8.469; IC95% 30,3%–32,3%)**. Ela bloqueia só **67 dos 2.718 encaminhamentos anteriores = 2,5% (n=2.718)**. Método: remover literalmente `{product_purchased}`, aplicar o serviço completo antes e depois dos cinco padrões congelados e usar Wilson, porque mantém limites válidos para proporções. Fundamento: mede exposição em outro domínio, não acurácia, pois não há rótulos compatíveis; pressupõe tickets independentes. **A barreira não generaliza para a Base 1.** Ela não será recalibrada com esses tickets.

O experimento sintético em [`outputs/robustez/relatorio.md`](outputs/robustez/relatorio.md) é evidência complementar. Após normalização em minúsculas, sem pontuação e sem números, há **160 reformulações, 160 erros de digitação, 104 textos curtos, 104 textos com mistura de idiomas e 640 casos fora do escopo, todos distintos (n por grupo igual a esses totais)**. Nos **400 casos fora do escopo em inglês (n=400)**, **84/400 = 21,0%** foram enviados direto para fila errada; nos **240 em português (n=240)**, **0/240 = 0,0%** foram enviados direto, porque a proteção de idioma desviou todos. Método: rótulo e hash antes da inferência, contagem por grupo e IC95% de Wilson; fundamento: teste controlado de estresse. Limitação: frases geradas por IA podem ser semanticamente correlacionadas e não estimam prevalência operacional.

A queda sintética de **44/204 = 21,6% para 0/204 = 0,0% em inglês (n=204; IC95% após a regra 0,0%–1,8%)** continua registrada, mas é só complemento: veio do mesmo gerador e vocabulário usados na calibração. Método: padrões presentes em pelo menos dois erros automáticos da metade de calibração; fundamento: separar escolha e medição dentro daquele conjunto. A limitação é decisiva: esse resultado não se repetiu nos tickets da Base 1. A barreira segue **desligada por padrão** e não altera modelo, split, teste ou cortes.

Entre os sintéticos que efetivamente iriam direto com a barreira, a taxa `errado ÷ (errado + certo)` foi **21/53 = 39,6% nas reformulações (n=53; IC95% 27,6%–53,1%)**, **30/64 = 46,9% com erros de digitação (n=64; IC95% 35,2%–58,9%)**, **34/56 = 60,7% nos textos curtos (n=56; IC95% 47,6%–72,4%)** e **4/9 = 44,4% nos mistos (n=9; IC95% 18,9%–73,3%)**; fora do escopo ficou não estimável, pois nenhum caso passou direto (**n=0**). Método: erro condicional somente entre encaminhados, com Wilson; fundamento: é a comparação correta com o risco da faixa alta. Premissa: sintéticos do mesmo gerador; todos os grupos têm **n<100** entre encaminhados e são exploratórios, e o grupo misto também tem **n<30**. No teste congelado, o mesmo cálculo dá **340/5.527 = 6,15% de erro, ou 5.187/5.527 = 93,85% de acerto (n=5.527; IC95% do erro 5,5%–6,8%)**. O modelo é bom no domínio em que foi treinado e se desvia fora dele.

O número oficial continua sendo **5.527/7.176 = 77,02% na faixa alta (n=7.176)**. O serviço efetivamente automatiza **5.510/7.176 = 76,8% (n=7.176)**: entre os 5.527 casos de faixa alta, **7 excedem 5.000 caracteres (n=5.527)** e **10 são desviados pela proteção de idioma (n=5.520 elegíveis)**; logo, `5.527 − 7 − 10 = 5.510`. Com a correção, cai para **5.460/7.176 = 76,1% (n=7.176)**, custo de **50 casos e 0,70 p.p.** Método: decomposição exata das barreiras e aplicação da regra sem ajuste ao teste congelado; fundamento: separar cobertura técnica do classificador da decisão final do serviço.

## Onde entra LLM e onde não

A LLM gerou casos de estresse com rótulos fixados antes da inferência; ela não escolhe fila, score, corte nem decisão automática. Em produção, pode resumir e rascunhar respostas sob revisão humana. A classificação continua com o modelo supervisionado congelado. Regras auditáveis cuidam de idioma, tamanho e kill switch, mas a barreira de escopo não generalizou: com ela ligada, **2.651/8.469 = 31,3% dos tickets da Base 1, de outro domínio (atendimento ao consumidor; n=8.469; IC95% 30,3%–32,3%)**, ainda iriam direto. Método e fundamento: mesma avaliação antes/depois descrita acima. Por isso a proposta não liga a automação direto: começa em modo sombra, com tickets da operação, e só automatiza depois de medir.

Para reproduzir essa calibração sem alterar o modelo:

```powershell
$env:PYTHONPATH="submissions/ramon-baptista/solution/src"; python submissions/ramon-baptista/solution/scripts/11_calibrate_language_guard.py
```

Para refazer o treinamento deliberadamente (substitui os artefatos congelados):

```powershell
$env:PYTHONPATH="submissions/ramon-baptista/solution/src"; python submissions/ramon-baptista/solution/scripts/train_and_freeze.py
```
