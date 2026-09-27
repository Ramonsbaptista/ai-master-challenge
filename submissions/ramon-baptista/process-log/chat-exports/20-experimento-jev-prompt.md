Nova tarefa: avaliar o Jev como desafiante do nosso classificador, e decidir o que fazer sobre português. A decisão de arquitetura e de método é sua; eu audito.

## Fatos novos desde a sua última análise

1. A documentação oficial TEM uma seção sobre idioma, que você não encontrou antes. Em https://docs.typesafe.ai/models, a seção "Language support" diz: "Jev accepts natural-language text. English is the primary training language and where accuracy is currently best. Other languages, including CJK scripts, are handled but not equally well; test on your own content before relying on Jev for a non-English workload, and pay close attention to Confidence when routing."

2. Temos acesso funcionando à API. A chave está na variável de ambiente AI_GATEWAY_API_KEY, no arquivo .env da raiz do projeto (que está no .gitignore). NUNCA escreva a chave em arquivo, log, saída ou documento.

3. Endpoint que funciona: POST https://ai-gateway.vercel.sh/v1/evaluate
   Cabeçalhos: Authorization: Bearer <chave>, Content-Type: application/json
   Corpo: {"model":"typesafe-ai/jev","state":"<texto>","questions":{"<id>":{"type":"choice","instructions":"<pergunta>","criteria":{"<opcao>":"<descricao>", ...}}}}
   Resposta: answers.<id> traz choice, probabilities (soma 1) e confidence; usage traz inputTokens e outputTokens.
   O Jev está gratuito até 25/09/2026 e a latência observada foi de 0,4 a 0,6 s por chamada.

4. Teste de fumaça que EU fiz (n=5, não é evidência, só mostra que a API responde):
   - "my laptop screen is broken and the keyboard does not work" -> Hardware, confidence 1,000
   - "a tela do meu notebook quebrou e o teclado nao funciona" -> Hardware, confidence 1,000
   - "esqueci minha senha e nao consigo acessar a vpn" -> Access, confidence 1,000
   - "preciso de aprovacao para comprar monitores novos para a equipe" -> Purchase, confidence 0,990
   - "ola obrigado" (texto sem informação) -> Miscellaneous, confidence 1,000
   O último caso me preocupa: texto vazio de conteúdo recebeu confiança máxima.

## O que eu quero de você

Projete e execute a avaliação. Decida você: tamanho e composição da amostra, como obter a versão em português (você mesmo pode traduzir), quais métricas usar, como tratar a questão da calibração, e o que medir além de acerto (custo, latência, estabilidade em chamadas repetidas).

O que eu preciso ter no final, para decidir:
- se o Jev entra na solução, e em que papel exatamente;
- o que fazer sobre português, com número, e não com opinião;
- o que cada escolha custa e o que ela arrisca.

Restrições:
- O teste congelado não pode ser usado para ajustar nada. Se você precisar ajustar prompt, critérios ou limiar, use outro conjunto e diga qual.
- Nenhuma afirmação sem o método, as premissas e o n. Regras do AGENTS.md valem.
- Os artefatos do experimento ficam em submissions/ramon-baptista/solution/. Não altere o modelo atual, o split nem as métricas já medidas.
- Respeite o limite de gasto: o Jev está gratuito até 25/09, mas dimensione a amostra com bom senso e reporte o consumo real de tokens.
- Antes de rodar qualquer coisa em escala, me diga em no máximo 15 linhas o desenho que você escolheu e por quê. Depois execute.

Responda em português.
