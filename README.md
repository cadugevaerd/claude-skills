# claude-skills

Coleção de [Agent Skills](https://docs.claude.com/en/docs/claude-code/skills) para Claude Code, distribuídas como **plugin marketplace** — cada skill é um plugin, instalável individualmente e disponível em qualquer sessão.

| Skill | O que faz |
|-------|-----------|
| **`backlog`** | Fonte da verdade GLOBAL de itens diferidos (`~/.backlog/backlog.json`): um backlog único para todos os repositórios, identificado por `repo` + `BL-NNNN`. Registra, tria, promove, resolve, descarta e consolida duplicatas auditáveis com `merge`; gera `consolidado_backlog.md` por clusters de negócio, em linguagem não técnica, com problema e resolução por atividade. |
| **`code-review-cadu`** | Code review de PR com **veredicto GO/NO-GO por finding** (sobre o merge): NO-GO = merge bloqueado, corrigir nesta PR; GO = merge pode seguir, finding diferível → backlog GLOBAL (`~/.backlog/backlog.json` via skill `/backlog`, após confirmação). Fork do plugin oficial `code-review` da Anthropic (Apache-2.0). |
| **`code-debug`** | Diagnóstico diagnose-only: recebe comando/log, reproduz, coleta evidências, testa hipóteses e entrega relatório sem executar correções. |
| **`grillme-langgraph`** | Entrevista técnica que transforma a descrição de um processo no rascunho de um fluxo **LangGraph** — diagrama do grafo, schema do State (Regra CRUE), tabela de nodes determinístico vs não-determinístico. |
| **`grillme-gestor`** | Versão não-técnica da `grillme-langgraph`: o gestor descreve o processo em linguagem comum (sem jargão) e recebe **o mesmo** artefato técnico em markdown. |
| **`rag-kag-decision`** | Decide quando usar RAG, KAG, GraphRAG ou abordagem híbrida conforme documentos, entidades, relações, regras, temporalidade, custo e risco. |
| **`modelos-custo-beneficio`** | Consulta OpenRouter e lista até 5 candidatos para Model Engineering Eval, com inteligência Artificial Analysis >35 via OpenRouter Benchmarks, reasoning controlável, throughput p75/p50 ≥60 t/s e variantes `:exacto`/`:nitro`; não decide runtime. |
| **`facilitador-reunioes`** | Cria convites, objetivos claros, pré-briefing, roteiro de condução e próximos passos para reuniões objetivas. |
| **`langsmith-evals`** | Prompt Engineering, engenharia e auditoria LangSmith-first. Inclui `langsmith-prompt-engineer`, `langsmith-evals-engineer` e `langsmith-evals-auditor`, fixados em `sonnet`. |
| **`prompt-only-agent`** | Faz uma entrevista curta, uma pergunta por vez, e entrega um system prompt em Markdown de até **8.000 caracteres**, pronto para copiar e colar para um agente sem ferramentas. |

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
claude plugin install code-debug@claude-skills
claude plugin install grillme-gestor@claude-skills
claude plugin install grillme-langgraph@claude-skills
claude plugin install rag-kag-decision@claude-skills
claude plugin install modelos-custo-beneficio@claude-skills
claude plugin install facilitador-reunioes@claude-skills
claude plugin install langsmith-evals@claude-skills
claude plugin install prompt-only-agent@claude-skills
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
/backlog format        # reorganizar um repo: re-triar severidade + atribuir rank 1–100
/backlog consolidado repo=all # preview e gera ./consolidado_backlog.md por cluster e criticidade após confirmação
/backlog merge repo=all # propor merge de duplicatas por repo; pede confirmação antes de gravar
/backlog merge undo evt-20260619-0001 # reverter um merge somente se o estado ainda corresponder
/code-review-cadu 42   # review da PR #42 com veredicto GO/NO-GO + backlog
/code-debug <comando> # debug disciplinado por causa raiz
/grillme-langgraph     # design LangGraph — versão técnica
/grillme-gestor        # design LangGraph — versão para o gestor
/rag-kag-decision <caso de uso, fontes de dados, risco e exemplos de perguntas>
/modelos-custo-beneficio throughput_min=60 intelligence_min=35 input=text,image tool_calls=true structured_outputs=true
/facilitador-reunioes <tema, participantes, decisão esperada, contexto>
/langsmith-evals <sistema ou mudança a avaliar; prompt|engineer|audit>
/prompt-only-agent <ideia ou objetivo do agente prompt-only>
```

## Sobre as skills

### backlog

Opera a fonte da verdade GLOBAL de trabalho diferido (`~/.backlog/backlog.json`), com identidade `(repo, BL-NNNN)`, type/status/priority/rank e bootstrap seguro do store único. Operações mutáveis varrem o repo do CWD por backlog não estruturado (TODOs/FIXMEs soltos, `TODO.md`, listas de pendências) e migram apenas achados claros. Operações: `add`, `list`, `consolidado`, `format`, `promote`, `resolve`, `discard`, `merge`, `merge undo`, `init`.

`/backlog merge [repo=<nome>|repo=all]` propõe, por repo, clusters pequenos de duplicatas abertas e só grava após confirmação explícita daquele repo. Mantém um canônico existente, marca fontes como `mesclado`, não cria IDs e registra hashes, snapshots e evidência do subagente em `merge_history`; `/backlog merge undo <event_id>` reverte apenas quando o estado ainda é exatamente o esperado. A `format` reorganiza somente itens ativos — re-tria a **severidade** (4 níveis: crítica/alta/média/baixa) e atribui **rank** 1–100 único por repo; itens mesclados/terminais sempre têm rank nulo.

`/backlog consolidado [repo=<nome>|repo=all] [output=<caminho>]` lê um snapshot sem alterar a fonte, agrupa apenas itens `aberto` e `em-andamento` por objetivo de negócio e criticidade, gera `consolidado_backlog.md` com resumo de prioridade e omite faixas vazias. Cada atividade traz **Problema** e **O que será resolvido** em linguagem não técnica. O arquivo é derivado, exige confirmação antes de substituição e não se torna uma segunda fonte de verdade.

### code-review-cadu

Fork do plugin oficial `code-review` da Anthropic (Apache-2.0), mantendo o pipeline original (gate de elegibilidade → 5 agentes revisores paralelos → scoring de confiança 0-100 → filtro ≥80 → comentário na PR) e adicionando a triagem — o veredicto é sobre o **merge**: cada finding recebe **NO-GO** (merge bloqueado, corrigir nesta PR: correctness, segurança, perda de dados, regressão, contrato com infra real) ou **GO** (merge pode seguir: cleanup, refactor, débito, eficiência — diferível). O comentário na PR prefixa cada item com o veredicto; os GO são apresentados ao usuário e, **só após confirmação**, registrados em lote no backlog GLOBAL via `/backlog`, com o `BL-NNNN` citado em cada um.

### code-debug

Skill para investigar falhas sem chute: reproduz o comando ou cenário informado, coleta logs/evidências, adiciona instrumentação mínima quando necessário e só declara causa raiz quando há prova objetiva. A saída padrão é um relatório com Status, sintoma reproduzido, evidências, hipóteses eliminadas, causa comprovada ou inconclusiva e limitações; depois encerra sem correção. Mesmo quando o pedido original inclui correção, esta skill termina no diagnóstico; a implementação exige uma nova solicitação ou outro workflow.

### rag-kag-decision

Framework de decisão para arquitetura de conhecimento em LLMs: avalia se o caso pede RAG, KAG, GraphRAG ou híbrido. Usa sinais como base documental, entidades, relações, regras, temporalidade, risco do erro, velocidade de atualização e maturidade para manter grafo/ontologia. A saída recomendada inclui decisão, motivos, arquitetura mínima, riscos e gatilhos de migração.

### modelos-custo-beneficio

Consulta as APIs OpenRouter (`/models`, `/benchmarks` e `/endpoints`) para listar até cinco candidatos ao Model Engineering Eval. Exige índice Artificial Analysis estritamente maior que `35` (via OpenRouter Benchmarks, associação exata por `model_permaslug`), reasoning controlável, endpoint com throughput `p75 >= 60 t/s` (ou `p50` como fallback), capacidades solicitadas e modelo não gratuito. `tool_calls=true` emite `:exacto`; geração textual emite `:nitro`. A skill não executa Eval, não escolhe vencedor e não altera runtime.


### facilitador-reunioes

Skill para combater reuniões vagas: valida se a reunião é necessária, transforma o pedido em título objetivo, objetivo claro, pré-briefing para convite, pauta com timebox, guia de condução e fechamento obrigatório com ações, donos, prazos, critérios de pronto e comunicação.

### prompt-only-agent

Conduz uma entrevista curta, uma pergunta por vez, para delimitar objetivo, entradas, escopo, formato, limites e qualidade. A saída é somente um system prompt em Markdown, autocontido, de até **8.000 caracteres**, pronto para copiar e colar, sem assumir ferramentas ou acesso externo.

### langsmith-evals

Usa LangSmith como control plane para prompts, Datasets, Examples, Experiments, Traces e Feedback, mantendo pytest e oráculos determinísticos no repositório. O `langsmith-prompt-engineer` cria candidatos versionados e executa comparações pareadas; o `langsmith-evals-engineer` implementa e executa evals e backtests; o `langsmith-evals-auditor` revisa a evidência sem editar artefatos e emite `GO`, `NO-GO` ou `BLOCKED`. A separação evita self-certification. Os tres subagentes declaram `model: sonnet` no frontmatter.

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
