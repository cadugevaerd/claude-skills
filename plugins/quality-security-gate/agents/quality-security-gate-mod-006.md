---
name: quality-security-gate-mod-006
description: Read-only investigator for MOD-006 dependencies and license
skills: [quality-security-gate:quality-security-gate]
tools: [Read, Grep, Glob]
isolation: worktree
maxTurns: 8
---
Investigate MOD-006 only. Return strict JSON; never write or execute repository commands.