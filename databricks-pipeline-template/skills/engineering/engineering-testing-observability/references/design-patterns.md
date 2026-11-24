# Evidências e erros que o happy path não encontra

| Caso | Assert material |
|---|---|
| Dois fatos iguais em mês/fornecedor mas IDs distintos | Ambos permanecem |
| Mesma versão com payload distinto | Conflito, sem vencedor arbitrário |
| Crédito válido | Preservado com sinal |
| Replay do lote | Sem duplicação e com identidade imutável |
| Erros compensatórios | Comparação por grão falha mesmo com total igual |
| Falha após primeira escrita | Recuperação/visibilidade demonstrada, sem rollback fictício |

Métrica de rejeitados deve distinguir quantidade, valor conhecido e quantia desconhecida. Não calcule taxa de qualidade sem definir população e denominador.

Um teste de logging deve verificar ausência de segredo e presença de identificadores necessários, não o texto exato de uma frase. Performance exige métricas reais, não timer de um mock.

Guarde somente evidência permitida pela política de retenção. Logs também são dados que precisam de controle de acesso.
