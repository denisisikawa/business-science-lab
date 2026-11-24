---
name: engineering-performance-cost
description: Avaliar performance e custo de pipelines Spark com medição comparável e preservação de resultados financeiros. Use para tuning; não promete ganho por heurística.
---

# Performance e custo com evidência

Trabalhe no Finance Evolution Lab, pipeline nativo sem dbt e com dados fictícios. No checkout, leia os padrões em `databricks-pipeline-template/docs/ENGINEERING_STANDARDS.md` e o código/contrato afetado. Priorize padrões existentes; os nomes Unity Catalog e diretórios futuros são blueprint, não objetos implantados. Se uma decisão técnica já estiver definida, aplique-a e registre-a sem perguntar de novo. Não invente regra financeira, acesso, calendário ou aprovação para avançar.

## Decisões incorporadas

- Comece pelo plano, volume, seletividade, cardinalidade e ações executadas. Registre runtime/compute, duração, shuffle/spill, dados lidos e custo quando disponível.
- Projete colunas e aplique filtros equivalentes cedo. Evite `collect`/`toPandas` sem limite e a repetição de ações que recalculam o mesmo plano.
- Cache só com reuso e memória justificados; libere quando não necessário. Broadcast exige tamanho e estatísticas adequados, não intuição.
- Não particione por chave de alta cardinalidade nem force `repartition(1)` como default. Verifique tamanho de arquivos e padrão de leitura antes de mudar layout.
- Aumentar compute não corrige fan-out, skew ou leitura desnecessária. Regras de runtime/serverless/clustering dependem de versão e workload.
- Otimização não pode mudar rejeições, chave, precisão ou versão vencedora. Preserve contrato e compare resultados antes/depois.

## Exemplo e contraexemplo

Correto: medir duas execuções comparáveis e reconciliar outputs, registrando efeito de cache/aquecimento. Incorreto: prometer 50% de economia porque trocou UDF ou escolheu cluster maior.

## Verificar

Leia [o plano de medição](references/design-patterns.md). Sem runtime, forneça diagnóstico estático e experimento, não benchmark. Não gere gasto remoto para medir sem escopo autorizado.

## Entrega padrão

Hipótese, baseline, mudança isolada, cenário comparável, resultado funcional, métricas e conclusão limitada ao cenário. Se custo não foi medido, não converta tempo em economia monetária presumida.

## Exceção que exige decisão

Feature não disponível, custo pago, mudança de storage/retensão ou perda de rastreabilidade exigem avaliação específica antes de execução.
