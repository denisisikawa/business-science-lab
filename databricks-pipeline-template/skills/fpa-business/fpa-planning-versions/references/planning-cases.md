# Planejamento: perguntas que precedem a modelagem

1. A decisão compara realizado com orçamento original, orçamento revisado ou último forecast?
2. Qual revisão estava disponível na data da análise? O histórico deve ser reproduzível?
3. Qual é o calendário e quando um período é considerado fechado?
4. Há ajustes retroativos, estornos ou provisões? Como serão apresentados?
5. Qual moeda/unidade e qual nível de consolidação definem comparabilidade?

Exemplo fictício: janeiro realizado 90, orçamento aprovado 100 e forecast de janeiro 95 são três valores distintos. Variação contra orçamento é −10; contra forecast é −5. Nenhum substitui o outro sem mudar a pergunta.

Cenários são alternativas explícitas, não probabilidades automáticas. Não chame uma projeção de compromisso aprovado. Data de atualização técnica não substitui data de corte financeira.

O pipeline atual modela custos por mês; orçamento versionado, calendário fiscal e snapshots de fechamento são extensões que precisam de implementação e teste. Esta skill não os cria ao ser carregada.
