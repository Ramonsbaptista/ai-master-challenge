# Resposta final do Codex — ambiente limpo no Linux

Corrigido o defeito de portabilidade.

- `run.sh` agora tenta `venv`, depois `--without-pip`, `pip --python` e, por fim, `get-pip.py`.
- A escolha mantém isolamento e funciona sem administrador; se tudo falhar, informa a causa real e recomenda `sudo apt install python3-venv`.
- `colab.ipynb` agora resolve corretamente o caminho do upload e executa o mesmo launcher/classificador.
- `run.ps1` não foi alterado e passou na validação sintática.
- A suíte Python existente passou integralmente; modelo, split, teste congelado e métricas não foram alterados.
- Não consegui executar o shell Linux localmente porque WSL/Git Bash estavam bloqueados naquele ambiente; não aleguei validação Linux completa.
- O sandbox bloqueou o Desktop. O ZIP foi validado, com barras normais e as exclusões solicitadas, e salvo no workspace como `projeto-para-colab.zip`.

Prompt correspondente: [`36-linux-venv-prompt.md`](36-linux-venv-prompt.md).
