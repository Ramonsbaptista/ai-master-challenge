Antes de construirmos o classificador, quero avaliar uma alternativa ao TF-IDF + regressão logística que você recomendou.

A alternativa é o Jev, descrito assim por quem me apresentou:

"O Jev é um novo modelo de inteligência artificial focado exclusivamente em tomar decisões estruturadas e classificar dados dentro de sistemas de software, abdicando totalmente da geração de textos livres. Desenvolvido pela startup TypeSafe AI, ele inaugura uma classe de modelos batizada de System One. Ao contrário de LLMs tradicionais, foi projetado para conversar diretamente com códigos e automações. Recebe dados em formatos como texto ou JSON e devolve respostas exatas (como sim/não ou escolha múltipla), sempre acompanhadas de uma nota de probabilidade e confiança."

Tarefa:

1. Pesquise na web e leia a documentação oficial do Jev (site da TypeSafe AI, docs, referência de API, preços, limites, termos de uso). Cite as URLs que você efetivamente abriu. Se não encontrar documentação oficial, diga isso claramente e NÃO invente capacidades — separe o que é confirmado por fonte do que é apenas a descrição acima.

2. Avalie se ele é a melhor escolha para o nosso protótipo, comparando com TF-IDF + regressão logística nestes critérios, sempre dizendo o que é confirmado e o que é suposição:
   - A "probabilidade e confiança" que ele devolve é calibrada? Existe documentação sobre como é calculada? Isso é decisivo, porque o nosso limite de confiança decide o que vai para humano.
   - Suporta uma taxonomia customizada de 8 classes, e aprende com exemplos rotulados (few-shot, fine-tuning ou equivalente)?
   - Custo e latência para classificar os ~9.600 textos do conjunto de teste, e para operação contínua.
   - Reprodutibilidade: a mesma entrada gera sempre a mesma saída? Há versionamento do modelo?
   - Privacidade: os textos saem da máquina para um servidor externo? (A base do case é pública, mas numa operação real seria dado de cliente.)
   - Auditabilidade: é possível explicar por que um ticket caiu numa categoria?
   - Maturidade: tempo de mercado, estabilidade da API, dependência de um fornecedor pequeno.
   - Os textos da nossa base 2 já vêm pré-processados, sem pontuação e com palavras cortadas. Isso favorece ou prejudica o Jev?

3. Recomende uma de três opções, com justificativa:
   a) usar o Jev no lugar do TF-IDF;
   b) manter TF-IDF como modelo principal e testar o Jev como comparação, no mesmo conjunto de teste;
   c) não usar o Jev.

Regras do AGENTS.md valem. Não escreva código nem crie arquivos nesta etapa. Responda em português.
