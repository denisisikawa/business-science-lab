---
name: finance-business-rules
description: Evoluir regras financeiras do Databricks Pipeline Template em PySpark e Python, com contrato explícito, reconciliação e testes de regressão. Use para mudanças de categorias, valores, competência e deduplicação.
---

# Evolução de regras financeiras

Localize o checkout e leia `databricks-pipeline-template/README.md`, `notebooks/pipeline_contract.py` e `notebooks/cost_pipeline_bronze_silver_gold.py` dentro desse projeto. Os testes estão em `tests/test_pipeline_contract.py` e `tests/test_pipeline_spark.py`, na raiz do repositório. Se os arquivos não estiverem acessíveis, solicite o checkout; não invente sua implementação. Esta skill contém instruções, não um runtime ou aprovação de negócio.

## Antes da mudança

Descreva a regra atual, a regra solicitada, granularidade, exemplos de entrada/saída e impacto histórico. Pergunte apenas pelas decisões materiais não especificadas: moeda/taxa, sinal, chave, conflito ou retroatividade. Não introduza dbt nem dados de empregadores neste laboratório sintético.

Preserve os invariantes, exceto quando a solicitação explicitamente os alterar:
- Chave: `source_system × transaction_id`; a mesma categoria/mês/fornecedor não identifica uma transação.
- Maior `updated_at` em UTC vence. Duplicata idêntica e versão antiga são destinos distintos; conteúdos conflitantes na mesma versão não têm vencedor arbitrário.
- BRL sem conversão implícita; centavos inteiros no backend local e Decimal(18,2) no Spark. Créditos negativos são válidos. Valores inválidos não viram zero; moeda não suportada não entra em somas BRL.
- Mês no primeiro dia, timestamp com fuso e destinos explícitos para todos os registros. Exclusões ainda não são modeladas.

## Implementação e evidência

Escreva um teste com resultado esperado calculado independentemente antes de ajustar a regra. Mantenha `normalize` como contrato compartilhado quando aplicável e verifique impacto nas janelas Spark, hash do payload, persistência e Gold. Uma categoria nova pode alterar validação e consumidores; mudança de chave/hash requer política de migração e replay, não apenas uma constante nova.

Cubra entrada válida, rejeitada, limite monetário, crédito, conflito, versão atrasada e reexecução conforme a mudança. Reconcilie quantidade e valores BRL conhecidos entre aceitos, rejeitados, duplicados e superseded; registre valores desconhecidos separadamente. Execute a suíte local e a paridade Spark quando o runtime estiver disponível. Não enfraqueça testes para acomodar resultado incorreto.

Apresente diff, regra antes/depois, testes executados, efeitos retroativos, plano de recuperação e limites. Não publique nova regra financeira como aprovada por negócio apenas porque testes passaram. Não execute escrita remota ou refresh fora do escopo autorizado.

## Exemplo de solicitação

“Aceitar a categoria NETWORK, preservando categorias atuais. Adicione casos para NETWORK, categoria inválida, replay e reconciliação. Explique se há necessidade de backfill.”

O resultado esperado é uma mudança no contrato e nos testes, não um filtro que descarte categorias desconhecidas silenciosamente.

## Especializações por domínio

Para mudanças de significado financeiro, selecione primeiro a especialização de FP&A apropriada (planejamento/versões, variações ou alocação). Passe sua regra e exemplos ao domínio de dados para contrato e validação. Não trate fórmula técnica como política financeira aprovada.

No checkout, consulte `databricks-pipeline-template/docs/SKILL_CATALOG.md` para selecionar apenas as referências necessárias. Se as especializações não estiverem disponíveis no assistente, use o catálogo como orientação e não alegue ter executado outra skill.

## Defaults, modelos e verificações incorporadas

- Reutilize contrato e nomenclatura existentes. Para regra nova, explicite objetivo, grão, versão e exemplos antes do código.
- No laboratório, a entrada monetária continua BRL e os créditos válidos são preservados; não pergunte novamente sobre esses defaults em uma alteração que não os afeta.
- Distinga inclusão de categoria de mudança de classificação histórica; a segunda precisa de versão/backfill e interpretação de negócio.
- Não escolha orçamento, driver, taxa ou calendário desconhecido só para evitar uma pergunta material.

Leia [o padrão de trabalho e os exemplos](references/working-patterns.md) para a saída esperada, contraprovas e critérios de aceite. Em implementação, consulte `databricks-pipeline-template/docs/ENGINEERING_STANDARDS.md` se disponível; padrões existentes prevalecem e ausência do checkout não autoriza inventar sua estrutura.
