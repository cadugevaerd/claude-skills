#!/usr/bin/env python3
"""Deterministic packaging and contract checks for caveman-stable."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO_ROOT / "plugins/caveman-stable"
STYLE = PLUGIN_ROOT / "output-styles/caveman-stable.md"
CONTRACT = PLUGIN_ROOT / "skills/caveman-stable/references/output-contract.md"
SHARED_MANIFEST = PLUGIN_ROOT / "tests/shared-files.sha256"


def read(path: Path) -> str:
    assert path.is_file(), f"missing: {path}"
    return path.read_text(encoding="utf-8")


def verify_shared_files() -> None:
    for line in read(SHARED_MANIFEST).splitlines():
        digest, relative = line.split("  ", 1)
        payload = (PLUGIN_ROOT / relative).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == digest, relative


def main() -> None:
    manifest = json.loads(read(PLUGIN_ROOT / ".claude-plugin/plugin.json"))
    marketplace = json.loads(read(REPO_ROOT / ".claude-plugin/marketplace.json"))
    assert manifest["name"] == "caveman-stable"
    assert manifest["version"] == "1.0.0"

    entries = [item for item in marketplace["plugins"] if item["name"] == "caveman-stable"]
    assert len(entries) == 1
    assert entries[0]["version"] == manifest["version"]
    assert entries[0]["source"] == "./plugins/caveman-stable"

    style = read(STYLE)
    match = re.fullmatch(r"---\n(?P<frontmatter>.*?)\n---\n(?P<body>.*)", style, re.DOTALL)
    assert match, "invalid output-style frontmatter"
    frontmatter = match.group("frontmatter")
    assert "name: caveman-stable" in frontmatter
    assert "keep-coding-instructions: true" in frontmatter
    assert "force-for-plugin: true" in frontmatter
    assert match.group("body").lstrip("\n") == read(CONTRACT)
    assert list((PLUGIN_ROOT / "output-styles").glob("*.md")) == [STYLE]
    assert not (PLUGIN_ROOT / "hooks").exists()

    verify_shared_files()
    assert read(PLUGIN_ROOT / "LICENSE").startswith("MIT License\n")
    upstream = read(PLUGIN_ROOT / "UPSTREAM.md")
    assert "JuliusBrussee/caveman" in upstream
    assert "0d95a81d35a9f2d123a5e9430d1cfc43d55f1bb0" in upstream

    package_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in PLUGIN_ROOT.rglob("*")
        if path.is_file() and path.suffix in {".md", ".json"}
    )
    assert ("Her" + "mes") not in package_text

    plugin_readme = read(PLUGIN_ROOT / "README.md")
    for phrase in (
        "claude plugin marketplace add cadugevaerd/claude-skills",
        "claude plugin install caveman-stable@claude-skills",
        "force-for-plugin: true",
        "/clear",
        "subagents comuns",
        "disable",
        "uninstall",
    ):
        assert phrase.lower() in plugin_readme.lower(), phrase

    root_readme = read(REPO_ROOT / "README.md")
    assert root_readme.count("claude plugin install caveman-stable@claude-skills") == 1
    print("caveman-stable Claude contract: OK")


if __name__ == "__main__":
    main()
