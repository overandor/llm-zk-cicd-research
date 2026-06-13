# Second Brain (Ollama-powered, local inference)

A minimal "second brain" indexer: it scans a directory of markdown notes and
uses a **local** [Ollama](https://ollama.com) model to generate a summary and
tags for each note. It is the practical companion to
[`docs/research/second_brain_ollama_cicd.md`](../docs/research/second_brain_ollama_cicd.md),
which discusses how local inference fits the ZK-CI privacy model described in
[`paper.md`](../paper.md).

## Why local inference

- **Privacy**: notes never leave the machine running Ollama.
- **No per-call cost**: inference is free after the model is downloaded.
- **Reproducible in CI**: a runner can install Ollama, pull a small model,
  and run the indexer without any external API keys.
- **Verifiable**: every note gets a SHA-256 content "commitment", the same
  primitive the ZK-CI framework uses as a public input when proving facts
  about private data.

## Usage

### 1. Install and start Ollama (local machine)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3.2:1b
```

### 2. Build the index

```bash
python3 second_brain/second_brain.py second_brain/notes --model llama3.2:1b
```

This writes `second_brain/index.json` containing, for each note, a
`commitment` (SHA-256 of the raw content), a `summary`, and `tags` produced
by the local model.

### Offline / CI mode

If Ollama is not running, or `--offline` is passed, the indexer falls back
to a deterministic heuristic (first heading as summary, longest words as
tags) so the pipeline always produces output:

```bash
python3 second_brain/second_brain.py second_brain/notes --offline
```

## Running the tests

```bash
python3 -m unittest discover -s second_brain/tests -v
```

The tests do not require Ollama - they use a fake client to exercise the
JSON-parsing and fallback logic.

## Files

- `ollama_client.py` - tiny stdlib-only HTTP client for the Ollama API.
- `second_brain.py` - CLI: builds `index.json` from a notes directory.
- `notes/` - sample notes used by the tests and CI.
- `tests/` - unit tests (no network or Ollama required).
