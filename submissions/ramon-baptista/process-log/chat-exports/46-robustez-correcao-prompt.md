Auditoria do Claude sobre a rodada 45, aprovada pelo Ramon. Três correções. Faça sozinho, sem agentes paralelos. Regras do AGENTS.md valem. PROIBIDO alterar modelo, split, teste congelado, limiares ou números publicados.

## Defeito encontrado

Em `solution/outputs/robustez/casos_rotulados.csv`, muitos casos são a mesma frase com um sufixo numérico ("Case 14", "ref 18", "caso 18", "Reference 1095"). Removendo o sufixo, as frases realmente distintas são:
- reformulações: 160 de 256;
- erros de digitação: 171 de 208;
- textos curtos: 16 de 208;
- mistura de idiomas: 16 de 208;
- fora do escopo: 12 de 240 (só 6 em inglês).

Casos repetidos não são observações independentes: o n declarado e os intervalos de Wilson estão inflados. Pela regra do AGENTS.md, grupos com menos de 30 casos distintos são exploratórios. Isso invalida as conclusões dos grupos curtos, idiomas misturados e fora do escopo, e enfraquece as demais.

## Correções

1. **Refazer o conjunto.** Pelo menos 100 frases realmente distintas por grupo, sem sufixo numérico nem qualquer marcador artificial. O script precisa checar a duplicidade (texto normalizado: minúsculas, sem pontuação, sem números) e falhar se houver repetição. O grupo "fora do escopo" precisa ter a maioria dos casos em INGLÊS, porque em português a proteção de idioma já desvia tudo e o teste não mede o classificador; reporte separadamente os casos em inglês e em português. Rótulos definidos antes da inferência, com hash novo. Refaça a calibração e a medição da correção "fora do escopo" (calibrar numa metade, medir na outra) sobre o conjunto novo. Apague ou substitua os artefatos antigos para não restar número contaminado.

2. **Base 1 como achado principal.** No relatório de robustez, no README e na proposta, o resultado principal passa a ser a Base 1: tickets reais de clientes (n=8.469), dos quais 2.718 (32,1%, IC95% 31,1%–33,1%) seriam encaminhados direto com confiança, embora sejam de outro domínio. Explique em linguagem de negócio o que isso significa em produção e que isso mede exposição, não acurácia. Os tickets sintéticos ficam como evidência complementar, com a limitação declarada.

3. **Explicar a divergência de cobertura.** A rodada 45 reportou cobertura no teste congelado de 5.510/7.176, mas o número oficial publicado é 5.527/7.176 (77,02%). Descubra e explique a diferença com código (ex.: efeito da proteção de idioma ou de outra barreira). Se a diferença for legítima, deixe as duas definições explícitas; nunca substitua o número oficial.

Depois, revise a seção "Onde entra LLM e onde não" no README e na proposta com os números novos.

## Ao final, em até 25 linhas
Os números novos por grupo (com n de frases distintas), a correção com seu custo, a explicação da divergência 5.510 × 5.527, o que mudou no README e na proposta, e o resultado real da suíte de testes.
