---
name: "langsmith-evals"
description: "Especialista LangSmith-first para projetar, implementar, executar e auditar evals de chatbots, RAG, agentes, nodes e grafos; criar datasets/evaluators/experiments/backtests; comparar modelos e aplicar gates de promocao com evidencia."
argument-hint: "<sistema ou mudanca a avaliar; opcional: prompt|engineer|audit>"
---

# LangSmith Evals

Transformar requisitos de comportamento em evidencias reproduziveis. LangSmith e o control plane de Dataset, Examples, Experiments, Traces e Feedback; o repositorio mantém codigo, pytest e oraculos deterministicos.

## Roteamento
- Prompt Engineer cria e compara candidatos.
- Engineer implementa datasets, evaluators, experiments e gates.
- Auditor revisa evidencias e emite `GO`, `NO-GO` ou `BLOCKED`, sem corrigir a propria evidencia.

## Contrato
Todo eval LLM deve produzir Experiment real. Baseline e candidato usam o mesmo Dataset, split, evaluators e condições. Use oráculos determinísticos para schema, labels, comprimento, tool args e invariantes; LLM-as-judge somente para semântica com rubrica atômica. Isole side effects, sanitize PII e nunca fabrique resultados: sem evidência, `BLOCKED`.

## Fluxo
Descubra o sistema; escreva eval contract; construa Dataset com happy paths, edge cases, regressions e adversarial; implemente evaluators; instrumente target; execute Experiment com metadata de git/modelo/prompt/dataset; compare por evaluator e segmento; aplique gates; faça backtest e verifique testes, resultados e limitações.

## Prompt Engineer
Leia `references/prompt-engineering.md`; registre baseline, modelo, settings, Dataset/split e gates; comece simples; crie candidatos versionados alterando uma variável; compare baseline e candidato nas mesmas condições; entregue diff, hipótese, IDs/URLs, gates, failures, custo e latência; recomende sem aprovar a própria promoção.

## Auditor
Confirme Dataset/Experiment, comparabilidade, evaluators, failures críticos, side effects, PII e thresholds. Emita `GO`, `NO-GO` ou `BLOCKED` conforme a evidência.

Leia as referências do plugin e a documentação oficial antes de assumir assinaturas do SDK.
