# Falhas que não podem virar garantias implícitas

| Evento | Resultado esperado a especificar/testar |
|---|---|
| Mesmo lote e conteúdo | Replay sem duplicação |
| Mesmo lote, conteúdo alterado | Rejeitar identidade imutável violada |
| Versão antiga chega depois | Preservar versão corrente |
| Mesma chave/versão, payload diferente | Conflito explícito, sem seleção aleatória |
| Bronze gravou, Silver falhou | Definir retomada e visibilidade de consumidores |
| Quarentena regravada | Preservar trilha e retenção necessárias |
| Correção em período fechado | Versão e aprovação de reabertura/ajuste |
| Mudança de regra | Identificar quais lotes/históricos devem ser recalculados |

Para cada teste, registre pré-estado, operação, pós-estado e efeito financeiro esperado. Modelo de recuperação deve ser demonstrado no runtime relevante. Time travel não é política de backup nem garantia de disponibilidade ilimitada de histórico.

O adaptador atual mantém quarentena/descartados em snapshots e não oferece publicação multi-tabela atômica. Isso deve continuar visível em documentação e handover até haver outra implementação validada.
