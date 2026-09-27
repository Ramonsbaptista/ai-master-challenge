Decisão do Ramon: o protótipo precisa de uma interface visual adequada, limpa e pronta para um usuário final. "Uma empresa do nível do G4 não vai aceitar um sistema cru desse jeito no terminal."

NESTA ETAPA, NÃO CONSTRUA NADA. Primeiro proponha o desenho, em no máximo 20 linhas, para o Ramon aprovar. Faça sozinho, sem abrir agentes paralelos.

O desenho precisa responder:

1. TECNOLOGIA. Qual você propõe (Streamlit, Gradio, Flask + HTML, outra) e por quê, considerando:
   - o avaliador precisa rodar com o mesmo comando único de hoje (run.ps1 / run.sh), que deve abrir a interface no navegador;
   - a máquina tem pouca RAM;
   - o teste congelado, os hashes, a proteção de idioma, o kill switch e os 10 testes precisam continuar funcionando, reaproveitando o mesmo núcleo (src/ticket_classifier/) — nenhuma lógica duplicada na interface;
   - o terminal continua existindo como alternativa, e o Colab continua funcionando para o teste Linux.

2. TELAS. Quais telas e o que cada uma mostra. No mínimo:
   - classificar um ticket: a decisão em linguagem de negócio, o porquê e o risco, com destaque visual claro para "vai direto para a fila" versus "vai para uma pessoa". A parte "onde a IA para" é o diferencial desta entrega e precisa ficar visível;
   - reproduzir a avaliação: conclusão para o gestor primeiro, detalhes técnicos depois;
   - o estado do kill switch e da proteção de idioma visível;
   - exemplos de tickets prontos para o usuário testar com um clique.

3. PÚBLICO. O avaliador é executivo, não técnico. A interface deve ser entendida sem ler o README.

4. ESFORÇO estimado, e o que você deixaria de fora para caber no prazo.

5. RISCOS: o que pode quebrar no que já está testado, e como evitar.

Regras do AGENTS.md valem. Responda em português.
