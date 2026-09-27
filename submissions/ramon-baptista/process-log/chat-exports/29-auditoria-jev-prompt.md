Preciso de uma auditoria rápida e honesta do experimento do Jev. Resultado obtido no teste congelado (n=800, 100 por classe): macro-F1 de 38,6% em inglês e 36,8% em português, contra 85,7% e 41,5% do nosso TF-IDF. Nenhum limiar de confiança atingiu 90% de acerto na validação, e 80 textos sem informação receberam todos "Miscellaneous" com confiança 1,0.

Há pessoas relatando resultados excelentes, rápidos e baratos com o Jev. Quero saber se o nosso resultado ruim se deve a ERRO DE CONFIGURAÇÃO nosso, ou se é o comportamento real do modelo neste problema.

Materiais:
- Script: submissions/ramon-baptista/solution/scripts/04_avaliar_jev.py (veja INSTRUCTIONS, CRITERIA, jev_one e o formato da requisição).
- Respostas salvas: submissions/ramon-baptista/solution/outputs/jev_evaluation/jev_results.jsonl e analysis.json.
- Amostra: .../jev_evaluation/sample_bilingual.csv (veja exemplos reais dos textos: são pré-processados, sem pontuação, com palavras cortadas).
- Documentação oficial: https://docs.typesafe.ai/llms.txt (índice), primitives/choice, confidence, models, model-jaggedness/jev-1.13, e os cookbooks/patterns.
- Parte da execução (tradução e chamadas com ritmo controlado) foi feita fora do seu sandbox, com os scripts C:\Users\Ramon\g4-ai-master\traduzir_amostra.py e rodar_jev_ritmado.py e rodar_jev_final.py. Confira se eles alteraram algo do seu método.

Verifique especificamente:
1. A requisição segue a documentação? Campos, tipo da pergunta, formato de criteria, modelo e versão.
2. As instruções e os critérios das 8 classes estão bem escritos segundo as boas práticas da documentação? Os critérios refletem o que cada rótulo realmente significa NESTA base? Olhe exemplos reais de cada classe e compare com a descrição que demos.
3. A documentação indica técnicas que não usamos e que costumam mudar muito o resultado: exemplos no critério, critério estruturado (objeto com inclui / não inclui / exemplos), perguntas decompostas, uso de "noul", várias perguntas por chamada?
4. O tipo de texto (pré-processado, palavras cortadas) é uma causa provável?
5. Onde o Jev mais erra na matriz de confusão, e isso aponta para critério mal definido ou para limitação do modelo?

Entregue:
- Veredito: erro de configuração, limitação real do modelo, ou as duas coisas — com evidência.
- Se houver erro de configuração, proponha a correção concreta (novos critérios, estrutura da pergunta) e estime o ganho plausível.
- Se valer a pena re-testar, proponha um re-teste pequeno SOMENTE na partição de validação (nunca no teste congelado), com no máximo 160 chamadas. Pode executá-lo, desde que: use workers 1, espere 2 segundos entre chamadas (o gateway para de responder após ~29 chamadas em rajada), salve cada resposta num arquivo novo (não sobrescreva jev_results.jsonl) e pare se a API ficar mais de 3 minutos sem responder.

Tempo máximo: 40 minutos. Regras do AGENTS.md valem. A chave está em AI_GATEWAY_API_KEY no .env; nunca a escreva em arquivo ou saída. Responda em português.
