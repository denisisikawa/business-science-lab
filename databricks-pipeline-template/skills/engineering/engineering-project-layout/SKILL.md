---
name: engineering-project-layout
description: Organizar diretórios, módulos, notebooks, configuração, contratos e testes de projetos Databricks sem quebrar entradas existentes ou duplicar lógica.
---

# Estrutura de projeto

Trabalhe no Finance Evolution Lab, pipeline nativo sem dbt e com dados fictícios. No checkout, leia os padrões em `databricks-pipeline-template/docs/ENGINEERING_STANDARDS.md` e o código/contrato afetado. Priorize padrões existentes; os nomes Unity Catalog e diretórios futuros são blueprint, não objetos implantados. Se uma decisão técnica já estiver definida, aplique-a e registre-a sem perguntar de novo. Não invente regra financeira, acesso, calendário ou aprovação para avançar.

## Decisões incorporadas

- Preserve entradas em `notebooks/` e testes atuais na raiz. Para módulos novos com necessidade real de pacote, use `src/finance_pipeline/` e explicite import/deployment.
- Config sem segredo em `config/`; contratos em `contracts/`; definição de jobs em `resources/` quando implementada; decisões em `docs/`; verificadores em `scripts/`.
- Notebook é entrada fina, com parâmetros e chamada de função. Regra compartilhada deve ser testável sem ordem oculta de células.
- Não acrescente pastas vazias, README por diretório ou um framework só para parecer completo.
- Não misture fixture, dado gerado, ambiente virtual e código versionado. Preserve `.gitignore` e dados fictícios identificados.
- Movimentar normalizador exige atualizar import local, distribuição Spark (`addPyFile` quando usada), wrappers e testes. Não renomeie sem escopo.

## Exemplo e contraexemplo

Correto: criar função de transformação reutilizável e manter wrapper compatível. Incorreto: copiar a regra para notebook, src e skill com três implementações divergentes.

## Verificar

Liste entradas/imports/consumidores, teste imports e execução sem estado prévio e confira sincronização dos notebooks quando alterados. O verificador de plano confere apenas segurança e raiz dos caminhos declarados, não o funcionamento do pacote.

## Entrega padrão

Árvore com estado existente/proposto, responsabilidades e comandos reproduzíveis. Para migração, mapa de arquivos/entrypoints e teste de compatibilidade. Leia [os casos de layout](references/design-patterns.md).

## Exceção que exige decisão

Se já houver estrutura de deploy/import corporativa, integre ao padrão real; não imponha `src` sem verificar como os workers carregam o módulo.
