# Second Brain: Local Ollama Inference in CI/CD

## Abstract

This note extends the ZK-CI research direction in [`paper.md`](../../paper.md)
with a concrete, low-cost building block: a personal "second brain" knowledge
base whose summarization and tagging stage runs entirely on a locally hosted
[Ollama](https://ollama.com) model, including inside CI/CD runners. It
illustrates how the "Privacy Model" and "Content Commitment" ideas from the
main paper apply even without a full ZK-proof toolchain.

## 1. Motivation

The main paper's privacy model assumes LLM analysis happens "in a trusted
execution environment" and that prompts/responses are kept private (Section
3.3). Calling a third-party hosted API (OpenAI, Anthropic, etc.) from a CI
pipeline makes that assumption hard to audit: the notes/code sent as prompts
leave the build environment entirely.

A "second brain" - a personal knowledge base of markdown notes that gets
automatically summarized and tagged - is a good small-scale testbed for the
opposite approach: run the model *on the same machine* that holds the data,
including the CI runner.

## 2. Architecture

```
notes/*.md ──► second_brain.py ──► Ollama (localhost:11434) ──► index.json
                    │
                    └─► SHA-256 commitment per note
```

- **Ingestion**: `second_brain/second_brain.py` walks a directory of markdown
  notes.
- **Local inference**: for each note, it calls a local Ollama server
  (`/api/generate`) with a system prompt asking for a one-sentence summary
  and a small set of tags, returned as JSON.
- **Content commitment**: each note's raw bytes are hashed with SHA-256.
  This commitment is the same primitive used as a "public input" in the
  ZK-CI quality-check circuit (Section 4.2.1 of the main paper) - it lets a
  later step prove "the summary for commitment `0xabc...` was produced from
  exactly this content" without re-publishing the note itself.
- **Fallback**: if Ollama is unreachable (e.g. a CI runner without the model
  pulled yet, or `--offline`), a deterministic heuristic produces a summary
  and tags so the pipeline never hard-fails on a missing model.

## 3. CI/CD Integration

`.github/workflows/ci.yml` contains two relevant jobs:

1. **`second-brain-test`**: runs the unit tests (fully mocked, no Ollama
   needed) and then runs the indexer in `--offline` mode. This is the fast,
   always-green path that validates the pipeline logic on every push.
2. **`second-brain-ollama-inference`**: installs Ollama on the runner,
   starts the server, pulls a small model (`llama3.2:1b`), and runs the
   indexer against the real model. This job is marked
   `continue-on-error: true` because model downloads can be slow or blocked
   by a runner's network policy - it demonstrates the local-inference path
   without making it a hard CI gate.

This mirrors the "LLM Analysis -> Proof Generation -> Verification ->
Deployment" pipeline in Section 3.1 of the main paper, but with the LLM
Analysis stage running on commodity CI hardware instead of a hosted API, and
the "proof" reduced to a content-addressable commitment rather than a full
zk-SNARK.

## 4. Relationship to ZK-CI

| ZK-CI concept (paper.md) | Second-brain analogue |
|---|---|
| LLM Analysis Module | `second_brain.py` + Ollama |
| Trusted execution environment | Local machine / CI runner running the model |
| Witness (private inputs) | Note content |
| Public input / commitment | SHA-256 hash of note content |
| Proof registry | `index.json` (commitment -> summary/tags) |

A natural next step (left as future work, same as Section 6.3 of the main
paper) is to wrap `analyze_note()` in a ZK circuit that proves "the tags in
`index.json` were derived from a note matching this commitment, using model
`X`" - without revealing the note text in the proof.

## 5. Limitations

- Small local models (1-3B parameters) produce lower-quality summaries than
  hosted frontier models; this is a tradeoff for privacy and cost, not a
  free upgrade.
- The offline fallback is purely heuristic and does not reflect the model's
  actual judgment - it exists only to keep CI green when no model is
  available.
- This is not a ZK proof: the SHA-256 commitment provides integrity/binding,
  not zero-knowledge. Combining it with an actual proof system remains
  future work.
