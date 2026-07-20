# Prompt Engineering Foundations

Transforme uma mudança de prompt em experimento reproduzível. Separe **instrução**, **contexto**, **dados de entrada** e **indicador de saída**; comece pelo menor prompt e adicione componentes somente por failure observado.

## Regras
1. Uma tarefa por prompt.
2. Use comandos diretos e separadores claros.
3. Troque limites vagos por critérios mensuráveis.
4. Declare labels, audiência, idioma, estilo, comprimento e formato.
5. Preserve baseline e altere um elemento significativo por candidato.
6. Mantenha o prompt curto.

Comece zero-shot; adicione few-shot apenas quando o formato ou comportamento exigir. Altere `temperature` **ou** `top_p`, nunca ambos, e registre modelo, versão e settings.

## Contrato
```text
Prompt ID/version:
Hipotese da mudanca:
Elemento alterado:
Modelo/provider/version:
Dataset/split/version:
Baseline Experiment:
Candidate Experiment:
Gates de formato e semantica:
Custo/latencia budget:
```

Compare nas mesmas condições e use evaluator determinístico para schema, labels, comprimento, regex e tool args; reserve LLM-as-judge para semântica calibrada. O Prompt Engineer entrega evidências e recomendações, mas a promoção exige o Auditor.
