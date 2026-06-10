# claude-skills

Coleção de [Agent Skills](https://docs.claude.com/en/docs/claude-code/skills) para Claude Code, instaláveis individualmente em `~/.claude/skills` (globais — disponíveis em qualquer sessão).

| Skill | O que faz |
|-------|-----------|
| **`backlog`** | Fonte da verdade de itens diferidos (`.specify/backlog.json`): registra, tria, promove e resolve features/bugs/débitos técnicos. Faz bootstrap da estrutura no projeto (JSON + `BACKLOG.md` + seção no `CLAUDE.md`) e, a cada execução, varre o projeto migrando TODOs/FIXMEs soltos e listas de pendências para a fonte da verdade. |
| **`grillme-langgraph`** | Entrevista técnica que transforma a descrição de um processo no rascunho de um fluxo **LangGraph** — diagrama do grafo, schema do State (Regra CRUE), tabela de nodes determinístico vs não-determinístico. |
| **`grillme-gestor`** | Versão não-técnica da `grillme-langgraph`: o gestor descreve o processo em linguagem comum (sem jargão) e recebe **o mesmo** artefato técnico em markdown. |

## Instalação (global)

Uma linha no PowerShell — o instalador descobre as skills do repositório e abre um **menu para selecionar quais instalar**:

```powershell
irm https://raw.githubusercontent.com/cadugevaerd/claude-skills/main/install.ps1 | iex
```

Sem menu (direto ao ponto), clonando o repo ou com o script local:

```powershell
.\install.ps1 -Skills backlog              # instala apenas uma
.\install.ps1 -Skills backlog,grillme-gestor
.\install.ps1 -Skills all                  # todas
.\install.ps1 -Force                       # sobrescreve sem perguntar
```

### Para o gestor — instalar APENAS a `grillme-gestor`

```powershell
irm https://raw.githubusercontent.com/cadugevaerd/claude-skills/main/install-gestor.ps1 | iex
```

Depois, abra o Claude Code e use `/grillme-gestor`. (Requer o Claude Code instalado.)

### Instalação manual (qualquer SO)

Copie as pastas desejadas de `skills/` para `~/.claude/skills/`:

```bash
git clone https://github.com/cadugevaerd/claude-skills.git
cp -r claude-skills/skills/backlog ~/.claude/skills/
```

Reinicie o Claude Code (ou abra uma nova sessão).

## Uso

```
/backlog               # registrar/triar/promover itens diferidos (faz bootstrap se preciso)
/grillme-langgraph     # design LangGraph — versão técnica
/grillme-gestor        # design LangGraph — versão para o gestor
```

## Sobre as skills

### backlog

Opera a fonte da verdade única de trabalho diferido do projeto (`.specify/backlog.json`, itens `BL-NNNN` com type/status/priority). Na primeira execução num projeto, cria a estrutura base e a instrução normativa no `CLAUDE.md`. Em toda execução, varre o projeto por backlog não estruturado (TODOs/FIXMEs soltos, `TODO.md`, listas de pendências) e migra para a estrutura padrão. Operações: `add`, `list`, `promote`, `resolve`, `discard`, `init`.

### grillme-langgraph / grillme-gestor

O Claude entrevista você (uma pergunta por vez), confirma o entendimento e gera o rascunho do fluxo. A saída contém:

1. **Resumo do fluxo** — objetivo, entrada, saída, padrão dominante.
2. **Diagrama Mermaid** — `flowchart TD` com nodes DET (retângulo), NÃO-DET roteado (losango), agent-as-node (subrotina) e pontos de State-Check/HITL.
3. **Schema do State (CRUE)** — só dado bruto, com a flag `status`.
4. **Tabela de nodes** — tipo, determinismo, mecanismo de aresta, responsabilidade.
5. **Explicação de cada node** — o que lê, faz e retorna.

A `grillme-gestor` salva o resultado como arquivo `.md` para você enviar. O padrão técnico de referência (Thinking in LangGraph, Regra CRUE, State-Check, agent-as-node vs nodes explícitos, 6 padrões de workflow) está em cada skill, em `references/padrao-langgraph.md`.

## Licença

MIT — veja [LICENSE](LICENSE).
