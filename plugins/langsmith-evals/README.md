# LangSmith Evals para Claude Code

Plugin com skill de conhecimento e tres subagentes automaticamente descobertos pelo Claude Code:

| Agent | Papel | Modelo fixado |
|---|---|---|
| `langsmith-evals-engineer` | Implementa e executa Dataset, evaluators, Experiments, backtests e gates | `sonnet` |
| `langsmith-pytest-engineer` | Implementa por TDD os oraculos deterministicos em Pytest, sem LLM-as-judge | `sonnet` |
| `langsmith-evals-auditor` | Revisa evidencia sem editar artefatos e emite GO/NO-GO/BLOCKED | `sonnet` |

Instalacao:

```bash
claude plugin install langsmith-evals@claude-skills
```

Uso:

```text
Use o langsmith-evals-engineer para criar e executar o eval desta mudanca.
Use o langsmith-pytest-engineer para implementar os contratos deterministicos.
Depois use o langsmith-evals-auditor para revisar a promocao.
```

A separacao mantem fronteiras claras: o Pytest Engineer prova contratos mecanicos, o Engineer trata o eval amplo e o Auditor decide sem autocertificacao.

A skill `/langsmith-evals` tambem pode ser usada diretamente na conversa principal.
