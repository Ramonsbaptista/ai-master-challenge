Testei o protótipo pessoalmente e encontrei problemas. Cinco correções.

## Contexto do meu teste

Digitei, em português: "Olá, o status do pedido está como entregue mas o cliente não recebeu a compra e já se passaram 24 horas".

Saída:
  Classe: Hardware
  Score do modelo (não calibrado): 0.2754
  Faixa: baixa

A faixa baixa foi o comportamento correto: o modelo nunca viu problema de entrega (não existe nas 8 categorias) e foi treinado em inglês. Mas eu só sei interpretar isso porque acompanhei o projeto.

## Correção 1 — o ambiente não é isolado (erro grave)

O run.ps1 cria o ambiente com `python -m venv --without-pip --system-site-packages`. A saída da instalação mostra "Requirement already satisfied ... pythoncore-3.14-64\lib\site-packages": o ambiente está reaproveitando os pacotes do meu computador. Na máquina do avaliador, que não os tem, é justamente onde a instalação pode falhar. Isso também significa que o teste de ponta a ponta que você reportou como aprovado NÃO simulou uma instalação limpa.

Corrija o run.ps1 e o run.sh para criar um ambiente isolado de verdade, com o instalador incluído e sem pacotes do sistema. Se houver motivo técnico para a escolha atual, explique antes de mudar.

## Correção 2 — refazer o teste do zero

Apague o ambiente, clone ou copie a solução para uma pasta nova com espaço no nome, e rode seguindo apenas o README. Reporte exatamente o que aconteceu, inclusive tempo e qualquer aviso.

## Correção 3 — teste em Linux

O run.sh nunca foi executado. Faça o notebook do Colab funcionar como teste em Linux, e deixe claro no README o passo a passo para rodá-lo. Se você não conseguir executar o Colab daqui, diga isso explicitamente e deixe as instruções prontas para eu rodar.

## Correção 4 — histórico dos testes

Faça o menu gravar cada classificação num arquivo de histórico (data e hora, texto, categoria, score, faixa), dentro de outputs/. Serve para que os testes feitos por qualquer pessoa virem evidência.

## Correção 5 — o avaliador não é técnico (a mais importante)

A pessoa que vai avaliar é executiva, não técnica. Ela lê "Classe: Hardware · Score 0.2754 · Faixa: baixa" e não entende nada — ou pior, conclui que o sistema errou.

Reescreva a saída do menu para uma pessoa não técnica entender sozinha, sem nunca ter visto o projeto. A resposta a um ticket deve dizer, em português simples:
- o que o sistema decidiu fazer com o ticket (ex.: "encaminhar direto para a fila de Hardware" ou "mandar para uma pessoa analisar");
- por quê, em uma frase (ex.: "o sistema não reconheceu o assunto com segurança");
- qual é o risco, quando a decisão for automática (ex.: "em tickets com este nível de segurança, o sistema acerta 94 de cada 100").

Troque "score", "faixa baixa/média/alta" e o nome das categorias em inglês por linguagem de negócio. Mantenha os valores técnicos disponíveis, mas em segundo plano (por exemplo, numa linha "detalhe técnico" menor, ou numa opção do menu).

Aplique a mesma regra à opção "Reproduzir a avaliação": primeiro uma conclusão de 3 a 4 linhas em linguagem de negócio, e só depois a matriz e as métricas.

Inclua no README uma seção "Como testar em 2 minutos", com 3 ou 4 exemplos de ticket prontos para copiar e colar, e o que o avaliador deve observar em cada um. Inclua pelo menos um exemplo que vai para uma pessoa, explicando por que isso é o comportamento desejado. Lembre que o modelo foi treinado em inglês: diga isso claramente e use exemplos em inglês, com a tradução ao lado.

## Regras

- Não altere o modelo, o split, o teste congelado nem as métricas. Só ambiente, interface, histórico e documentação.
- Regras do AGENTS.md valem.
- Não diga que testou algo que não testou.

Ao terminar, mostre exatamente como fica a saída do menu para o meu ticket de teste, antes e depois.
