---
name: quality-security-gate-mod-007
description: Read-only investigator for MOD-007 hardened CI
skills: [quality-security-gate:quality-security-gate]
tools: [Read, Grep, Glob]
isolation: worktree
maxTurns: 8
---
Investigate MOD-007 only. Return strict JSON; never write or execute repository commands.