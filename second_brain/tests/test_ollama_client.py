import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ollama_client import OllamaClient, OllamaError  # noqa: E402


class TestOllamaClient(unittest.TestCase):
    def test_is_available_false_when_unreachable(self):
        client = OllamaClient(host="http://127.0.0.1:1", timeout=1)
        self.assertFalse(client.is_available())

    def test_generate_raises_ollama_error_when_unreachable(self):
        client = OllamaClient(host="http://127.0.0.1:1", model="llama3.2:1b", timeout=1)
        with self.assertRaises(OllamaError):
            client.generate("hello")


if __name__ == "__main__":
    unittest.main()
