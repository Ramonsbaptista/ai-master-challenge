A tradução está pronta. Como o seu sandbox não conseguia ler o modelo do Argos, eu executei a tradução fora dele, seguindo exatamente o desenho que você definiu. Não mudei o método, só rodei.

Arquivo: submissions/ramon-baptista/solution/outputs/jev_evaluation/sample_bilingual.csv
- 1.600 linhas: 800 de validação e 800 de teste, 100 por classe em cada partição, nas 8 classes.
- Colunas: record_id, partition, Topic_group, Document, Document_pt, sha256_en.
- record_id calculado com a MESMA regra do seu script: sha256 de "posição \x1f texto \x1f rótulo" sobre o CSV completo da Base 2. As linhas de teste saíram do split congelado; as de validação, da validação.
- Amostragem por classe com random_state=20260922, sem groupby.apply (o pandas 3.0 remove a coluna de agrupamento).
- Tradução: Argos 1.11.0, modelo en->pt 1.9, pipeline inicializado uma única vez, execução serial. O cache translation_cache.json foi reaproveitado pelo hash do texto.
- 0 traduções vazias. Duração: 37,9 minutos.
- Limitação já registrada: o modelo produz português europeu, não brasileiro.
- O script que usei está em C:\Users\Ramon\g4-ai-master\traduzir_amostra.py — confira antes de confiar.

Antes de rodar:
1. Verifique o arquivo: contagens por partição e classe, se os record_id do teste existem no split congelado, e se não há vazios. Se algo não bater com o seu desenho, pare e me diga.
2. NÃO rode o passo de tradução (prepare): ele vai tentar ler o Argos e falhar. Use o CSV pronto.

Depois siga: piloto cronometrado (me diga o tempo), execução completa das chamadas ao Jev, estabilidade, textos sem informação e relatório.

Entregue os 6 itens combinados:
1. as quatro medições (Jev e modelo atual, em inglês e português), macro-F1, método e n;
2. comparação estatística entre sistemas e entre idiomas;
3. calibração da confiança do Jev, incluindo os textos sem informação;
4. estabilidade em chamadas repetidas;
5. consumo real de tokens, latência e custo;
6. sua recomendação: o Jev entra? em que papel? e o que fazer sobre português?

Se travar, pare e me diga o que precisa. Regras do AGENTS.md valem. Responda em português.
