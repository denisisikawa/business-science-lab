# Implementar regra sem redescobrir o projeto

## Modelo de entrega

| Campo | Conteúdo |
|---|---|
| Necessidade | Pergunta financeira e usuário da decisão |
| Regra antes/depois | Fórmula/domínio, grão, sinais e versão |
| Default reaproveitado | Contrato/configuração já encontrado |
| Exemplo e contraprova | Valores esperados calculados independentemente |
| Implementação | Arquivos e efeitos no hash/consumidores |
| Histórico | Preservar versão ou recalcular intervalo definido |
| Evidência | Comando, runtime, resultado e limite |

**Bom:** NETWORK passa a ser categoria válida a partir de uma regra explicitada; casos antigos e inválidos continuam testados. **Ruim:** mapear toda categoria desconhecida para NETWORK para reduzir rejeitados.

## Verificações

Confira normalizador, Spark, persistência, documentação e consumidores afetados; rode testes de regressão relevantes. Uma regra escrita na skill ainda não é implementada. Não transforme alteração de categoria em autorização para publicar ou sobrescrever histórico.

Pergunte somente por uma diferença material não resolvida no contrato: retroatividade, moeda, classificação e aprovação de regra. Reuse decisões técnicas já aprovadas e registre-as no resumo.
