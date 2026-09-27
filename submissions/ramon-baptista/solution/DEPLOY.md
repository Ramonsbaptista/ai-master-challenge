# Publicar a demonstração no Render

## Por que Render

O Render foi escolhido porque oferece Web Service gratuito, URL pública com HTTPS e deploy de
Docker sem adaptar a aplicação para outro framework. Em setembro de 2026, a instância gratuita
tem 0,1 CPU e 512 MB de RAM. Ela adormece após 15 minutos sem acesso; a primeira visita seguinte
mostra a página de carregamento do Render e costuma levar cerca de um minuto para acordar. É uma
limitação aceitável para a demonstração, mas o link deve ser aberto alguns minutos antes da
avaliação. O Hugging Face Spaces não foi escolhido porque novos Spaces Docker/Gradio passaram a
exigir plano pago, apesar de a máquina CPU Basic não ter custo por hora.

Fontes oficiais: [plano gratuito e tempo de despertar](https://render.com/docs/free),
[recursos da instância](https://render.com/docs/compute-plans) e
[deploy de Flask](https://render.com/docs/deploy-flask).

## Passo a passo

1. Envie este repositório para uma conta sua no GitHub. Confirme que a pasta
   `submissions/ramon-baptista/solution/` contém `Dockerfile`, `requirements.txt`, `src/`, `data/`
   e `artifacts/`. Você verá esses arquivos na página do repositório. Não envie `.env`.
2. Acesse [dashboard.render.com](https://dashboard.render.com/), crie uma conta ou entre nela e
   clique em **New > Web Service**. Você verá a tela para conectar um repositório Git.
3. Conecte o GitHub e selecione o repositório desta entrega. Você verá o formulário do serviço.
4. Em **Root Directory**, informe `submissions/ramon-baptista/solution`. Em **Runtime**, escolha
   **Docker**. O Render encontrará `Dockerfile` nessa pasta.
5. Dê um nome, por exemplo `triagem-assistida-ramon`, escolha a região mais próxima e selecione
   **Free**. Não adicione banco, disco, segredo ou variável: o Dockerfile já ativa somente o modo
   público seguro e usa a porta fornecida pelo Render.
6. Em **Health Check Path**, informe `/saude`. Clique em **Create Web Service**. Você verá os logs
   de build; na primeira vez, o Render instala as versões fixadas e inicia o Gunicorn.
7. Espere o estado **Live**. No topo aparecerá uma URL terminada em `.onrender.com`; abra-a e
   confirme o aviso “Demonstração pública — não envie dados reais de clientes.”
8. Teste um exemplo e abra **Avaliação reproduzível**. O primeiro acesso calcula e valida a
   avaliação; os seguintes usam o resultado em memória. Antes de enviar a entrega, abra o link
   novamente para acordar o serviço gratuito.

## Controles do modo público

- O servidor escuta em `0.0.0.0` apenas dentro do comando de produção; o launcher local continua
  restrito a `127.0.0.1`.
- O mesmo `create_app`, o mesmo classificador e as mesmas verificações SHA-256 são usados nos dois
  modos. Não há cópia da lógica do modelo.
- Textos têm o mesmo limite de 5.000 caracteres. No modo público, nenhum texto, hash ou histórico
  de classificação é gravado.
- O Gunicorn roda sem debug, com um processo e quatro threads. Um único processo evita duplicar o
  modelo na RAM; a reprodução da avaliação é protegida por cache em memória seguro entre threads,
  portanto acessos simultâneos reutilizam um único resultado em vez de repetir o cálculo pesado.
- O filesystem gratuito é efêmero e a aplicação não depende de escrita persistente.

## Atualizar ou diagnosticar

Cada `git push` para a branch conectada cria novo deploy. Se falhar, abra **Logs**: a rota `/saude`
só responde como saudável depois que modelo, manifesto e proteção de idioma foram carregados e os
hashes conferidos. O `render.yaml` incluído documenta a mesma configuração para uso futuro via
Blueprint; o procedimento acima é o mais simples para publicar somente esta subpasta.

Para validar também a imagem em uma máquina com Docker, execute a partir da pasta `solution`:

```powershell
docker build -t triagem-assistida-ramon .
docker run --rm -p 10000:10000 -e PORT=10000 triagem-assistida-ramon
```

Em outro terminal, `Invoke-WebRequest http://127.0.0.1:10000/saude` deve retornar status 200 e
`{"status":"ok"}`; a interface fica em `http://127.0.0.1:10000/`.
