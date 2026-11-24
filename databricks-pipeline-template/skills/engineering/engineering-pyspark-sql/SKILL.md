---
name: engineering-pyspark-sql
description: Implementar transformações PySpark/SQL tipadas, determinísticas e testáveis com cardinalidade de joins, regras explícitas e paridade do contrato financeiro.
---

# Transformações PySpark e SQL

Trabalhe no Finance Evolution Lab, pipeline nativo sem dbt e com dados fictícios. No checkout, leia os padrões em `databricks-pipeline-template/docs/ENGINEERING_STANDARDS.md` e o código/contrato afetado. Priorize padrões existentes; os nomes Unity Catalog e diretórios futuros são blueprint, não objetos implantados. Se uma decisão técnica já estiver definida, aplique-a e registre-a sem perguntar de novo. Não invente regra financeira, acesso, calendário ou aprovação para avançar.

## Decisões incorporadas

- Projete colunas, use schema/tipos explícitos, valide casts e preserve campos necessários de origem. Não transforme erro em null/zero silencioso.
- Decimal(18,2) para valores do contrato, UTC para instante e primeiro dia para month. Não use float para ledger ou soma de moeda.
- Antes de join, defina 1:1/1:N/N:1 e teste duplicatas da dimensão. Fan-out pode inflar custo mesmo com SQL válido.
- Resolva empates e conflitos antes de merge; `dropDuplicates` sem ordenação/política não seleciona a versão de negócio.
- Prefira funções Spark nativas quando demonstrada equivalência. O UDF atual compartilha normalizador; otimização só com paridade para valores inválidos, créditos, fusos e conflito.
- Não espalhe I/O e regra por funções com efeitos ocultos. SQL gerado deve ter fonte/escopo explícitos e identificação de nomes aprovada.

## Exemplo e contraexemplo

Correto: dimensão única por chave antes do join N:1, conferindo valores antes/depois. Incorreto: join em fornecedor não único que replica as despesas e depois soma.

## Verificar

Casos pequenos com valores esperados, nulos, chaves ausentes, fan-out e empate. Execute testes existentes de contrato/paridade quando o runtime permitir; um teste SQLite não valida comportamento Spark/Delta.

## Entrega padrão

Função/SQL, contrato de entrada/saída, cardinalidade de joins e evidência de reconciliação. Leia [os casos de transformação](references/design-patterns.md) antes de mudar join, cast ou deduplicação.

## Exceção que exige decisão

Mudar tratamento de ausência/negativo/categoria é regra financeira; não escolha `fillna(0)` ou filtro apenas para eliminar falha.
