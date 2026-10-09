"""Fast, network-free checks for deterministic project behavior."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from check_citations import check
from research import save_outputs, slugify, summarize
from tools import RetryableError, with_retry


class FakeBackend:
    def __init__(self, report, sources):
        self.payloads = {
            "/tmp/work/report/report.md": report.encode(),
            "/tmp/work/research/sources.json": json.dumps(sources).encode(),
        }

    def download_files(self, paths):
        from deepagents.backends.protocol import FileDownloadResponse
        return [FileDownloadResponse(path=p, content=self.payloads.get(p),
                                     error=None if p in self.payloads else "file_not_found") for p in paths]


class CoreTests(unittest.TestCase):
    def test_retry_then_success(self):
        calls = []

        def operation():
            calls.append(1)
            if len(calls) < 3:
                raise RetryableError("temporary")
            return "ok"

        with patch("tools.time.sleep"):
            self.assertEqual(with_retry(operation), "ok")
        self.assertEqual(len(calls), 3)

    def test_retry_does_not_sleep_after_last_attempt(self):
        with patch("tools.time.sleep") as sleeping:
            with self.assertRaises(RetryableError):
                with_retry(lambda: (_ for _ in ()).throw(RetryableError("no")), attempts=2)
        self.assertEqual(sleeping.call_count, 1)

    def test_slugify_is_safe(self):
        self.assertEqual(slugify("../../A Topic!!"), "a-topic")
        self.assertEqual(slugify(""), "topic")
        self.assertLessEqual(len(slugify("a" * 100)), 60)

    def test_citation_validator(self):
        sources = [{"n": 1, "url": "https://example.com/a", "source": "web"}]
        report = "# T\n\nClaim [1].\n\n## References\n[1] A. web. https://example.com/a (2026-01-01)\n"
        self.assertEqual(check(report, sources), [])
        self.assertTrue(check("# T\n\nBad [2].", sources))

    def test_summary_and_atomic_save(self):
        messages = [{"tool_calls": [{"name": "task"}, {"name": "execute"}],
                     "usage_metadata": {"input_tokens": 2, "output_tokens": 3}}]
        summary = summarize(messages, 1.26, "m")
        self.assertEqual(summary["subagent_calls"], 1)
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            sources = [{"n": 1, "url": "https://example.com/a", "source": "web"}]
            path = save_outputs(FakeBackend("# report", sources), "A Topic", messages, 1.26, "m", Path(folder))
            self.assertTrue(path.exists())
            self.assertEqual(json.loads((Path(folder) / "a-topic.meta.json").read_text())["n_sources"], 1)


if __name__ == "__main__":
    unittest.main()
