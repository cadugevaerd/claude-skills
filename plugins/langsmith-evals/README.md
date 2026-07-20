# LangSmith Evals para Claude Code

Plugin com skill de conhecimento e tres subagentes automaticamente descobertos pelo Claude Code:

| Agent | Papel | Modelo fixado |
|---|---|---|
| `langsmith-prompt-engineer` | Cria, versiona e compara prompts com baseline e Experiments pareados | `sonnet` |
| `langsmith-evals-engineer` | Implementa e executa Dataset, evaluators, Experiments, backtests e gates | `sonnet` |
| `langsmith-evals-auditor` | Revisa evidencia sem editar artefatos e emite GO/NO-GO/BLOCKED | `sonnet` |

Instalacao:

```bash
claude plugin install langsmith-evals@claude-skills
```

Use o `langsmith-prompt-engineer` para criar candidatos, o `langsmith-evals-engineer` para executar o eval e o `langsmith-evals-auditor` para revisar a promocao.
