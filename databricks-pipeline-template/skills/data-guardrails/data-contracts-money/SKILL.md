---
name: data-contracts-money
description: Definir ou revisar contratos de dados financeiros, chaves, tipos, precisão monetária e evolução de schema no pipeline nativo. Use antes de alterar colunas, moeda ou granularidade.
---

# Contratos e precisão monetária

Localize o checkout do Finance Evolution Lab e confira o README, o contrato em `databricks-pipeline-template/notebooks/pipeline_contract.py`, o adaptador adjacente e os testes na raiz. Não presuma que uma regra documentada já está implementada. Use dados fictícios; não introduza dbt neste pipeline nativo. A skill orienta o trabalho, não concede acesso nem aprovação de negócio.

## Aplicar

Leia [o contrato e os casos de fronteira](references/contract-cases.md) ao mudar schema, chave, sinais ou valores. Identifique produtor, consumidor, grão, colunas, tipos, nulabilidade, moeda/unidade, calendário e política de compatibilidade. Diferencie erro de parsing de exceção legítima de negócio.

- Preserve chave por origem × transação; fornecedor/mês não identifica uma despesa.
- Use decimal explícito e valide overflow/casas antes de persistir. Nulo, inválido e zero são estados distintos. Não arredonde silenciosamente uma entrada inválida.
- No contrato atual: apenas BRL; créditos negativos são válidos; centavos no backend local, Decimal(18,2) no Spark. Mudança dessas regras exige decisão explícita e testes.
- Não some moedas distintas. Não deduza moeda de símbolo/localidade. Conversão exige taxa, origem, data, direção e política de arredondamento.
- Defina vigência/versão do novo contrato, compatibilidade e efeito sobre hash, histórico, consumidores e replay. Campo desconhecido não autoriza schema evolution irrestrita.

## Entregar

Contrato antes/depois, exemplos independentes, decisões pendentes, classificação de compatibilidade, migração/backfill quando necessário e testes observáveis. Aponte exatamente qual código valida cada regra e quais ainda são propostas.

## Caso de avaliação

Entrada `1.001` no contrato de duas casas deve ser rejeitada, não virar `1.00`. Crédito `-10.25` deve permanecer válido. Uma nova moeda sem taxa não pode entrar em uma soma BRL.
