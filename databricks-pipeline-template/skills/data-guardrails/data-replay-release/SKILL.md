---
name: data-replay-release
description: Revisar idempotência, versões, falhas parciais e liberação de mudanças em pipelines financeiros nativos. Use para replay, backfill, correções históricas e publicação.
---

# Replay, histórico e entrega

Localize o checkout do Finance Evolution Lab e confira o README, o contrato em `databricks-pipeline-template/notebooks/pipeline_contract.py`, o adaptador adjacente e os testes na raiz. Não presuma que uma regra documentada já está implementada. Use dados fictícios; não introduza dbt neste pipeline nativo. A skill orienta o trabalho, não concede acesso nem aprovação de negócio.

## Aplicar

Leia [a matriz de falhas e recuperação](references/recovery-cases.md) para planejar retries, backfill e release. Identifique backend, entrada imutável, chave de lote, versão da regra e estado persistido.

- Preserve identidade de transação e ordenação determinística. Versão antiga não sobrescreve atual; payloads conflitantes na mesma versão não recebem vencedor arbitrário.
- No SQLite local, batch ID identifica conteúdo imutável; conteúdo diferente deve falhar. Em Delta, confirme identidade/versão de escrita suportadas e política real de retenção antes de confiar no retry.
- Não transfira garantia transacional do SQLite para múltiplas tabelas Delta. Snapshot consistente de JDBC é requisito externo; conexão não implica CDC.
- Backfill precisa de intervalo, dependências, versões e política para competência fechada. Não reescreva histórico publicado silenciosamente.
- Explique falhas parciais: quais saídas mudaram, quais devem aguardar e como retomar. Não prometa rollback global nem exactly-once ponta a ponta sem prova.
- Compare snapshot/overwrite, append e merge com retenção, rejeições e consumidores. Não apague evidência de investigação para fazer o próximo lote passar.
- Entrega por identidade autorizada; revisão independente para chave, moeda, alocação, histórico e acesso conforme a política. Duas skills não são dois revisores.

## Entregar

Cenários de retry, atraso, conflito e falha parcial; testes/ambiente/revisão; impacto histórico e recuperação verificável. Separe testes locais, transformação Spark, escrita Delta e workspace. Não execute deploy ou operações destrutivas fora da autorização existente.

## Caso de avaliação

Versão de 120,00 já persistida recebe versão antiga de 100,00: total atual deve permanecer 120,00. Repetir o lote não duplica fatos. Reutilizar batch ID com conteúdo alterado deve falhar no backend local.
