from __future__ import annotations

import os
import socket
import sys
import time
from functools import lru_cache
from threading import Lock, Thread
from urllib.error import URLError
from urllib.request import urlopen
import webbrowser

from flask import Flask, jsonify, render_template, request

from . import evaluate
from .cli import safety_mode_active, save_history
from .core import PrototypeError, load_manifest, load_verified_model
from .language import load_language_guard
from .service import CATEGORY_NAMES, MAX_TICKET_LENGTH, TicketInputError, classify_ticket


EXAMPLES = [
    "my laptop screen is broken and the keyboard does not work",
    "i forgot my password and cannot log in to the vpn",
    "i need administrator rights to install software on my computer",
    "my mailbox is full and i cannot receive new emails, please increase the storage quota",
    "please create a new project code and add the team members to the internal project",
    "please order a new headset for me, the purchase request is attached",
    "my monitor keeps flickering and the docking station does not detect the second screen",
    "question about my payslip and the number of vacation days left",
    "hello thanks",
    "Olá, o status do pedido está como entregue mas o cliente não recebeu a compra e já se passaram 24 horas",
]

LOCAL_HOST = "127.0.0.1"
DEFAULT_PORT = 5000
STARTUP_TIMEOUT_SECONDS = 60.0


def public_deploy_active() -> bool:
    return os.getenv("TICKET_CLASSIFIER_PUBLIC_DEPLOY", "").strip().casefold() in {
        "1", "true", "yes", "on", "sim"
    }


def find_available_port(preferred: int = DEFAULT_PORT, host: str = LOCAL_HOST) -> int:
    """Prefere a porta habitual e pede uma porta livre ao SO se ela estiver ocupada."""
    for candidate in (preferred, 0):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            try:
                probe.bind((host, candidate))
            except OSError:
                continue
            return int(probe.getsockname()[1])
    raise OSError("não foi possível encontrar uma porta local livre")


