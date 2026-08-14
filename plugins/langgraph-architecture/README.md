# LangGraph Architecture para Claude Code

Plugin com duas skills que delegam obrigatoriamente a dois subagentes Opus em worktrees isolados:

| Skill | Subagente | Modelo | Fronteira |
|---|---|---|---|
| `/langgraph-architecture:langgraph-architecture-plan` | `langgraph-architecture:langgraph-architect` | `opus` + `max` | cria somente o plano |
| `/langgraph-architecture:langgraph-repository-review` | `langgraph-architecture:langgraph-reviewer` | `opus` + `max` | read-only |

## Instalação

```bash
claude plugin install langgraph-architecture@claude-skills
```

## Uso

```text
/langgraph-architecture:langgraph-architecture-plan repo=. planeje um chatbot corporativo com RAG
/langgraph-architecture:langgraph-repository-review repo=. revise esta implementação e liste os problemas
```

O Architect cria somente `LANGGRAPH-ARCHITECTURE-PLAN.md`. O Reviewer lista findings comprovados sem editar o repositório. Ambos declaram `isolation: worktree`; se o subagente não estiver disponível, a skill retorna `BLOCKED` sem fallback genérico.
