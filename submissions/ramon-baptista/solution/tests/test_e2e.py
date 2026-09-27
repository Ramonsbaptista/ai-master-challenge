import csv
import io
import os
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ticket_classifier import cli
from ticket_classifier.core import (PrototypeError, assert_consistency, load_manifest,
                                    load_verified_model, per_class_metrics, route,
                                    routing_thresholds)
from ticket_classifier.evaluate import reproduce
from ticket_classifier.language import load_language_guard, should_send_to_human
from ticket_classifier.service import classify_ticket
from ticket_classifier.web import (EXAMPLES, cached_evaluation, clear_evaluation_cache, create_app,
                                   find_available_port, main,
                                   open_browser_when_ready)


class CriticalControlsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model, cls.manifest = load_verified_model()
        cls.guard = load_language_guard()

    def setUp(self):
        self.history_dir = ROOT / "tests" / "history_test_output"
        self.history_path = self.history_dir / "classification_history.csv"
        if self.history_path.exists():
            self.history_path.unlink()

    def tearDown(self):
        if self.history_path.exists():
            self.history_path.unlink()

    def test_frozen_evaluation_reproduces(self):
        result = reproduce()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["n"], self.manifest["test"]["n"])
        routing = result["effective_routing"]
        self.assertEqual(routing["high_band_n"], self.manifest["test_routing"]["alta"]["n"])
        self.assertEqual(routing["blocked_by_size_n"], 7)
        self.assertEqual(routing["blocked_by_language_n"], 10)
        self.assertEqual(routing["automated_n"], 5510)
        self.assertEqual(routing["automated_correct_n"] +
                         (routing["automated_n"] - routing["automated_correct_n"]), 5510)

    def test_tampered_artifact_refuses_evaluation(self):
        with patch("ticket_classifier.core.sha256_file", return_value="hash-alterado"):
            with self.assertRaisesRegex(PrototypeError, "hash do modelo"):
                reproduce()

    def test_confusion_matrix_consistency(self):
        classes = self.manifest["classes"]
        matrix = np.asarray(self.manifest["test"]["confusion_matrix"])
        y_true = np.repeat(classes, matrix.sum(axis=1))
        y_pred = np.concatenate([np.repeat(classes, row) for row in matrix])
        calculated, rows = per_class_metrics(y_true, y_pred, classes)
        np.testing.assert_array_equal(calculated, matrix)
        assert_consistency(calculated, rows, y_true, classes)
        self.assertEqual(int(calculated.sum()), self.manifest["test"]["n"])

    def test_confusion_matrix_rejects_wrong_class_n(self):
        classes = ["A", "B"]
        matrix, rows = per_class_metrics(["A", "B"], ["A", "B"], classes)
        with self.assertRaisesRegex(AssertionError, "Linha"):
            assert_consistency(matrix, rows, np.array(["A", "A"]), classes)

    def test_routing_cuts_come_from_manifest_and_boundaries_are_inclusive(self):
        low, high = routing_thresholds(load_manifest())
        self.assertEqual((low, high), (self.manifest["routing_thresholds"]["low"],
                                      self.manifest["routing_thresholds"]["high"]))
        bands = route(np.array([np.nextafter(low, -np.inf), low,
                                np.nextafter(high, -np.inf), high]), low, high)
        self.assertEqual(bands.tolist(), ["baixa", "media", "media", "alta"])

    def test_language_guard_short_cases_both_directions(self):
        english = ["i forgot my password and cannot log in to the vpn",
                   "the printer on the third floor is jammed and shows an error light"]
        portuguese = ["a tela do meu notebook quebrou e o teclado nao funciona",
                      "esqueci minha senha e nao consigo entrar na vpn"]
        self.assertTrue(all(not should_send_to_human(t, self.model, self.guard)[0] for t in english))
        self.assertTrue(all(should_send_to_human(t, self.model, self.guard)[0] for t in portuguese))

    def test_language_guard_long_cases_both_directions(self):
        english = "please help because my account is locked and i cannot access the shared project folder today"
        portuguese = "por favor preciso de ajuda porque minha senha nao funciona e o acesso ao projeto esta bloqueado"
        self.assertFalse(should_send_to_human(english, self.model, self.guard)[0])
        self.assertTrue(should_send_to_human(portuguese, self.model, self.guard)[0])

    def test_kill_switch_forces_human_review(self):
        ticket = "the printer on the third floor is jammed and shows an error light"
        with patch.dict(os.environ, {"TICKET_CLASSIFIER_KILL_SWITCH": "true"}), \
             patch("builtins.input", return_value=ticket), \
             patch.object(cli, "OUTPUTS", self.history_dir), \
             patch("sys.stdout", new_callable=io.StringIO) as output:
            cli.classify()
            self.assertIn("modo de segurança está ativo", output.getvalue())
            with self.history_path.open(encoding="utf-8-sig") as handle:
                row = list(csv.DictReader(handle))[0]
            self.assertEqual(row["decisao"], "analise_humana")
            self.assertEqual(row["faixa_tecnica"], "modo_seguranca")

    def test_kill_switch_is_visible_in_menu(self):
        with patch.dict(os.environ, {"TICKET_CLASSIFIER_KILL_SWITCH": "1"}), \
             patch("builtins.input", return_value="0"), \
             patch("sys.stdout", new_callable=io.StringIO) as output:
            cli.main()
            self.assertIn("Modo de segurança ativo: todos os tickets vão para análise humana",
                          output.getvalue())

    def test_empty_input_fails_safe_without_storing_text(self):
        with patch("builtins.input", return_value="   "), \
             patch.object(cli, "OUTPUTS", self.history_dir), \
             patch("sys.stdout", new_callable=io.StringIO) as output:
            cli.classify()
            self.assertIn("enviar para uma pessoa", output.getvalue())
            with self.history_path.open(encoding="utf-8-sig") as handle:
                row = list(csv.DictReader(handle))[0]
            self.assertNotIn("texto", row)
            self.assertIn("texto_sha256", row)
            self.assertEqual(row["tamanho_caracteres"], "0")
            self.assertEqual(row["decisao"], "analise_humana")


class WebLayerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model, cls.manifest = load_verified_model()
        cls.guard = load_language_guard()

    def setUp(self):
        self.history_dir = ROOT / "tests" / "web_history_test_output"
        self.history_path = self.history_dir / "classification_history.csv"
        if self.history_path.exists():
            self.history_path.unlink()
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

    def tearDown(self):
        if self.history_path.exists():
            self.history_path.unlink()

    def test_routes_respond(self):
        for path in ("/", "/saude", "/avaliacao", "/avaliacao/resultado", "/controles"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)

    def test_evaluation_separates_high_band_from_effective_automation(self):
        response = self.client.get("/avaliacao/resultado")
        self.assertIn("Faixa alta do modelo".encode("utf-8"), response.data)
        self.assertIn("Encaminhamento efetivo".encode("utf-8"), response.data)
        self.assertIn("5.527".encode("utf-8"), response.data)
        self.assertIn("5.510".encode("utf-8"), response.data)

    def test_web_decision_equals_core_for_all_ten_examples(self):
        with patch.object(cli, "OUTPUTS", self.history_dir):
            for text in EXAMPLES:
                expected = classify_ticket(text, self.model, self.manifest, self.guard, False)
                response = self.client.post("/", data={"ticket": text})
                self.assertEqual(response.status_code, 200)
                self.assertIn(expected["headline"].encode("utf-8"), response.data)
                if expected["language_diversion"]:
                    self.assertNotIn("Fila sugerida".encode("utf-8"), response.data)
                else:
                    self.assertIn(expected["category_name"].encode("utf-8"), response.data)

    def test_kill_switch_blocks_automation_in_web(self):
        text = EXAMPLES[0]
        with patch.dict(os.environ, {"TICKET_CLASSIFIER_KILL_SWITCH": "true"}), \
             patch.object(cli, "OUTPUTS", self.history_dir):
            response = self.client.post("/", data={"ticket": text})
        self.assertIn("Vai para uma pessoa".encode("utf-8"), response.data)
        with self.history_path.open(encoding="utf-8-sig") as handle:
            row = list(csv.DictReader(handle))[0]
        self.assertEqual(row["decisao"], "analise_humana")
        self.assertEqual(row["faixa_tecnica"], "modo_seguranca")

    def test_web_history_never_stores_ticket_text(self):
        text = EXAMPLES[1]
        with patch.object(cli, "OUTPUTS", self.history_dir):
            self.client.post("/", data={"ticket": text})
        raw = self.history_path.read_text(encoding="utf-8-sig")
        self.assertNotIn(text, raw)
        with self.history_path.open(encoding="utf-8-sig") as handle:
            row = list(csv.DictReader(handle))[0]
        self.assertNotIn("texto", row)
        self.assertEqual(row["tamanho_caracteres"], str(len(text)))

    def test_public_mode_warns_and_does_not_write_history(self):
        text = EXAMPLES[0]
        with patch.dict(os.environ, {"TICKET_CLASSIFIER_PUBLIC_DEPLOY": "true"}), \
             patch.object(cli, "OUTPUTS", self.history_dir):
            response = self.client.post("/", data={"ticket": text})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Demonstração pública".encode("utf-8"), response.data)
        self.assertFalse(self.history_path.exists())

    def test_evaluation_is_cached(self):
        clear_evaluation_cache()
        with patch("ticket_classifier.web.evaluate.reproduce", return_value={"status": "ok"}) as reproduce_mock:
            self.assertIs(cached_evaluation(), cached_evaluation())
        reproduce_mock.assert_called_once_with()
        clear_evaluation_cache()


class StartupTest(unittest.TestCase):
    def test_occupied_default_port_uses_another(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as occupied:
            occupied.bind(("127.0.0.1", 0))
            occupied_port = occupied.getsockname()[1]
            selected = find_available_port(occupied_port)
        self.assertNotEqual(selected, occupied_port)
        self.assertGreater(selected, 0)

    def test_browser_opens_only_after_server_responds(self):
        events = []
        with patch("ticket_classifier.web.wait_until_ready",
                   side_effect=lambda *_args, **_kwargs: events.append("respondeu") or True), \
             patch("ticket_classifier.web.webbrowser.open",
                   side_effect=lambda _url: events.append("abriu") or True):
            open_browser_when_ready("http://127.0.0.1:5000/")
        self.assertEqual(events, ["respondeu", "abriu"])

    def test_browser_does_not_open_when_server_fails(self):
        with patch("ticket_classifier.web.wait_until_ready", return_value=False), \
             patch("ticket_classifier.web.webbrowser.open") as browser_mock, \
             patch("sys.stderr", new_callable=io.StringIO) as error:
            open_browser_when_ready("http://127.0.0.1:5000/", timeout=0.01)
        browser_mock.assert_not_called()
        self.assertIn("servidor não respondeu", error.getvalue())

    def test_startup_failure_is_legible_without_traceback(self):
        with patch("ticket_classifier.web.create_app", side_effect=RuntimeError("artefato ausente")), \
             patch("sys.stderr", new_callable=io.StringIO) as error:
            with self.assertRaises(SystemExit) as raised:
                main()
        self.assertEqual(raised.exception.code, 1)
        self.assertIn("Não foi possível iniciar a aplicação: artefato ausente", error.getvalue())
        self.assertNotIn("Traceback", error.getvalue())


if __name__ == "__main__":
    unittest.main()
