Decidimos: o n8n fica fora da entrega obrigatória. O protótipo será 100% em Python.

Antes de você começar a construir, preciso de um plano para que a solução rode sem falhar quando o avaliador do G4 for executá-la na máquina dele. Não conhecemos a máquina: pode ser Windows, macOS ou Linux, com ou sem Python instalado, com outra versão de Python, com pouca ou muita memória.

Sei que risco zero não existe. Por isso, quero que você:

1. LISTE os pontos de falha concretos que podem acontecer quando uma pessoa desconhecida tenta rodar um projeto Python pela primeira vez. Seja específico ao nosso caso: pandas, scikit-learn, arquivos CSV grandes, modelo treinado salvo em disco, caminhos de arquivo, encoding, versões de biblioteca, sistema operacional, tamanho do repositório no GitHub, dados que precisam ser baixados.

2. Para cada ponto de falha, diga COMO FECHAR: qual decisão técnica elimina ou reduz o risco.

3. Responda especificamente:
   - Os CSVs brutos (cerca de 18 MB) e o modelo treinado devem ir no repositório, ou ser baixados/gerados na execução? Quais as consequências de cada escolha para o PR e para o avaliador?
   - Qual a forma mais robusta de fixar as dependências?
   - Como garantir que o resultado (a matriz de confusão e o macro-F1) seja exatamente o mesmo na máquina do avaliador e na minha?
   - Faz sentido oferecer mais de uma forma de rodar (por exemplo, um comando local e um notebook que rode no Google Colab sem instalar nada)? Qual seria a principal?
   - Como o avaliador consegue testar um ticket novo digitado por ele, de forma simples, sem precisar entender o código?
   - Como fazer a solução falhar com uma mensagem clara e útil, em vez de um erro técnico incompreensível, se algo der errado?

4. Diga como vamos TESTAR que funciona antes de entregar, simulando a máquina de alguém que nunca viu o projeto.

5. Termine com a estrutura de pastas e arquivos que você propõe, e o comando exato que o avaliador vai digitar.

Não escreva código nem crie arquivos nesta etapa. Regras do AGENTS.md valem. Responda em português.
