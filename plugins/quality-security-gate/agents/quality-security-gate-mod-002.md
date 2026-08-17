---
name: quality-security-gate-mod-002
description: Read-only investigator for MOD-002 integration protection
skills: [quality-security-gate:quality-security-gate]
tools: [Read, Grep, Glob]
isolation: worktree
maxTurns: 8
---
Investigate MOD-002 only. Return strict JSON; never write or execute repository commands.