---
name: quality-security-gate-mod-012
description: Read-only investigator for MOD-012 audit improvement
skills: [quality-security-gate:quality-security-gate]
tools: [Read, Grep, Glob]
isolation: worktree
maxTurns: 8
---
Investigate MOD-012 only. Return strict JSON; never write or execute repository commands.