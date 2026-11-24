# Modelo de replay e recuperação

| Passo | Estado a registrar |
|---|---|
| Antes | Revisão, lote, fonte/snapshot, versão e destinos |
| Operação | Retry, correção ou backfill com intervalo explícito |
| Esperado | Chaves, versão vencedora, contagem e total |
| Depois | Resultado observado e efeitos parciais |
| Consumo | O que pode ser publicado e o que deve aguardar |

**Bom:** reapresentar o mesmo lote imutável sem duplicar fatos. **Ruim:** criar outro batch ID em todo retry e chamar isso de idempotência.

Reabrir competência fechada exige política de negócio, não só uma cláusula MERGE. Quarentena sobrescrita precisa de retenção compatível com auditoria. Uma tabela atualizada e outra falha não se recuperam por promessa de rollback global.

Avalie lote novo, replay, conteúdo alterado com mesmo ID, versão antiga, conflito e falha após primeira escrita. SQLite e Delta exigem evidências próprias. Referência preenchida no plano não comprova execução do teste.
