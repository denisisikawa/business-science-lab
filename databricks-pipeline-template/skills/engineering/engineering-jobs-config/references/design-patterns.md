# Operação declarada versus comprovada

DAG mínimo: ingest_bronze → transform_silver → aggregate_gold. Uma futura tarefa de validação pode preceder a promoção da versão; isso exige desenho de visibilidade para não expor tabelas parcialmente atualizadas.

Retries: a declaração `idempotent=true` e uma referência preenchida no plano permitem uma validação estrutural, não provam o comportamento. Revise a evidência e teste falhas/reexecução no backend real.

Mudar só `environment` de dev para prod não aprova implantação. Valide catálogo/destinos, identidade, parâmetros, aprovações e recuperação. Não carregue config produtiva automaticamente na ausência da de desenvolvimento.

Em falha de rede, defina se a origem é snapshot estável e se a escrita chegou a concluir antes do retry. “Timeout” não prova ausência de efeito.
