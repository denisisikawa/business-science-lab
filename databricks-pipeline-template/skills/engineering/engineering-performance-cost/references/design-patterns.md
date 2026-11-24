# Plano mínimo de experimento

1. Fixe entrada/revisão, runtime e compute; registre intervalo e volume.
2. Registre plano físico e métricas relevantes; identifique reuso/cache.
3. Mude um fator material e execute cenário comparável quando autorizado.
4. Compare contagem, chaves, disposições e valores exatos, não apenas duração.
5. Documente variabilidade e limites de extrapolação. Sem repetição suficiente, não anuncie resultado estável.

Exemplo: várias ações `count()` e somas sobre a mesma transformação podem recalcular trabalho. Agregar métricas pode ajudar, mas preservar diagnóstico de rejeitados e limites de custo/latência continua necessário.

Tamanho do cluster, broadcast, particionamento e cache são escolhas condicionais. Estatística desatualizada e distribuição enviesada podem invalidar uma heurística. Não desabilite controles financeiros como estratégia de tuning.
