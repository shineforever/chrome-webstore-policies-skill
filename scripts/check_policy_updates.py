#!/usr/bin/env python3
"""Watch official Chrome Web Store policy pages.

Used by GitHub Actions to refresh snapshots and open a review PR.
Used locally (and by scan.py) to warn when this skill may be stale.

Does not rewrite SKILL.md / checklist.md. Policy wording changes need a human.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

USER_AGENT = (
    "chrome-webstore-policies-skill/1.1 "
    "(+https://github.com/shineforever/chrome-webstore-policies-skill)"
)
REMOTE_MANIFEST_URL = (
    "https://raw.githubusercontent.com/shineforever/"
    "chrome-webstore-policies-skill/main/sources/manifest.json"
)
INSTALL_COMMAND = (
    "npx skills add shineforever/chrome-webstore-policies-skill "
    "--agent cursor --agent claude-code --agent codex"
)

LAST_UPDATED_RE = re.compile(r"Last updated\s+(\d{4}-\d{2}-\d{2})", re.I)
DATE_MODIFIED_RE = re.compile(r'"dateModified"\s*:\s*"(\d{4}-\d{2}-\d{2})"')

SOURCES: tuple[dict[str, str], ...] = (
    {
        "id": "policies",
        "title": "Program Policies (single page)",
        "html_url": "https://developer.chrome.com/docs/webstore/program-policies/policies",
        "text_url": "https://developer.chrome.com/docs/webstore/program-policies/policies.md.txt",
    },
    {
        "id": "program-policies-index",
        "title": "Program Policies index",
        "html_url": "https://developer.chrome.com/docs/webstore/program-policies",
        "text_url": "https://developer.chrome.com/docs/webstore/program-policies.md.txt",
    },
    {
        "id": "troubleshooting",
        "title": "Troubleshooting / rejection IDs",
        "html_url": "https://developer.chrome.com/docs/webstore/troubleshooting",
        "text_url": "https://developer.chrome.com/docs/webstore/troubleshooting.md.txt",
    },
    {
        "id": "cws-dashboard-privacy",
        "title": "CWS Dashboard privacy fields",
        "html_url": "https://developer.chrome.com/docs/webstore/cws-dashboard-privacy",
        "text_url": "https://developer.chrome.com/docs/webstore/cws-dashboard-privacy.md.txt",
    },
    {
        "id": "user-data-faq",
        "title": "User Data FAQ",
        "html_url": "https://developer.chrome.com/docs/webstore/program-policies/user-data-faq",
        "text_url": "https://developer.chrome.com/docs/webstore/program-policies/user-data-faq.md.txt",
    },
    {
        "id": "deceptive-installation-tactics-faq",
        "title": "Deceptive Installation Tactics FAQ",
        "html_url": "https://developer.chrome.com/docs/webstore/program-policies/deceptive-installation-tactics-faq",
        "text_url": "https://developer.chrome.com/docs/webstore/program-policies/deceptive-installation-tactics-faq.md.txt",
    },
    {
        "id": "quality-guidelines-faq",
        "title": "Quality Guidelines FAQ",
        "html_url": "https://developer.chrome.com/docs/webstore/program-policies/quality-guidelines-faq",
        "text_url": "https://developer.chrome.com/docs/webstore/program-policies/quality-guidelines-faq.md.txt",
    },
    {
        "id": "spam-faq",
        "title": "Spam FAQ",
        "html_url": "https://developer.chrome.com/docs/webstore/program-policies/spam-faq",
        "text_url": "https://developer.chrome.com/docs/webstore/program-policies/spam-faq.md.txt",
    },
    {
        "id": "affiliate-ads-faq",
        "title": "Affiliate Ads FAQ",
        "html_url": "https://developer.chrome.com/docs/webstore/program-policies/affiliate-ads-faq",
        "text_url": "https://developer.chrome.com/docs/webstore/program-policies/affiliate-ads-faq.md.txt",
    },
)


@dataclass(frozen=True)
class SourceResult:
    source_id: str
    title: str
    html_url: str
    text_url: str
    last_updated: str | None
    sha256: str
    text: str
    previous_last_updated: str | None
    previous_sha256: str | None

    @property
    def date_changed(self) -> bool:
        return bool(self.last_updated) and self.last_updated != self.previous_last_updated

    @property
    def content_changed(self) -> bool:
        return self.previous_sha256 != self.sha256

    @property
    def signal(self) -> str:
        if self.date_changed:
            return "strong"
        if self.content_changed:
            return "weak"
        return "unchanged"


def script_parent() -> Path:
    return Path(__file__).resolve().parent.parent


def manifest_paths(root: Path) -> list[Path]:
    paths = [root / "sources" / "manifest.json"]
    skill_dir = root / ".cursor" / "skills" / "chrome-webstore-policy-review"
    if skill_dir.is_dir():
        paths.append(skill_dir / "sources" / "manifest.json")
    return paths


def load_manifest(root: Path) -> dict[str, Any]:
    path = root / "sources" / "manifest.json"
    if not path.is_file():
        return {
            "skill_version": "1.1.0",
            "policy_last_updated": "2025-05-22",
            "remote_manifest_url": REMOTE_MANIFEST_URL,
            "install": INSTALL_COMMAND,
            "sources": [],
        }
    return json.loads(path.read_text(encoding="utf-8"))


def source_lookup(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in manifest.get("sources") or [] if "id" in item}


def normalize_text(raw: str) -> str:
    return raw.replace("\r\n", "\n").replace("\r", "\n")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_last_updated(html: str) -> str | None:
    modified = DATE_MODIFIED_RE.search(html)
    if modified:
        return modified.group(1)
    match = LAST_UPDATED_RE.search(html)
    if match:
        return match.group(1)
    return None


def http_get(url: str, timeout: float, retries: int = 3) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/plain, text/html;q=0.9, */*;q=0.8",
        },
    )
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                status = getattr(response, "status", 200)
                if status >= 400:
                    raise urllib.error.HTTPError(
                        url, status, f"HTTP {status}", response.headers, None
                    )
                data = response.read()
            return data.decode("utf-8")
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            time.sleep(1.2 * (attempt + 1))
    assert last_error is not None
    raise last_error


def fetch_source(
    spec: dict[str, str],
    previous: dict[str, Any] | None,
    timeout: float,
) -> SourceResult:
    html = http_get(spec["html_url"], timeout=timeout)
    text = normalize_text(http_get(spec["text_url"], timeout=timeout))
    previous = previous or {}
    return SourceResult(
        source_id=spec["id"],
        title=spec["title"],
        html_url=spec["html_url"],
        text_url=spec["text_url"],
        last_updated=parse_last_updated(html),
        sha256=sha256_text(text),
        text=text,
        previous_last_updated=previous.get("last_updated"),
        previous_sha256=previous.get("sha256"),
    )


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def snapshot_path(root: Path, source_id: str) -> Path:
    return root / "sources" / "snapshots" / f"{source_id}.md.txt"


def build_manifest(
    previous: dict[str, Any],
    results: list[SourceResult],
    checked_at: str | None = None,
) -> dict[str, Any]:
    policies = next((item for item in results if item.source_id == "policies"), None)
    manifest = {
        "skill_version": previous.get("skill_version", "1.1.0"),
        "policy_last_updated": previous.get("policy_last_updated", "2025-05-22"),
        "remote_manifest_url": previous.get("remote_manifest_url", REMOTE_MANIFEST_URL),
        "install": previous.get("install", INSTALL_COMMAND),
        "sources": [
            {
                "id": item.source_id,
                "title": item.title,
                "html_url": item.html_url,
                "text_url": item.text_url,
                "snapshot": f"snapshots/{item.source_id}.md.txt",
                "last_updated": item.last_updated,
                "sha256": item.sha256,
            }
            for item in results
        ],
    }
    if checked_at:
        manifest["checked_at"] = checked_at
    # policy_last_updated stays human-owned. Surface the live date separately.
    if policies and policies.last_updated:
        manifest["official_policy_last_updated"] = policies.last_updated
    return manifest


def write_outputs(root: Path, manifest: dict[str, Any], results: list[SourceResult]) -> None:
    snap_dir = root / "sources" / "snapshots"
    snap_dir.mkdir(parents=True, exist_ok=True)
    for item in results:
        snapshot_path(root, item.source_id).write_text(item.text, encoding="utf-8")
    payload = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    for path in manifest_paths(root):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")


def render_report(results: list[SourceResult], checked_at: str) -> str:
    changed = [item for item in results if item.signal != "unchanged"]
    strong = [item for item in changed if item.signal == "strong"]
    if strong:
        headline = "强信号：至少一页的 Last updated 变了，需要审 Skill 文档。"
    elif changed:
        headline = "弱信号：Last updated 没变，但正文 hash 变了。可能是措辞/排版，仍请扫一眼。"
    else:
        headline = "官方来源与仓库快照一致，无需更新。"

    lines = [
        "## Chrome Web Store 政策快照",
        "",
        f"- 检查时间：`{checked_at}`",
        f"- 变更页数：{len(changed)} / {len(results)}",
        f"- {headline}",
        "",
        "| 页面 | Last updated | 正文 | 信号 |",
        "|------|--------------|------|------|",
    ]
    for item in results:
        old_date = item.previous_last_updated or "—"
        new_date = item.last_updated or "—"
        if item.date_changed:
            date_cell = f"`{old_date}` → `{new_date}`"
        else:
            date_cell = f"`{new_date}`"
        content_cell = "CHANGED" if item.content_changed else "same"
        lines.append(
            f"| [{item.title}]({item.html_url}) | {date_cell} | {content_cell} | {item.signal} |"
        )

    lines.extend(
        [
            "",
            "## 不要直接合并",
            "",
            "这个 PR 只更新 `sources/` 快照。合并前请人工核对：",
            "",
            "- [ ] 读完快照 diff，确认是新规则 / 收紧 / 放宽 / 纯排版",
            "- [ ] 如有规则变化：改 `SKILL.md`、`checklist.md`、`rejection-ids.md`、`privacy.md`",
            "- [ ] 把 `sources/manifest.json` 里的 `policy_last_updated` 改成官方政策单页日期",
            "- [ ] 改了 Skill 文档就 bump `skill_version`",
            "- [ ] 把根目录文档同步到 `.cursor/skills/chrome-webstore-policy-review/`",
            "",
            "用户本地更新：",
            "",
            f"```bash\n{INSTALL_COMMAND}\n```",
            "",
        ]
    )
    return "\n".join(lines)


def compare_dates(local: str | None, official: str | None) -> str:
    if not official:
        return "UNKNOWN"
    if not local:
        return "STALE"
    if official > local:
        return "STALE"
    return "CURRENT"


def print_freshness(timeout: float = 8.0, root: Path | None = None) -> str:
    """Print a short freshness block. Never raises to the caller of scan.py."""
    root = root or script_parent()
    manifest = load_manifest(root)
    local_date = manifest.get("policy_last_updated")
    local_version = manifest.get("skill_version", "unknown")
    install = manifest.get("install", INSTALL_COMMAND)
    remote_url = manifest.get("remote_manifest_url", REMOTE_MANIFEST_URL)

    official_date: str | None = None
    remote_version: str | None = None
    errors: list[str] = []

    try:
        html = http_get(
            "https://developer.chrome.com/docs/webstore/program-policies/policies",
            timeout=timeout,
            retries=2,
        )
        official_date = parse_last_updated(html)
    except Exception as exc:  # noqa: BLE001 — freshness must not break scan
        errors.append(f"official page: {exc}")

    try:
        remote = json.loads(http_get(remote_url, timeout=timeout, retries=2))
        remote_version = remote.get("skill_version")
    except Exception:
        # 404 until this file is on main, or GitHub is unreachable.
        remote_version = None

    status = compare_dates(local_date, official_date)
    version_status = "UNKNOWN"
    if remote_version and local_version:
        version_status = "CURRENT" if remote_version == local_version else "STALE"

    print("# policy freshness")
    print(f"status\t{status}")
    print(f"skill_policy_last_updated\t{local_date or 'unknown'}")
    print(f"official_policy_last_updated\t{official_date or 'UNKNOWN'}")
    print(f"skill_version\t{local_version}")
    print(f"github_skill_version\t{remote_version or 'UNKNOWN'}")
    print(f"github_skill_status\t{version_status}")

    if status == "STALE":
        print(
            "WARN\tpolicy source newer than this skill\t"
            f"official {official_date} > skill {local_date}"
        )
        print(f"WARN\tupdate this skill\t{install}")
        print(
            "WARN\tcontinue the review, but say the checklist may be incomplete "
            "until the skill is updated"
        )
    elif status == "UNKNOWN":
        print("UNKNOWN\tcould not verify official Last updated\tcontinue with local checklist")
    else:
        print("OK\tpolicy date matches this skill")

    if version_status == "STALE":
        print(
            "WARN\tskill_version on GitHub is different\t"
            f"local {local_version} vs github {remote_version}; {install}"
        )
    for err in errors:
        print(f"UNKNOWN\tfreshness fetch\t{err}")
    return status


def run_watch(update: bool, report_path: Path | None, timeout: float) -> int:
    root = script_parent()
    previous = load_manifest(root)
    previous_sources = source_lookup(previous)
    results: list[SourceResult] = []
    errors: list[str] = []

    for spec in SOURCES:
        try:
            results.append(
                fetch_source(spec, previous_sources.get(spec["id"]), timeout=timeout)
            )
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{spec['id']}: {exc}")

    if errors:
        for err in errors:
            print(f"ERROR\t{err}", file=sys.stderr)
        return 2

    checked_at = utc_now()
    changed = [item for item in results if item.signal != "unchanged"]
    report = render_report(results, checked_at)
    print(report)

    if report_path:
        report_path.write_text(report + "\n", encoding="utf-8")

    if not changed:
        print("\nOK\tno source changes")
        return 0

    if update:
        # Do not persist checked_at: that would open a weekly no-op PR.
        manifest = build_manifest(previous, results)
        write_outputs(root, manifest, results)
        print(f"\nWROTE\t{len(results)} snapshots and manifest")
    else:
        print("\nDRY-RUN\tpass --update to write snapshots")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--update",
        action="store_true",
        help="Write snapshots and sources/manifest.json when sources changed",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Write the markdown report to this path",
    )
    parser.add_argument(
        "--freshness",
        action="store_true",
        help="Only compare this skill's policy date with the official page",
    )
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()

    if args.freshness:
        try:
            print_freshness(timeout=min(args.timeout, 10.0))
            return 0
        except Exception as exc:  # noqa: BLE001
            print(f"UNKNOWN\tpolicy freshness check failed\t{exc}")
            return 0
    return run_watch(update=args.update, report_path=args.report, timeout=args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
