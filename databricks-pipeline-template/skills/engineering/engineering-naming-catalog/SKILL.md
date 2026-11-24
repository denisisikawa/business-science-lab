---
name: engineering-naming-catalog
description: Aplicar convenções locais de catálogos, schemas, tabelas, views, colunas e jobs do Finance Evolution Lab, respeitando padrões existentes e compatibilidade.
---

# Nomenclatura e objetos

Trabalhe no Finance Evolution Lab, pipeline nativo sem dbt e com dados fictícios. No checkout, leia os padrões em `databricks-pipeline-template/docs/ENGINEERING_STANDARDS.md` e o código/contrato afetado. Priorize padrões existentes; os nomes Unity Catalog e diretórios futuros são blueprint, não objetos implantados. Se uma decisão técnica já estiver definida, aplique-a e registre-a sem perguntar de novo. Não invente regra financeira, acesso, calendário ou aprovação para avançar.

## Decisões incorporadas

- Objetos novos: `finance_lab_<env>.<layer>.<object>`; env dev/test/prod, layers bronze/silver/gold/ops. Inglês e snake_case.
- Exemplos: `bronze.cost_transactions_raw`, `silver.cost_transactions`, `gold.cost_monthly`, `ops.cost_transactions_rejected`.
- Views novas: `vw_<purpose>`; job `finance_cost_pipeline_dev`; tarefas `ingest_bronze`, `transform_silver`, `aggregate_gold`.
- Colunas novas: `_id` identifica chave, `_at` instante, `_date` data e `_count` contagem quando apropriado; mantenha `month`, `amount` e os nomes do contrato vigente.
- Não use `final2`, nomes de pessoas, segredo, workspace real ou ambiente produtivo como default.
- Nome plenamente qualificado evita ambiguidade de catálogo, mas não concede privilégio. Nomes de tabela e paths físicos não são intercambiáveis.

## Exemplo e contraexemplo

Correto: propor `finance_lab_dev.gold.cost_monthly` com grão definido. Incorreto: criar `prod.default.CustoFinal2` ou renomear tabelas existentes sem verificar consumidores.

## Verificar

Para o blueprint do laboratório, execute o verificador de plano descrito nos padrões. Compare colisões, consumidores e política real. Funções/volumes/modelos fora do escopo do helper exigem avaliação específica; não marque como validados pelo teste de tabelas/views.

## Entrega padrão

Mapa `objeto atual | proposto | tipo | grão | consumidor | compatibilidade | migração`. Leia [os casos de nomes](references/design-patterns.md) para compatibilidade e parametrização.

## Exceção que exige decisão

Outro padrão corporativo já adotado prevalece no seu ambiente. Registre a diferença em vez de impor o blueprint deste laboratório.
