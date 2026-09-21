#!/usr/bin/env python3
"""Static preflight for Chrome Web Store policy review.

Prints findings only. The agent maps them to policies in SKILL.md.
Exit code is 0 even when findings exist, unless the path is invalid.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CODE_SUFFIXES = {".js", ".mjs", ".cjs", ".ts", ".tsx", ".html", ".htm", ".css"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next"}

REMOTE_SCRIPT = re.compile(
    r"""<script[^>]+src\s*=\s*['"]https?://""",
    re.I,
)
EVAL_LIKE = re.compile(
    r"""\b(?:eval|new\s+Function)\s*\(|set(?:Timeout|Interval)\s*\(\s*['"`]""",
)
HTTP_URL = re.compile(r"""['"]http://[^'"]+""")
IMPORT_REMOTE = re.compile(r"""\bimport\s*\(\s*['"]https?://""")
BASE64_BLOB = re.compile(r"""(?:atob|btoa|Buffer\.from)\s*\(""")
UNICODE_ESC = re.compile(r"""(?:\\u00[0-9a-fA-F]{2}){4,}""")
AFFILIATE = re.compile(
    r"""(?:[?&](?:utm_source=affiliate|aff(?:iliate)?id|tag=|ref=|clickid=)|affiliate)""",
    re.I,
)


def find_manifest(root: Path) -> Path | None:
    direct = root / "manifest.json"
    if direct.is_file():
        return direct
    matches = [p for p in root.rglob("manifest.json") if not _skip(p)]
    return matches[0] if matches else None


def _skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def iter_code_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file() or _skip(path):
            continue
        if path.suffix.lower() in CODE_SUFFIXES:
            yield path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def check_manifest_files(root: Path, manifest: dict) -> list[str]:
    findings = []
    mentioned: list[str] = []

    for key in ("background", "action", "browser_action", "page_action", "options_ui", "options_page", "sandbox"):
        value = manifest.get(key)
        if isinstance(value, str):
            mentioned.append(value)
        elif isinstance(value, dict):
            for inner in value.values():
                if isinstance(inner, str):
                    mentioned.append(inner)
                elif isinstance(inner, list):
                    mentioned.extend(x for x in inner if isinstance(x, str))

    for cs in manifest.get("content_scripts") or []:
        for key in ("js", "css"):
            mentioned.extend(cs.get(key) or [])

    web_acc = manifest.get("web_accessible_resources") or []
    if web_acc and isinstance(web_acc[0], dict):
        for item in web_acc:
            mentioned.extend(item.get("resources") or [])
    else:
        mentioned.extend(x for x in web_acc if isinstance(x, str))

    icons = manifest.get("icons") or {}
    mentioned.extend(icons.values())
    default_icon = (manifest.get("action") or {}).get("default_icon")
    if isinstance(default_icon, str):
        mentioned.append(default_icon)
    elif isinstance(default_icon, dict):
        mentioned.extend(default_icon.values())

    overrides = manifest.get("chrome_url_overrides") or {}
    mentioned.extend(x for x in overrides.values() if isinstance(x, str))

    for rel in mentioned:
        if not isinstance(rel, str) or rel.startswith(("http://", "https://", "data:")):
            if isinstance(rel, str) and rel.startswith(("http://", "https://")):
                findings.append(f"BLOCKER\tmanifest remote path\t{rel}")
            continue
        target = root / rel
        if not target.exists():
            findings.append(f"BLOCKER\tmissing file\tmanifest → {rel}")
    return findings


def scan_file(root: Path, path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [f"WARN\tbinary-or-non-utf8\t{path.relative_to(root)}"]

    rel = str(path.relative_to(root))
    findings = []
    checks = [
        (REMOTE_SCRIPT, "BLOCKER", "remote <script>"),
        (EVAL_LIKE, "RISK", "eval/new Function/string timer"),
        (IMPORT_REMOTE, "BLOCKER", "remote dynamic import"),
        (HTTP_URL, "RISK", "plaintext http URL"),
        (BASE64_BLOB, "RISK", "base64 encode/decode helper"),
        (UNICODE_ESC, "RISK", "long unicode escapes"),
        (AFFILIATE, "RISK", "possible affiliate marker"),
    ]
    for pattern, level, label in checks:
        if pattern.search(text):
            findings.append(f"{level}\t{label}\t{rel}")
    return findings


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/scan.py /path/to/extension", file=sys.stderr)
        return 2

    root = Path(sys.argv[1]).expanduser().resolve()
    if not root.exists():
        print(f"Path not found: {root}", file=sys.stderr)
        return 2

    manifest_path = find_manifest(root)
    print(f"# CWS static scan")
    print(f"root\t{root}")

    if not manifest_path:
        print("BLOCKER\tno manifest.json")
        return 0

    print(f"manifest\t{manifest_path}")
    try:
        manifest = load_json(manifest_path)
    except json.JSONDecodeError as exc:
        print(f"BLOCKER\tinvalid manifest.json\t{exc}")
        return 0

    print(f"name\t{manifest.get('name')}")
    print(f"version\t{manifest.get('version')}")
    print(f"manifest_version\t{manifest.get('manifest_version')}")
    if manifest.get("manifest_version") != 3:
        print("RISK\tnot Manifest V3\tnew CWS submissions should be MV3")

    for key in ("permissions", "optional_permissions", "host_permissions"):
        values = manifest.get(key) or []
        print(f"{key}\t{json.dumps(values, ensure_ascii=False)}")

    csp = manifest.get("content_security_policy")
    if csp:
        print(f"csp\t{json.dumps(csp, ensure_ascii=False)}")

    if manifest.get("chrome_url_overrides"):
        print(f"INFO\tchrome_url_overrides\t{json.dumps(manifest['chrome_url_overrides'])}")
    if manifest.get("chrome_settings_overrides"):
        print(f"INFO\tchrome_settings_overrides\t{json.dumps(manifest['chrome_settings_overrides'])}")

    findings = check_manifest_files(manifest_path.parent, manifest)
    for path in iter_code_files(manifest_path.parent):
        findings.extend(scan_file(manifest_path.parent, path))

    if not findings:
        print("OK\tno static findings")
        return 0

    print("# findings")
    seen = set()
    for row in findings:
        if row in seen:
            continue
        seen.add(row)
        print(row)
    print(f"# {len(seen)} finding(s). Map these to SKILL.md / rejection-ids.md; do not treat as final verdict.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
