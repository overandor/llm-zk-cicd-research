# Local Inference with Ollama

Ollama runs open-weight LLMs (Llama, Mistral, Qwen, etc.) entirely on local
hardware and exposes a simple REST API on http://localhost:11434.

For a "second brain" knowledge base, local inference means notes never leave
the machine: summarization, tagging, and search embeddings are generated
on-device. This avoids sending proprietary notes to a third-party API and
keeps inference cost at zero after the model is downloaded.

In CI/CD, a runner can install Ollama, pull a small model such as
llama3.2:1b, and use it to analyze build artifacts or documentation without
any external network calls during the actual inference step.
