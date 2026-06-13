# Example: Second Brain with Local Ollama Inference

## Overview

This example shows how to run the `second_brain` indexer (see
[`second_brain/README.md`](../second_brain/README.md)) both locally with a
real Ollama model and in CI with the offline fallback, following the
local-inference privacy model described in
[`docs/research/second_brain_ollama_cicd.md`](../docs/research/second_brain_ollama_cicd.md).

## Use Case

- Keep a personal knowledge base ("second brain") of markdown notes.
- Automatically summarize and tag new notes using a model that never sends
  the note content off the machine.
- Produce a content commitment (SHA-256) per note so downstream tooling can
  verify which version of a note a given summary corresponds to.

## Local Workflow (with Ollama)

```bash
# 1. Install and start Ollama, pull a small model
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3.2:1b

# 2. Index your notes
python3 second_brain/second_brain.py second_brain/notes --model llama3.2:1b

# 3. Inspect the result
cat second_brain/index.json
```

Each entry in `index.json` looks like:

```json
{
  "file": "zero_knowledge_proofs.md",
  "commitment": "afdbe319e1bc1b3ca9e3e421fc23c275560958649ce5...",
  "summary": "Zero-knowledge proofs let a prover convince a verifier without revealing extra information.",
  "tags": ["zk-snarks", "privacy", "verification", "proofs", "cicd"]
}
```

## CI Workflow (offline fallback)

In `.github/workflows/ci.yml`, the `second-brain-test` job runs without
Ollama installed:

```bash
python -m unittest discover -s second_brain/tests -v
python second_brain/second_brain.py second_brain/notes --offline -o second_brain/index.json
```

This keeps the pipeline fast and dependency-free while still exercising the
indexing logic and commitment generation.

A separate `second-brain-ollama-inference` job installs Ollama on the runner
and repeats the indexing step with a real model, demonstrating that the same
script works identically against local inference in CI as it does on a
developer machine.
