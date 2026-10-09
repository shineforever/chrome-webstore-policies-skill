#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_policy_updates import (  # noqa: E402
    SourceResult,
    compare_dates,
    parse_last_updated,
    render_report,
    sha256_text,
    normalize_text,
)


def _result(**kwargs) -> SourceResult:
    defaults = dict(
        source_id="policies",
        title="Program Policies (single page)",
        html_url="https://example.test/policies",
        text_url="https://example.test/policies.md.txt",
        last_updated="2025-05-22",
        sha256="abc",
        text="hello",
        previous_last_updated="2025-05-22",
        previous_sha256="abc",
    )
    defaults.update(kwargs)
    return SourceResult(**defaults)


class ParseLastUpdatedTests(unittest.TestCase):
    def test_prefers_date_modified(self) -> None:
        html = (
            '{"dateModified": "2025-05-22"}'
            "<p>Last updated 2024-01-01 UTC.</p>"
        )
        self.assertEqual(parse_last_updated(html), "2025-05-22")

    def test_falls_back_to_visible_text(self) -> None:
        self.assertEqual(
            parse_last_updated("<p>Last updated 2026-07-20 UTC.</p>"),
            "2026-07-20",
        )

    def test_missing(self) -> None:
        self.assertIsNone(parse_last_updated("<html>no date</html>"))


class ClassifyTests(unittest.TestCase):
    def test_unchanged(self) -> None:
        self.assertEqual(_result().signal, "unchanged")

    def test_date_change_is_strong(self) -> None:
        item = _result(last_updated="2026-01-01", sha256="new")
        self.assertEqual(item.signal, "strong")
        self.assertTrue(item.date_changed)

    def test_hash_only_is_weak(self) -> None:
        item = _result(sha256="new-hash")
        self.assertEqual(item.signal, "weak")
        self.assertTrue(item.content_changed)
        self.assertFalse(item.date_changed)

    def test_missing_dates_are_not_strong(self) -> None:
        item = _result(
            last_updated=None,
            previous_last_updated=None,
            sha256="same",
            previous_sha256="same",
        )
        self.assertEqual(item.signal, "unchanged")
        self.assertFalse(item.date_changed)


class FreshnessStatusTests(unittest.TestCase):
    def test_current(self) -> None:
        self.assertEqual(compare_dates("2025-05-22", "2025-05-22"), "CURRENT")

    def test_stale_when_official_newer(self) -> None:
        self.assertEqual(compare_dates("2025-05-22", "2026-01-01"), "STALE")

    def test_unknown_without_official(self) -> None:
        self.assertEqual(compare_dates("2025-05-22", None), "UNKNOWN")


class ReportTests(unittest.TestCase):
    def test_strong_signal_copy(self) -> None:
        report = render_report(
            [_result(last_updated="2026-01-01", sha256="new")],
            "2026-10-09T00:00:00Z",
        )
        self.assertIn("强信号", report)
        self.assertIn("不要直接合并", report)

    def test_normalize_hash_stable(self) -> None:
        self.assertEqual(
            sha256_text(normalize_text("a\r\nb\r\n")),
            sha256_text("a\nb\n"),
        )


if __name__ == "__main__":
    raise SystemExit(unittest.main())
