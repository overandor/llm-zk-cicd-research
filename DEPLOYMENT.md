# Deployment Guide

## Prerequisites

- None (research repository)
- Optional: [Ollama](https://ollama.com) for local LLM inference (used by `second_brain/`)

## Local Development

```bash
# View paper
cat paper.md

# Build documentation
# Add build steps as needed
```

## Second Brain (local Ollama inference)

```bash
# Run the unit tests (no Ollama required)
python3 -m unittest discover -s second_brain/tests -v

# Build the note index offline (no Ollama required)
python3 second_brain/second_brain.py second_brain/notes --offline

# Build the note index using a local Ollama model
ollama serve &
ollama pull llama3.2:1b
python3 second_brain/second_brain.py second_brain/notes --model llama3.2:1b
```

See [`second_brain/README.md`](second_brain/README.md) and
[`docs/research/second_brain_ollama_cicd.md`](docs/research/second_brain_ollama_cicd.md)
for details.

## Deployment

This is a research repository. No deployment required.
