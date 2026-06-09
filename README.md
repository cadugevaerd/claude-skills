# grillme-langgraph skills

Duas [Agent Skills](https://docs.claude.com/en/docs/claude-code/skills) para Claude Code que transformam a descrição de um processo no rascunho de um fluxo **LangGraph** — diagrama do grafo, schema do State (Regra CRUE), tabela de nodes determinístico vs não-determinístico e a explicação de cada node.

| Skill | Para quem | Perguntas | Saída |
|-------|-----------|-----------|-------|
| **`grillme-langgraph`** | Desenvolvedor | Técnicas (nodes, state, determinismo, agent-as-node) | Design LangGraph completo |
| **`grillme-gestor`** | Gestor / não-técnico | Só de negócio (sem jargão) | **A mesma** saída técnica, em markdown |

A `grillme-gestor` é a versão não-técnica: o gestor descreve o processo em linguagem comum e o Claude faz toda a tradução para o design LangGraph. As duas produzem o **mesmo artefato** final.

## Instalação (global)

Uma linha no PowerShell — instala em `~/.claude/skills` e fica disponível em qualquer sessão:

```powershell
irm https://raw.githubusercontent.com/cadugevaerd/grillme-langgraph-skills/main/install.ps1 | iex
```

Instalar apenas uma das skills, ou forçar sobrescrita:

```powershell
# baixa o instalador e roda com opções
$i = irm https://raw.githubusercontent.com/cadugevaerd/grillme-langgraph-skills/main/install.ps1
$i | iex
# ou, clonando o repo:
.\install.ps1 -Skills grillme-gestor
.\install.ps1 -Force
```

### Instalação manual

Copie as pastas de `skills/` para `~/.claude/skills/`:

```
~/.claude/skills/grillme-langgraph/
~/.claude/skills/grillme-gestor/
```

Reinicie o Claude Code (ou abra uma nova sessão).

## Uso

```
/grillme-langgraph     # versão técnica
/grillme-gestor        # versão para o gestor
```

O Claude entrevista você (uma pergunta por vez), confirma o entendimento e gera o rascunho do fluxo. A `grillme-gestor` salva o resultado como arquivo `.md` para você enviar.

## O que a saída contém

1. **Resumo do fluxo** — objetivo, entrada, saída, padrão dominante.
2. **Diagrama Mermaid** — `flowchart TD` com nodes DET (retângulo), NÃO-DET roteado (losango), agent-as-node (subrotina) e pontos de State-Check/HITL.
3. **Schema do State (CRUE)** — só dado bruto, com a flag `status`.
4. **Tabela de nodes** — tipo, determinismo, mecanismo de aresta, responsabilidade.
5. **Explicação de cada node** — o que lê, faz e retorna.

O padrão técnico de referência (Thinking in LangGraph, Regra CRUE, State-Check, agent-as-node vs nodes explícitos, 6 padrões de workflow) está em cada skill, em `references/padrao-langgraph.md`.

## Licença

MIT — veja [LICENSE](LICENSE).
