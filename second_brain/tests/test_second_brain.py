import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from second_brain import analyze_note, build_index, fallback_entry, hash_content  # noqa: E402


class FakeOllamaClient:
    """Stand-in for OllamaClient that returns a canned response."""

    def __init__(self, response, model="fake-model"):
        self.response = response
        self.model = model

    def generate(self, prompt, system=None):
        return self.response


class TestHashContent(unittest.TestCase):
    def test_deterministic_and_sensitive_to_content(self):
        self.assertEqual(hash_content("hello"), hash_content("hello"))
        self.assertNotEqual(hash_content("hello"), hash_content("world"))
        self.assertEqual(len(hash_content("hello")), 64)


class TestFallbackEntry(unittest.TestCase):
    def test_extracts_summary_and_tags(self):
        text = "# Zero-Knowledge Proofs\n\nThey enable verifiable computation."
        entry = fallback_entry(text)
        self.assertEqual(entry["summary"], "Zero-Knowledge Proofs")
        self.assertTrue(all(len(tag) > 4 for tag in entry["tags"]))
        self.assertEqual(entry["tags"], sorted(entry["tags"]))


class TestAnalyzeNote(unittest.TestCase):
    def test_uses_ollama_json_response(self):
        client = FakeOllamaClient('{"summary": "A test note.", "tags": ["ci", "ollama", "zk"]}')
        entry = analyze_note(client, "irrelevant text")
        self.assertEqual(entry["summary"], "A test note.")
        self.assertEqual(entry["tags"], ["ci", "ollama", "zk"])

    def test_falls_back_on_invalid_json(self):
        client = FakeOllamaClient("not json")
        entry = analyze_note(client, "# Local inference\n\nRuns models on-device.")
        self.assertEqual(entry, fallback_entry("# Local inference\n\nRuns models on-device."))

    def test_falls_back_on_incomplete_response(self):
        client = FakeOllamaClient('{"summary": ""}')
        entry = analyze_note(client, "# Pipelines\n\nAutomate builds and deploys.")
        self.assertEqual(entry, fallback_entry("# Pipelines\n\nAutomate builds and deploys."))


class TestBuildIndex(unittest.TestCase):
    def test_offline_index_contains_commitments_for_each_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            notes_dir = Path(tmp)
            (notes_dir / "a.md").write_text("# Note A\n\nLocal inference keeps data private.\n")
            (notes_dir / "b.md").write_text("# Note B\n\nContinuous integration runs checks.\n")

            index = build_index(notes_dir, client=None)

            self.assertEqual(len(index["notes"]), 2)
            self.assertEqual(index["model"], "offline-heuristic")
            files = {entry["file"] for entry in index["notes"]}
            self.assertEqual(files, {"a.md", "b.md"})
            for entry in index["notes"]:
                self.assertEqual(len(entry["commitment"]), 64)
                self.assertIn("summary", entry)
                self.assertIn("tags", entry)

    def test_index_is_json_serializable(self):
        with tempfile.TemporaryDirectory() as tmp:
            notes_dir = Path(tmp)
            (notes_dir / "a.md").write_text("# Note A\n\nSome content.\n")
            index = build_index(notes_dir, client=None)
            json.dumps(index)  # should not raise


if __name__ == "__main__":
    unittest.main()
