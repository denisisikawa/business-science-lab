# Aplicação prática do contrato

## Modelo de especificação

| Campo | Tipo | Nulo? | Unidade/moeda | Regra | Erro/rejeição | Compatibilidade |
|---|---|---|---|---|---|---|
| amount | Decimal(18,2) no Spark | Não | BRL | Até 16 dígitos inteiros e 2 decimais | invalid_amount | Versão do contrato |
| updated_at | timestamp UTC | Não | instante | Entrada com fuso | invalid_updated_at | Versão/ordenação |

A tabela é exemplo do contrato atual, não DDL já implantado. No backend local amount persistido é centavos inteiros; não confunda representações.

**Bom:** `-10.25` conserva crédito; `1.001` vai para rejeição. **Ruim:** cast/round transforma ambos em despesa positiva válida.

## Verificar por mudança

Schema: coluna ausente, extra, incompatível e nullable. Precisão: mínimo/máximo, overflow, zero, crédito e valor inválido. Chave: fatos legítimos semelhantes e colisão. Data: fuso equivalente, mês inválido e atualização antiga.

Pergunte apenas por alteração material de moeda, escala, chave ou significado não resolvida no contrato. O verificador de plano valida declarações de tipo; teste os dados reais/fictícios no transformador também.
