"""Second Brain: a local knowledge-base indexer powered by Ollama.

Scans a directory of markdown notes and, for each note, uses a locally
running Ollama model to produce a short summary and a set of tags. Every
note also gets a SHA-256 "commitment" of its raw content - the same kind of
content commitment the ZK-CI framework (see docs/research) uses as a public
input when proving properties about private data without revealing it.

If Ollama is not reachable (or --offline is passed), the indexer falls back
to a deterministic offline heuristic so the pipeline always produces a
result - useful for CI environments without GPU/model access.
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ollama_client import OllamaClient, OllamaError  # noqa: E402

SUMMARY_SYSTEM_PROMPT = (
    "You are a 'second brain' assistant that organizes personal notes. "
    "Given the contents of a note, respond with ONLY a JSON object of the "
    'form {"summary": "<one sentence summary>", "tags": ["tag1", "tag2"]}. '
    "Use 3-5 lowercase, single-word tags."
)


def hash_content(text: str) -> str:
    """Return the SHA-256 hex digest of a note's content."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fallback_entry(text: str) -> dict:
    """Deterministic offline summary/tags used when Ollama is unavailable."""
    words = [w.strip(".,!?:;\"'()").lower() for w in text.split()]
    words = [w for w in words if len(w) > 4]
    tags = sorted(set(words))[:5]
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    return {"summary": first_line.lstrip("#").strip()[:160], "tags": tags}


def analyze_note(client, text: str) -> dict:
    """Summarize and tag a note using Ollama, falling back on any failure."""
    try:
        raw = client.generate(prompt=text, system=SUMMARY_SYSTEM_PROMPT)
        parsed = json.loads(raw)
        summary = str(parsed.get("summary", "")).strip()
        tags = [str(tag).lower() for tag in parsed.get("tags", [])]
        if not summary or not tags:
            raise ValueError("incomplete Ollama response")
        return {"summary": summary, "tags": tags}
    except (OllamaError, json.JSONDecodeError, ValueError, AttributeError):
        return fallback_entry(text)


def build_index(notes_dir: Path, client=None) -> dict:
    """Build the second-brain index for every markdown note in notes_dir."""
    entries = []
    for path in sorted(notes_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        analysis = analyze_note(client, text) if client else fallback_entry(text)
        entries.append(
            {
                "file": path.name,
                "commitment": hash_content(text),
                "summary": analysis["summary"],
                "tags": analysis["tags"],
            }
        )
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": getattr(client, "model", "offline-heuristic"),
        "notes": entries,
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Index second-brain notes using local Ollama inference."
    )
    parser.add_argument(
        "notes_dir",
        nargs="?",
        default=str(Path(__file__).resolve().parent / "notes"),
        help="Directory of markdown notes (default: second_brain/notes)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=str(Path(__file__).resolve().parent / "index.json"),
        help="Path to write the JSON index (default: second_brain/index.json)",
    )
    parser.add_argument(
        "--host", default="http://localhost:11434", help="Ollama server URL"
    )
    parser.add_argument(
        "--model", default="llama3.2:1b", help="Ollama model name to use for inference"
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip Ollama entirely and use offline heuristics",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    notes_dir = Path(args.notes_dir)
    if not notes_dir.is_dir():
        print(f"Notes directory not found: {notes_dir}", file=sys.stderr)
        return 1

    client = None
    if not args.offline:
        candidate = OllamaClient(host=args.host, model=args.model)
        if candidate.is_available():
            client = candidate
        else:
            print("Ollama not reachable, falling back to offline heuristics", file=sys.stderr)

    index = build_index(notes_dir, client)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote index with {len(index['notes'])} note(s) to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
