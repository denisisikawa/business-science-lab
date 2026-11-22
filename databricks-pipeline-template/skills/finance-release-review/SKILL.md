---
name: finance-release-review
description: Revisar alterações do Databricks Pipeline Template antes de liberar uma versão, conferindo testes, contrato, reconciliação, linhagem e evidências. Use para revisão de PR e preparação de release.
---

# Revisão de entrega financeira

Leia o diff, `databricks-pipeline-template/README.md`, código alterado e testes afetados no checkout. Se a alteração envolver regra financeira, compare exemplos antes/depois e aprovação de negócio fornecida; não suponha aprovação ausente. Se envolver infraestrutura, confira ambiente e mecanismo de implantação reais.

Verifique proporcionalmente à mudança:
- Contrato, granularidade, chaves e tipos permanecem consistentes entre normalizador, Spark e persistência.
- Todos os registros têm destino e contagens/valores BRL conhecidos reconciliam. Valores desconhecidos não são escondidos em tolerância ou zero.
- Replay, versões atrasadas e conflitos continuam cobertos; mudanças incompatíveis têm migração/backfill e recuperação definidos.
- Metadados realmente existentes permitem localizar origem/lote; não declare linhagem ponta a ponta ou controles Unity Catalog que não foram configurados.
- Testes locais, Spark, Delta/JDBC e workspace são evidências diferentes. Confira comandos, ambiente, revisão e resultados; não use resultados antigos como execução da nova revisão.
- Alterações de contratos e operação estão documentadas. O README separa implementado, testado e proposto.

Execute verificações relevantes disponíveis. Produza achados com severidade, arquivo, impacto e ação concreta; declare também o que não foi verificado. Um checklist completo não autoriza deploy, refresh, alteração de acesso nem publicação de dados.

Exemplo: “Revise este diff de deduplicação. Verifique risco de regressão financeira, testes de replay e a diferença entre evidência local e execução Delta. Não execute jobs remotos.”