def wait_until_ready(url: str, timeout: float = STARTUP_TIMEOUT_SECONDS,
                     poll_interval: float = 0.1) -> bool:
    """Só considera o servidor pronto depois de receber uma resposta HTTP real."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urlopen(url, timeout=min(1.0, max(poll_interval, 0.01))) as response:
                if response.status == 200:
                    return True
        except (OSError, URLError):
            pass
        time.sleep(poll_interval)
    return False


def open_browser_when_ready(url: str, timeout: float = STARTUP_TIMEOUT_SECONDS) -> None:
    if wait_until_ready(f"{url}saude", timeout=timeout):
        if not webbrowser.open(url):
            print(f"O navegador não abriu sozinho. Copie este endereço: {url}", flush=True)
    else:
        print(
            f"O servidor não respondeu em até {timeout:.0f} segundos. "
            f"Confira as mensagens acima e tente abrir manualmente: {url}",
            file=sys.stderr, flush=True,
        )


_evaluation_lock = Lock()


@lru_cache(maxsize=1)
def _cached_evaluation_unlocked() -> dict:
    return evaluate.reproduce()


def cached_evaluation() -> dict:
    """Serializa a primeira reprodução e reutiliza o resultado no processo."""
    with _evaluation_lock:
        return _cached_evaluation_unlocked()


def clear_evaluation_cache() -> None:
    with _evaluation_lock:
        _cached_evaluation_unlocked.cache_clear()


def _number_br(value: int) -> str:
    return f"{int(value):,}".replace(",", ".")


def _decimal_br(value: float, places: int = 2) -> str:
    return f"{value:.{places}f}".replace(".", ",")


def _percent_br(value: float, places: int = 2) -> str:
    return f"{100 * value:.{places}f}%".replace(".", ",")


def _largest_confusions(matrix: list[list[int]], classes: list[str], limit: int = 3) -> list[dict]:
    """Traduz os maiores erros da matriz sem alterar resultados da avaliação."""
    errors = []
    for real_index, row in enumerate(matrix):
        for predicted_index, count in enumerate(row):
            if real_index != predicted_index and count:
                errors.append({
                    "real": CATEGORY_NAMES.get(classes[real_index], classes[real_index]),
                    "predicted": CATEGORY_NAMES.get(classes[predicted_index], classes[predicted_index]),
                    "count": int(count),
                })
    return sorted(errors, key=lambda item: item["count"], reverse=True)[:limit]


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(MAX_CONTENT_LENGTH=32 * 1024, JSON_AS_ASCII=False)
    if test_config:
        app.config.update(test_config)

    app.jinja_env.filters["number_br"] = _number_br
    app.jinja_env.filters["decimal_br"] = _decimal_br
    app.jinja_env.filters["percent_br"] = _percent_br

    try:
        model, manifest = load_verified_model()
        guard = load_language_guard()
        startup_error = None
    except (PrototypeError, AssertionError, FileNotFoundError, KeyError, ValueError) as exc:
        model = manifest = guard = None
        startup_error = str(exc).splitlines()[0]

    app.extensions["ticket_classifier"] = {
        "model": model, "manifest": manifest, "guard": guard, "startup_error": startup_error
    }

    @app.context_processor
    def visible_controls():
        state = app.extensions["ticket_classifier"]
        return {
            "kill_switch": safety_mode_active(),
            "integrity_ok": state["startup_error"] is None,
            "language_guard_ok": state["guard"] is not None,
            "public_demo": public_deploy_active(),
        }

    @app.get("/saude")
    def health_check():
        state = app.extensions["ticket_classifier"]
        if state["startup_error"]:
            return jsonify({"status": "indisponivel"}), 503
        return jsonify({"status": "ok"})

    @app.route("/", methods=["GET", "POST"])
    def classify_page():
        result = error = None
        text = request.form.get("ticket", "") if request.method == "POST" else ""
        if request.method == "POST":
            state = app.extensions["ticket_classifier"]
            if state["startup_error"]:
                error = "A análise está indisponível porque a integridade dos artefatos não pôde ser confirmada."
            else:
                try:
                    result = classify_ticket(text, state["model"], state["manifest"], state["guard"],
                                             safety_mode_active())
                    if not public_deploy_active():
                        save_history(text.strip(), result["decision"], result["category"],
                                     result["score"], result["band"])
                except TicketInputError as exc:
                    error = str(exc)
                    if not public_deploy_active():
                        save_history(text.strip(), "analise_humana", "", None, "entrada_invalida")
                except (PrototypeError, AssertionError, FileNotFoundError, ValueError) as exc:
                    error = "Não foi possível analisar com segurança. Verifique os controles e tente novamente."
                    app.logger.warning("Falha controlada na classificação: %s", exc)
        return render_template("classify.html", examples=EXAMPLES, result=result, error=error,
                               ticket=text, max_length=MAX_TICKET_LENGTH)

    @app.get("/avaliacao")
    def evaluation_page():
        return render_template("evaluation.html")

    @app.get("/avaliacao/resultado")
    def evaluation_result():
        try:
            result = cached_evaluation()
            manifest = load_manifest()
            classes = manifest["classes"]
            return render_template("_evaluation_result.html", result=result, manifest=manifest,
                                   categories=CATEGORY_NAMES,
                                   confusions=_largest_confusions(result["matrix"], classes))
        except (PrototypeError, AssertionError, FileNotFoundError, KeyError, ValueError) as exc:
            return jsonify({"error": "A avaliação foi interrompida porque uma verificação de integridade falhou.",
                            "detail": str(exc).splitlines()[0]}), 503

    @app.get("/controles")
    def controls_page():
        return render_template("controls.html", startup_error=startup_error)

    @app.errorhandler(413)
    def request_too_large(_error):
        return render_template("classify.html", examples=EXAMPLES, result=None,
                               error="O texto enviado é grande demais. Reduza o ticket e tente novamente.",
                               ticket="", max_length=MAX_TICKET_LENGTH), 413

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error("Erro interno controlado: %s", error)
        return render_template("error.html"), 500

    return app


def main() -> None:
    try:
        print("Carregando o modelo, aguarde…", flush=True)
        app = create_app()
        startup_error = app.extensions["ticket_classifier"]["startup_error"]
        if startup_error:
            raise RuntimeError(startup_error)
        port = find_available_port()
        url = f"http://{LOCAL_HOST}:{port}/"
        print(f"Interface pronta em: {url}", flush=True)
        print(f"Se o navegador não abrir sozinho, copie o endereço acima.", flush=True)
        print("Não feche esta janela.", flush=True)
        print("Para encerrar, Ctrl+C.", flush=True)
        Thread(target=open_browser_when_ready, args=(url,), daemon=True).start()
        app.run(host=LOCAL_HOST, port=port, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\nAplicação encerrada.", flush=True)
    except Exception as exc:
        message = str(exc).splitlines()[0] or exc.__class__.__name__
        print(f"Não foi possível iniciar a aplicação: {message}", file=sys.stderr, flush=True)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
