"""Minimal client for the local Ollama REST API.

Ollama (https://ollama.com) runs LLMs locally and exposes a small HTTP API
(default: http://localhost:11434). This client wraps the two endpoints used
by the second-brain indexer: text generation and availability checks. It has
no third-party dependencies so it works in restricted CI environments.
"""

import json
import urllib.error
import urllib.request


class OllamaError(Exception):
    """Raised when the local Ollama server cannot be reached or errors out."""


class OllamaClient:
    def __init__(self, host="http://localhost:11434", model="llama3.2:1b", timeout=120):
        self.host = host.rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate(self, prompt, system=None):
        """Run a single-turn generation and return the response text."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system
        result = self._post("/api/generate", payload)
        return result.get("response", "")

    def is_available(self, timeout=None):
        """Return True if the Ollama server responds to /api/tags."""
        url = f"{self.host}/api/tags"
        try:
            with urllib.request.urlopen(url, timeout=timeout or min(self.timeout, 5)):
                return True
        except (urllib.error.URLError, OSError):
            return False

    def _post(self, path, payload):
        url = f"{self.host}{path}"
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise OllamaError(f"Failed to reach Ollama at {url}: {exc}") from exc
