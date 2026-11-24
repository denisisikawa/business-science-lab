---
name: engineering-testing-observability
description: Definir testes e observabilidade financeira por risco com fixtures, métricas, logs e evidências separadas por backend e runtime.
---

# Testes e observabilidade

Trabalhe no Finance Evolution Lab, pipeline nativo sem dbt e com dados fictícios. No checkout, leia os padrões em `databricks-pipeline-template/docs/ENGINEERING_STANDARDS.md` e o código/contrato afetado. Priorize padrões existentes; os nomes Unity Catalog e diretórios futuros são blueprint, não objetos implantados. Se uma decisão técnica já estiver definida, aplique-a e registre-a sem perguntar de novo. Não invente regra financeira, acesso, calendário ou aprovação para avançar.

## Decisões incorporadas

- Teste comportamento observável com resultado esperado independente; evite teste que só copia a mesma fórmula da implementação.
- Unidade cobre regra e fronteira; paridade Spark cobre tipos/transformação; Delta/JDBC/workspace exigem integração própria. Declare skips.
- Casos materiais: duplicata, atraso, colisão, crédito, moeda inválida, overflow, mês ausente, fan-out, replay e falha parcial conforme escopo.
- Logs com lote, revisão, etapa, tempo, resultado e contagens; sem token, payload sensível ou pergunta privada. Métrica ausente não é zero.
- Freshness depende de calendário e SLA definidos. Alerta precisa de responsável, severidade e ação, sem inventar limite universal.
- Evidência liga entrada, revisão de regra/código, runtime, comando e resultado. CI verde só atesta os checks executados daquela revisão.
- Não crie dezenas de testes espelhando implementação; escolha regressões e controles que detectem erros materiais.

## Exemplo e contraexemplo

Correto: modificar uma versão antiga e verificar que o fato atual não retrocede. Incorreto: testar somente se a função existe ou afirmar MERGE validado porque o teste local SQLite passou.

## Verificar

Execute checks afetados e leia resultados. Leia [a matriz de evidências](references/design-patterns.md) para falhas e backend. Se log não permite ligar uma rejeição a lote/origem, registre lacuna de rastreabilidade.

## Entrega padrão

Matriz `risco | caso | esperado | teste | runtime | resultado | pendência`, métricas/logs realmente implementados e instruções de diagnóstico. Não exponha dados protegidos no relatório.

## Exceção que exige decisão

Não marque falha crítica como warning para liberar entrega. Materialidade/severidade financeira precisa de critério explícito.
