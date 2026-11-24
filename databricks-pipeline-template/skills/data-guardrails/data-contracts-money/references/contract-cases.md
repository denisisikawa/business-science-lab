# Decisões e fronteiras do contrato

| Tema | Exigir antes da implementação | Contraprova |
|---|---|---|
| Grão | Evento representado e chave estável | Duas despesas legítimas no mesmo fornecedor/mês |
| Datas | Competência, lançamento, alteração e ingestão separados | Timestamp sem fuso e período fora do calendário |
| Valor | Precisão, escala, sinal, unidade e moeda | NaN, infinito, overflow, terceira casa decimal |
| Null | Se significa ausência, desconhecido ou não aplicável | Ausência convertida indevidamente em zero |
| Evolução | Versão, consumidores e migração | Replay antigo interpretado com regra nova sem versão |

Exemplo BRL: duas transações de 100,00 e um crédito de −10,25 totalizam 189,75. Não deduplique as transações por terem valor/mês iguais. Um registro USD 20,00 sem taxa permanece fora do total BRL; preserve valor e moeda originais e a razão de rejeição.

O contrato atual exige mês no primeiro dia e timestamp de alteração com fuso, normalizado em UTC. Não confunda mês de competência com data de ingestão. Exclusões não estão implementadas.

Antes de aumentar precisão ou adicionar moeda, verifique tipos em todas as camadas e consumidores; mudar apenas o normalizador não resolve a persistência. Alteração de chave/hash pode mudar identidade e versões de registros existentes.
