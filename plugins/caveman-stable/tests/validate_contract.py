#!/usr/bin/env python3
"""Deterministic packaging and contract checks for caveman-stable."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO_ROOT / "plugins/caveman-stable"
STYLE = PLUGIN_ROOT / "output-styles/caveman-stable.md"
CONTRACT = PLUGIN_ROOT / "skills/caveman-stable/references/output-contract.md"
SHARED_MANIFEST = PLUGIN_ROOT / "tests/shared-files.sha256"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(path: Path) -> str:
    require(path.is_file(), f"missing: {path}")
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    for line in text.splitlines():
        require(":" in line, f"invalid frontmatter line: {line!r}")
        key, raw_value = (part.strip() for part in line.split(":", 1))
        require(bool(key), f"empty frontmatter key: {line!r}")
        require(key not in fields, f"duplicate frontmatter key: {key}")
        if raw_value == "true":
            value: Any = True
        elif raw_value == "false":
            value = False
        else:
            value = raw_value
        fields[key] = value
    return fields


def verify_shared_files() -> None:
    for line in read(SHARED_MANIFEST).splitlines():
        digest, relative = line.split("  ", 1)
        payload = (PLUGIN_ROOT / relative).read_bytes()
        require(hashlib.sha256(payload).hexdigest() == digest, relative)


def main() -> None:
    manifest = json.loads(read(PLUGIN_ROOT / ".claude-plugin/plugin.json"))
    marketplace = json.loads(read(REPO_ROOT / ".claude-plugin/marketplace.json"))
    require(manifest["name"] == "caveman-stable", "wrong plugin name")
    require(manifest["version"] == "1.0.0", "wrong plugin version")
    require("hooks" not in manifest, "Claude plugin must not declare hooks")

    entries = [item for item in marketplace["plugins"] if item["name"] == "caveman-stable"]
    require(len(entries) == 1, "marketplace must contain exactly one caveman-stable entry")
    entry = entries[0]
    require(entry["version"] == manifest["version"], "marketplace version mismatch")
    require(entry["source"] == "./plugins/caveman-stable", "wrong marketplace source")
    require("hooks" not in entry, "marketplace entry must not declare hooks")

    style = read(STYLE)
    match = re.fullmatch(r"---\n(?P<frontmatter>.*?)\n---\n(?P<body>.*)", style, re.DOTALL)
    if match is None:
        raise AssertionError("invalid output-style frontmatter")
    frontmatter = parse_frontmatter(match.group("frontmatter"))
    require(
        frontmatter
        == {
            "name": "caveman-stable",
            "description": "Stable concise technical output that preserves coding behavior and accuracy.",
            "keep-coding-instructions": True,
            "force-for-plugin": True,
        },
        "unexpected output-style frontmatter",
    )
    require(match.group("body") == "\n" + read(CONTRACT), "output-style body differs from contract")
    require(list((PLUGIN_ROOT / "output-styles").glob("*.md")) == [STYLE], "unexpected output styles")
    require(not (PLUGIN_ROOT / "hooks").exists(), "Claude plugin must not contain hooks directory")

    verify_shared_files()
    require(read(PLUGIN_ROOT / "LICENSE").startswith("MIT License\n"), "MIT license missing")
    upstream = read(PLUGIN_ROOT / "UPSTREAM.md")
    require("JuliusBrussee/caveman" in upstream, "upstream attribution missing")
    require(
        "0d95a81d35a9f2d123a5e9430d1cfc43d55f1bb0" in upstream,
        "upstream reference commit missing",
    )

    forbidden = b"Her" + b"mes"
    for path in PLUGIN_ROOT.rglob("*"):
        if path.is_file():
            require(forbidden not in path.read_bytes(), f"forbidden runtime reference: {path}")

    plugin_readme = read(PLUGIN_ROOT / "README.md")
    for phrase in (
        "claude plugin marketplace add cadugevaerd/claude-skills",
        "claude plugin install caveman-stable@claude-skills",
        "force-for-plugin: true",
        "/reload-plugins",
        "/clear",
        "subagents comuns",
        "disable",
        "uninstall",
    ):
        require(phrase.lower() in plugin_readme.lower(), phrase)

    root_readme = read(REPO_ROOT / "README.md")
    require(
        root_readme.count("claude plugin install caveman-stable@claude-skills") == 1,
        "root README install command missing or duplicated",
    )
    require("não é compatível com a instalação manual" in root_readme.lower(), "manual install warning missing")
    print("caveman-stable Claude contract: OK")


if __name__ == "__main__":
    main()
