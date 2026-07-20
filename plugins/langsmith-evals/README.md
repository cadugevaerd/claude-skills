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

Uso:

```text
Use o langsmith-prompt-engineer para criar candidatos e comparar este prompt.
Use o langsmith-evals-engineer para criar e executar o eval desta mudanca.
Depois use o langsmith-evals-auditor para revisar a promocao.
```

A separacao reduz self-certification: o Engineer nao aprova sozinho a propria rubrica e o Auditor nao corrige a evidencia que deveria revisar.

A skill `/langsmith-evals` tambem pode ser usada diretamente na conversa principal.
