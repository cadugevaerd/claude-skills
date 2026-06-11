# claude-skills

Coleção de [Agent Skills](https://docs.claude.com/en/docs/claude-code/skills) para Claude Code, distribuídas como **plugin marketplace** — cada skill é um plugin, instalável individualmente e disponível em qualquer sessão.

| Skill | O que faz |
|-------|-----------|
| **`backlog`** | Fonte da verdade de itens diferidos (`.specify/backlog.json`): registra, tria, promove e resolve features/bugs/débitos técnicos. Faz bootstrap da estrutura no projeto (JSON + `BACKLOG.md` + seção no `CLAUDE.md`) e, a cada execução, varre o projeto migrando TODOs/FIXMEs soltos e listas de pendências para a fonte da verdade. |
| **`code-review-cadu`** | Code review de PR com **veredicto GO/NO-GO por finding**: GO = corrigir nesta PR antes do merge; NO-GO = registrar no backlog (`.specify/backlog.json` via skill `/backlog`, após confirmação). Fork do plugin oficial `code-review` da Anthropic (Apache-2.0). |
| **`grillme-langgraph`** | Entrevista técnica que transforma a descrição de um processo no rascunho de um fluxo **LangGraph** — diagrama do grafo, schema do State (Regra CRUE), tabela de nodes determinístico vs não-determinístico. |
| **`grillme-gestor`** | Versão não-técnica da `grillme-langgraph`: o gestor descreve o processo em linguagem comum (sem jargão) e recebe **o mesmo** artefato técnico em markdown. |

## Instalação

### Recomendada — plugin do Claude Code (Windows, Linux e macOS)

O repo é um **plugin marketplace** do Claude Code: mesmo comando em qualquer SO,
sem dependências além do próprio Claude Code. No terminal:

```bash
# 1. registrar o marketplace (uma vez)
claude plugin marketplace add cadugevaerd/claude-skills

# 2. instalar só o que você quer
claude plugin install backlog@claude-skills
claude plugin install code-review-cadu@claude-skills
claude plugin install grillme-gestor@claude-skills
claude plugin install grillme-langgraph@claude-skills
```

Ou dentro de uma sessão do Claude Code:

```
/plugin marketplace add cadugevaerd/claude-skills
/plugin install backlog@claude-skills
```

Gerenciamento depois:

```bash
claude plugin list                                  # o que está instalado
claude plugin update backlog@claude-skills          # atualiza um plugin (reinicie o Claude Code)
claude plugin marketplace update claude-skills      # atualiza o catálogo do marketplace
claude plugin uninstall backlog@claude-skills       # remove
```

### Alternativa — instalador PowerShell (Windows)

O instalador descobre as skills do repositório e abre um **menu para selecionar
quais instalar** em `~/.claude/skills`:

```powershell
irm https://raw.githubusercontent.com/cadugevaerd/claude-skills/main/install.ps1 | iex
```

Sem menu (direto ao ponto), com o script local:

```powershell
.\install.ps1 -Skills backlog              # instala apenas uma
.\install.ps1 -Skills backlog,grillme-gestor
.\install.ps1 -Skills all                  # todas
.\install.ps1 -Force                       # sobrescreve sem perguntar
```

Para o gestor — instalar APENAS a `grillme-gestor`:

```powershell
irm https://raw.githubusercontent.com/cadugevaerd/claude-skills/main/install-gestor.ps1 | iex
```

### Instalação manual (qualquer SO)

Copie as pastas desejadas de `plugins/<nome>/skills/` para `~/.claude/skills/`:

```bash
git clone https://github.com/cadugevaerd/claude-skills.git
cp -r claude-skills/plugins/backlog/skills/backlog ~/.claude/skills/
```

Reinicie o Claude Code (ou abra uma nova sessão).

## Uso

```
/backlog               # registrar/triar/promover itens diferidos (faz bootstrap se preciso)
/code-review-cadu 42   # review da PR #42 com veredicto GO/NO-GO + backlog
/grillme-langgraph     # design LangGraph — versão técnica
/grillme-gestor        # design LangGraph — versão para o gestor
```

## Sobre as skills

### backlog

Opera a fonte da verdade única de trabalho diferido do projeto (`.specify/backlog.json`, itens `BL-NNNN` com type/status/priority). Na primeira execução num projeto, cria a estrutura base e a instrução normativa no `CLAUDE.md`. Em toda execução, varre o projeto por backlog não estruturado (TODOs/FIXMEs soltos, `TODO.md`, listas de pendências) e migra para a estrutura padrão. Operações: `add`, `list`, `promote`, `resolve`, `discard`, `init`.

### code-review-cadu

Fork do plugin oficial `code-review` da Anthropic (Apache-2.0), mantendo o pipeline original (gate de elegibilidade → 5 agentes revisores paralelos → scoring de confiança 0-100 → filtro ≥80 → comentário na PR) e adicionando a triagem: cada finding recebe **GO** (bloqueia merge: correctness, segurança, perda de dados, regressão, contrato com infra real) ou **NO-GO** (cleanup, refactor, débito, eficiência — diferível). O comentário na PR prefixa cada item com o veredicto; os NO-GO são apresentados ao usuário e, **só após confirmação**, registrados em lote no backlog do projeto via `/backlog`, com o `BL-NNNN` citado em cada um.

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
