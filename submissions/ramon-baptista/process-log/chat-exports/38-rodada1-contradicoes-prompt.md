Rodada 1 de 2 das correções antes do PR. A comparação com os concorrentes (bastidores/concorrentes/comparacao.md) apontou duas ações. Faça as duas, nesta ordem, sozinho e sem abrir agentes paralelos (o limite de uso da conta é curto).

## 1. Eliminar as contradições estatísticas (prioridade máxima)

O README diz que a métrica de "desperdício acima da mediana" foi retirada, mas scripts/02_diagnostico.py, outputs/02_resumo.json, outputs/02_diagnostico.md e outputs/02_desperdicio_horas.csv ainda a produzem ou publicam. O mesmo output mantém um ranking de cruzamentos canal × prioridade × tipo com grupos de n=10 a 23, o que contradiz a regra do AGENTS.md de que n<30 é exploratório.

Faça:
- ajuste o script para não produzir mais a métrica de desperdício pela mediana; se quiser manter alguma medida de tempo excedente, use uma referência que não se autoinfle (por exemplo, acima do P90) e nomeie como "tempo corrido excedente", nunca "desperdício";
- no ranking de cruzamentos, grupos com n<30 ficam marcados como exploratórios e não aparecem como conclusão; se couber, agregue para dois fatores;
- regenere os outputs afetados rodando o script uma vez;
- faça uma busca em TODA a pasta submissions/ramon-baptista/ (README, diagnóstico, proposta, outputs, process-log organizado) por termos e números da métrica retirada ("desperdício", "4.064", "406", "20.321", "acima da mediana") e pelo ranking antigo, e corrija ou marque cada ocorrência. Nos arquivos de auditoria e no diário, as menções são históricas (registram que o erro foi pego) e devem ficar como estão.
- reporte a lista do que mudou.

## 2. Sensibilidade no cenário econômico

Hoje o README mostra um único cenário ilustrativo (924,5 horas, R$ 46,2 mil). Gere três cenários — conservador, base e favorável — variando apenas as premissas já declaradas (participação de cada faixa, minutos por ticket, custo por hora). Mostre qual premissa mais move o resultado. Continue chamando de "benefício bruto", nunca de ROI, com método, premissas e n em cada número.

Atualize o README e a proposta de instrumentação para mostrar a faixa em vez do ponto único, de forma curta e em linguagem de gestor — uma tabela de três linhas basta. Não aumente o tamanho do README além do necessário.

## Regras

- Não altere o modelo, o split, o teste congelado nem as métricas do classificador.
- Um script único por etapa, rodado uma vez.
- Regras do AGENTS.md valem.
- Ao terminar, liste em no máximo 15 linhas: os arquivos alterados, a faixa dos três cenários, e qualquer ocorrência que você decidiu não mudar e por quê.

Responda em português.
