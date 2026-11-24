---
name: fpa-planning-versions
description: Formalizar regras de FP&A para realizado, orçamento, forecast, competência e versões de planejamento. Use antes de modelar comparações ou atualizar cenários; não valida infraestrutura.
---

# Planejamento, competência e versões

Para análise de negócio, use as definições e dados fornecidos; não exija o checkout inteiro. Se a tarefa envolver código, localize o Finance Evolution Lab e confira README, contrato, adaptador e testes afetados. Não presuma que uma regra documentada já está implementada. Use dados fictícios; não introduza dbt neste pipeline nativo. A skill orienta o trabalho, não concede acesso nem aprovação de negócio.

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

## Defaults, modelos e verificações incorporadas

- Use o calendário e versões já fornecidos; na demonstração atual month é civil mensal, não calendário fiscal de um empregador.
- Em visão anual, delimite meses realizados e projetados antes de somar; não sobreponha realizado e forecast.
- Se orçamento/forecast não existe nos dados, trate como escopo futuro ou ausência, nunca gere números como se fossem aprovados.
- Modelo da resposta: pergunta, cenários/versões, corte, grão, moeda, fórmula, exemplo e pendência material.

Leia [o padrão de trabalho e os exemplos](references/working-patterns.md) para a saída esperada, contraprovas e critérios de aceite. Em implementação, consulte `databricks-pipeline-template/docs/ENGINEERING_STANDARDS.md` se disponível; padrões existentes prevalecem e ausência do checkout não autoriza inventar sua estrutura.
