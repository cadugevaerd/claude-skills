# claude-skills

Coleção de [Agent Skills](https://docs.claude.com/en/docs/claude-code/skills) para Claude Code, distribuídas como **plugin marketplace** — cada skill é um plugin, instalável individualmente e disponível em qualquer sessão.

| Skill | O que faz |
|-------|-----------|
| **`langsmith-evals`** | Prompt Engineering, engenharia e auditoria LangSmith-first. Inclui `langsmith-prompt-engineer`, `langsmith-evals-engineer` e `langsmith-evals-auditor`, fixados em `sonnet`. |

## Instalação

```bash
claude plugin marketplace add cadugevaerd/claude-skills
claude plugin install langsmith-evals@claude-skills
```

## Uso

```
/langsmith-evals <sistema ou mudança a avaliar; prompt|engineer|audit>
```

## Licença

MIT — veja [LICENSE](LICENSE).
