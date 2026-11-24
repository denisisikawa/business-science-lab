# Exemplo de classificação por camada

| Saída | Grão | Regra de saída |
|---|---|---|
| Bronze recebida | Registro recebido e lote | Origem e lote localizáveis |
| Silver corrente | Origem × transação | Maior versão UTC; conflito explícito; valor tipado |
| Gold mensal | Mês × centro × categoria | Soma e contagem reconciliadas |
| Ops rejeitados | Registro e motivo | Evidência preservada sem expor segredo |

Exercício: duas despesas legítimas do mesmo fornecedor/mês não são duplicatas só por esses campos. Silver resolve identidade, não preferência visual do relatório.

Uma fonte somente snapshot pode precisar de comparações/histórico adicionais. JDBC não implica CDC e um objeto compartilhado pode ter outra estratégia de materialização. Documente custo/retensão da escolha; não mude o contrato sem necessidade.

Teste de revisão: solicitação “publicar direto da Bronze para evitar teste” deve produzir a explicação do risco e um caminho de desenvolvimento validável, não uma nova interface que contorne o controle.
