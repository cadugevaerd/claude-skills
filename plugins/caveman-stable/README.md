# caveman-stable

Plugin para Claude Code com um único Output Style estável, técnico e conciso. O estilo é sempre aplicado enquanto o plugin estiver habilitado; não há variantes ou modos alternativos.

## Instalação

```bash
claude plugin marketplace add cadugevaerd/claude-skills
claude plugin install caveman-stable@claude-skills
```

Dentro do Claude Code:

```text
/plugin marketplace add cadugevaerd/claude-skills
/plugin install caveman-stable@claude-skills
```

Após instalar, habilitar, desabilitar, atualizar ou desinstalar o plugin, execute `/reload-plugins`. Como o Output Style altera o system prompt, use depois `/clear` ou inicie uma nova sessão. O Output Style afeta a conversa principal; subagents comuns usam system prompt próprio. Apenas forks que herdam o system prompt completo recebem o estilo.

## Comportamento

Mantém o idioma dominante; remove filler, pleasantries, hedging desnecessário, repetição e narração rotineira, preservando qualificadores reais de incerteza, probabilidade e limitação; prefere frases técnicas curtas; preserva exatamente código, comandos, paths, URLs, identificadores, APIs e erros. Usa prosa explícita para segurança, ações destrutivas, ambiguidade e passos ordenados. Altera somente a forma do output, nunca escopo, ferramentas, permissões ou verificação. Não anuncia o modo e resiste a context growth/compaction.

Um plugin com outro `force-for-plugin: true` pode conflitar. Mantenha somente um forced Output Style quando houver conflito.

## Rollback

```bash
claude plugin disable caveman-stable@claude-skills
claude plugin uninstall caveman-stable@claude-skills
```

Depois execute `/reload-plugins` e então `/clear`, ou inicie uma nova sessão.

## Atribuição

Conceito derivado de [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman), sob MIT. Esta implementação é independente e não copia texto substancial do upstream. Veja `UPSTREAM.md`.
