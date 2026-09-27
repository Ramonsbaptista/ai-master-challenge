from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

from .core import ARTIFACTS, PrototypeError, sha256_file


LANGUAGE_GUARD_PATH = ARTIFACTS / "language_guard.json"


def _normalized_tokens(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKD", text.casefold())
    ascii_text = "".join(char for char in normalized if not unicodedata.combining(char))
    return re.findall(r"[a-z]+", ascii_text)


def language_evidence(text: str, guard: dict) -> tuple[int, int]:
    """Conta marcadores frequentes; repeticoes contam uma vez para reduzir ruido."""
    tokens = set(_normalized_tokens(text))
    return (len(tokens.intersection(guard["english_markers"])),
            len(tokens.intersection(guard["portuguese_markers"])))


def vocabulary_coverage(text: str, model) -> tuple[float, int, int]:
    """Fração dos tokens do texto presentes no vocabulário unigram do TF-IDF."""
    vectorizer = model.named_steps["tfidf"]
    tokens = vectorizer.build_tokenizer()(vectorizer.build_preprocessor()(text))
    vocabulary = vectorizer.vocabulary_
    recognized = sum(token in vocabulary for token in tokens)
    return (recognized / len(tokens) if tokens else 0.0), recognized, len(tokens)


def load_language_guard() -> dict:
    if not LANGUAGE_GUARD_PATH.exists():
        raise FileNotFoundError(
            "Causa: configuração da proteção de idioma ausente.\n"
            "Como corrigir: restaure artifacts/language_guard.json.\n"
            "Diagnóstico: não é seguro automatizar sem o limiar validado."
        )
    manifest = json.loads((ARTIFACTS / "manifest.json").read_text(encoding="utf-8"))
    expected = manifest["files"]["language_guard"]["sha256"]
    actual = sha256_file(LANGUAGE_GUARD_PATH)
    if actual != expected:
        raise PrototypeError(
            "Causa: hash da protecao de idioma nao confere.\n"
            "Como corrigir: restaure artifacts/language_guard.json.\n"
            f"Diagnostico: esperado {expected}; encontrado {actual}."
        )
    return json.loads(LANGUAGE_GUARD_PATH.read_text(encoding="utf-8"))


def should_send_to_human(text: str, model, guard: dict) -> tuple[bool, float, int, int]:
    coverage, recognized, total = vocabulary_coverage(text, model)
    en_hits, pt_hits = language_evidence(text, guard)
    evidence = int(guard["minimum_marker_hits"])
    if pt_hits >= evidence and pt_hits > en_hits:
        return True, coverage, recognized, total
    if en_hits >= evidence and en_hits > pt_hits:
        return False, coverage, recognized, total
    enough_tokens = total >= int(guard["minimum_tokens"])
    return enough_tokens and coverage < float(guard["threshold"]), coverage, recognized, total
