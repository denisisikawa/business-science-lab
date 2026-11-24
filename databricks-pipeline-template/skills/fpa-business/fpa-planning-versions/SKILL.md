---
name: fpa-planning-versions
description: Formalizar regras de FP&A para realizado, orçamento, forecast, competência e versões de planejamento. Use antes de modelar comparações ou atualizar cenários; não valida infraestrutura.
---

# Planejamento, competência e versões

Localize o checkout do Finance Evolution Lab e confira o README, o contrato em `databricks-pipeline-template/notebooks/pipeline_contract.py`, o adaptador adjacente e os testes na raiz. Não presuma que uma regra documentada já está implementada. Use dados fictícios; não introduza dbt neste pipeline nativo. A skill orienta o trabalho, não concede acesso nem aprovação de negócio.

## Aplicar

Leia [as decisões de planejamento](references/planning-cases.md) quando houver comparação, fechamento ou forecast. Não trate exemplos como política contábil universal; obtenha as definições adotadas para o caso.

- Defina objetivo decisório, entidade, conta/centro, grão temporal, moeda e escopo de consolidação.
- Diferencie realizado, orçamento aprovado, forecast e cenário. Nomeie versão e data de corte; não substitua orçamento por último forecast sem indicar.
- Separe competência, lançamento, pagamento e ingestão. Calendário fiscal pode não coincidir com calendário civil.
- Para período misto, explicite quais meses são realizado fechado e quais são projeção. Dados futuros não podem aparecer no treino/backtest como informação já conhecida.
- Determine tratamento de créditos, estornos, provisões e ajustes após fechamento conforme política do caso; não determine lançamento contábil real por inferência.
- Ausência de orçamento é diferente de orçamento zero. Não complete lacunas com zero ou forward-fill sem uma regra explícita.
- Defina taxas/unidades e comparabilidade antes de somar filiais/moedas. Diga se análise é nominal, moeda constante, recorrente ou total.

## Entregar

Ficha de regra com pergunta de negócio, cenários/versões, período/corte, grão, moeda, sinal, exceções, exemplo e contraprova. Identifique decisões não fornecidas; encaminhe o contrato para implementação técnica, sem afirmar que estas funcionalidades já existem no pipeline.

## Caso de avaliação

Realizado janeiro–março e forecast abril–dezembro compõem uma visão anual com corte março. Somar realizado anual a forecast anual sem delimitação duplica meses. Explique a escolha antes de escrever SQL.
