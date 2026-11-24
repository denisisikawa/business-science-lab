---
name: fpa-variance-drivers
description: Analisar variações de FP&A com convenção de sinais, denominadores, drivers e evidências. Use para realizado versus orçamento, pontes e comentários; não inventa causalidade ou valores ausentes.
---

# Variações, drivers e narrativa financeira

Para análise de negócio, use as definições e dados fornecidos; não exija o checkout inteiro. Se a tarefa envolver código, localize o Finance Evolution Lab e confira README, contrato, adaptador e testes afetados. Não presuma que uma regra documentada já está implementada. Use dados fictícios; não introduza dbt neste pipeline nativo. A skill orienta o trabalho, não concede acesso nem aprovação de negócio.

## Aplicar

Leia [fórmulas e exemplos](references/variance-cases.md) ao calcular variações ou escrever uma explicação. Estabeleça referência, realizado, moeda, período, versão e convenção de favorabilidade antes de interpretar.

- Calcule diferença absoluta como realizado − referência, salvo convenção explicitamente diferente. Sinal aritmético não é automaticamente bom/ruim.
- Percentual exige denominador e política: para base positiva, diferença/referência. Base zero torna esse percentual indefinido; base negativa pede convenção documentada, não leitura automática.
- Despesas e receitas têm interpretações diferentes; capex/opex, recorrência e efeitos de timing precisam de classificação aprovada, não inferida de nome.
- Ponte deve reconciliar exatamente com a variação total e explicar escopo, ordem e interação dos fatores. Não some explicações sobrepostas.
- Separe contribuição calculada de causa operacional. Uma categoria que aumentou é um componente da diferença, não prova de aumento de preço ou desperdício.
- Avalie volume, preço, mix, câmbio e calendário somente com dados compatíveis. Não invente taxas/quantidades nem decomponha o que a base não sustenta.
- Comentário deve citar período, comparação, valores, fonte e limitações; distinguir hipótese de causa verificada. Não converter variação em economia realizada.

## Entregar

Tabela com base, realizado, diferença, percentual quando definido e favorabilidade justificada; ponte reconciliada quando possível; comentário factual e perguntas de investigação. A skill de negócio especifica a interpretação; o guardrail técnico confere dados e cálculos.

## Caso de avaliação

Despesa 120 versus orçamento 100: +20 e +20%, normalmente desfavorável conforme política. Receita com os mesmos valores pode ser favorável. Orçamento zero não produz 0% nem infinito como explicação de negócio.

## Defaults, modelos e verificações incorporadas

- Para o exemplo do laboratório, diferença = realizado − referência; base positiva permite diferença/base. Preserve outra convenção explicitamente aprovada.
- Base zero/ausente não recebe percentual inventado. Não determine favorabilidade só pelo sinal sem saber se é custo, receita e contexto.
- Sem evidência de volume/preço, entregue contribuição por grupo e hipótese a investigar, sem ponte causal fabricada.
- Modelo: comparação identificada, cálculo, interpretação, evidência e ação de investigação.

Leia [o padrão de trabalho e os exemplos](references/working-patterns.md) para a saída esperada, contraprovas e critérios de aceite. Em implementação, consulte `databricks-pipeline-template/docs/ENGINEERING_STANDARDS.md` se disponível; padrões existentes prevalecem e ausência do checkout não autoriza inventar sua estrutura.
