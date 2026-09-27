"""Entrada de produção: reutiliza integralmente a aplicação e suas verificações."""

from .web import create_app

app = create_app()
