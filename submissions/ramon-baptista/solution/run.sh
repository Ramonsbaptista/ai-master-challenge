#!/usr/bin/env sh
set -eu
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
VENV="$ROOT/.venv"
VENV_PYTHON="$VENV/bin/python"
VENV_ERROR="$ROOT/.venv-bootstrap-error.log"
GET_PIP="$ROOT/.get-pip.py"

cleanup_bootstrap_files() {
  rm -f -- "$VENV_ERROR" "$GET_PIP"
}

venv_diagnostic() {
  if grep -qi 'ensurepip\|python3-venv' "$VENV_ERROR"; then
    echo "Causa: o Python deste sistema não inclui ensurepip para ambientes virtuais."
    echo "Como corrigir: no Ubuntu/Debian, execute 'sudo apt update && sudo apt install python3-venv' e tente novamente."
  else
    echo "Causa: não foi possível criar ou preparar o ambiente virtual."
    echo "Como corrigir: verifique permissão de escrita na pasta da solução e espaço em disco; no Ubuntu/Debian, instale também 'python3-venv'."
  fi
  echo "Diagnóstico: falharam a criação normal do venv e as alternativas sem privilégio (pip hospedeiro e get-pip.py)."
  if [ -s "$VENV_ERROR" ]; then
    echo "Detalhes do último erro:"
    cat "$VENV_ERROR"
  fi
  cleanup_bootstrap_files
  exit 1
}

create_venv() {
  rm -rf -- "$VENV"
  : >"$VENV_ERROR"
  if python3 -m venv "$VENV" 2>"$VENV_ERROR"; then
    cleanup_bootstrap_files
    return 0
  fi

  if grep -qi 'ensurepip\|python3-venv' "$VENV_ERROR"; then
    echo "ensurepip indisponível; tentando bootstrap do pip sem privilégio de administrador."
  else
    echo "A criação normal do venv falhou; tentando alternativa sem privilégio de administrador."
  fi
  rm -rf -- "$VENV"
  if ! python3 -m venv --without-pip "$VENV" 2>>"$VENV_ERROR"; then
    venv_diagnostic
  fi

  if python3 -m pip --version >/dev/null 2>&1 &&
     python3 -m pip --python "$VENV_PYTHON" install --upgrade pip 2>>"$VENV_ERROR"; then
    cleanup_bootstrap_files
    return 0
  fi

  if python3 -c 'import sys, urllib.request; urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", sys.argv[1])' "$GET_PIP" 2>>"$VENV_ERROR" &&
     "$VENV_PYTHON" "$GET_PIP" 2>>"$VENV_ERROR"; then
    cleanup_bootstrap_files
    return 0
  fi
  venv_diagnostic
}

trap cleanup_bootstrap_files EXIT HUP INT TERM
if ! command -v python3 >/dev/null 2>&1; then
  echo "Causa: Python não foi encontrado."
  echo "Como corrigir: instale Python 3.11 a 3.14 ou use o notebook Colab incluído."
  echo "Diagnóstico: comando python3 indisponível."
  exit 1
fi
if ! python3 -c 'import sys; raise SystemExit(0 if (3,11) <= sys.version_info[:2] < (3,15) else 1)'; then
  echo "Causa: versão de Python não suportada."
  echo "Como corrigir: instale Python 3.11 a 3.14 ou use o notebook Colab incluído."
  echo "Diagnóstico: detectado $(python3 --version)."
  exit 1
fi
VENV_EXISTED=0
VENV_HEALTHY=0
if [ -d "$VENV" ]; then
  VENV_EXISTED=1
  if [ -x "$VENV_PYTHON" ] &&
     "$VENV_PYTHON" -c 'import sys' >/dev/null 2>&1 &&
     "$VENV_PYTHON" -m pip --version >/dev/null 2>&1; then
    VENV_HEALTHY=1
  else
    echo "Ambiente virtual incompleto; recriando .venv."
    rm -rf -- "$VENV"
    VENV_EXISTED=0
  fi
fi
if [ "$VENV_EXISTED" -eq 0 ]; then
  create_venv
fi
if ! "$VENV_PYTHON" -m pip --version >/dev/null 2>&1; then
  echo "Causa: o ambiente virtual foi criado sem pip."
  echo "Como corrigir: no Ubuntu/Debian, execute 'sudo apt update && sudo apt install python3-venv' e tente novamente."
  echo "Diagnóstico: python -m pip --version falhou dentro do ambiente isolado."
  exit 1
fi
if ! "$VENV_PYTHON" -m pip install -r "$ROOT/requirements.txt"; then
  if [ "$VENV_HEALTHY" -eq 1 ]; then
    echo "Ambiente virtual incompleto; recriando .venv."
    create_venv
    "$VENV_PYTHON" -m pip install -r "$ROOT/requirements.txt"
  else
    exit 1
  fi
fi
if [ "${1:-}" = "--cli" ] || [ ! -t 0 ]; then
  PYTHONPATH="$ROOT/src" "$VENV_PYTHON" -m ticket_classifier.cli
else
  PYTHONPATH="$ROOT/src" "$VENV_PYTHON" -m ticket_classifier.web
fi
