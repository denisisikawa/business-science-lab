# Metodologia de custeio gerencial · Contestação de cartões

## Decisão que o modelo apoia

Medir quanto custa tratar uma contestação por tipo de caso e canal, quanto da capacidade é consumida e o que explica a variação mensal de custo. O primeiro recorte usa dados sintéticos para uma operação de Cartões. A visão gerencial concilia com o centro de custo e permite avaliar custo unitário, capacidade e premissas do orçamento.

A curva ABC do laboratório ordena o gasto por categoria. O TDABC atribui o custo da equipe às atividades pelo tempo consumido. A concentração de gasto pode orientar quais grupos de recursos modelar primeiro.

## Regras de apropriação

| Grupo de custo | Regra | Fonte ou evidência |
| --- | --- | --- |
| Despesa dedicada a um produto, canal ou caso | Apropriar diretamente ao destino identificável | Lançamento contábil, centro de custo, contrato ou identificador do caso |
| Equipe de operações compartilhada | Atribuir o custo pelo tempo ativo de trabalho por tipo de atividade | Folha e encargos, jornada prática e registro operacional |
| Tecnologia compartilhada | Atribuir primeiro o consumo identificável. Distribuir o gasto compartilhado restante com uma unidade medida, como processamento, armazenamento ou assentos atribuídos | Fatura, tags, inventário e medição de uso |
| Despesa corporativa comum | Exibir no centro corporativo. Se houver uma visão de custo completo, explicitar a regra gerencial e o valor adicional | Plano de contas e critério aprovado |

Cada parcela do lançamento entra em uma única regra. Um contrato totalmente apropriado a Cartões fica fora dos grupos de recursos compartilhados. Custos já cobrados por consumo também ficam fora da taxa horária da operação. Estornos ao cliente, perdas de fraude e efeitos de funding ficam fora do piloto de custo operacional. Esta é uma visão gerencial conciliada com o razão.

## TDABC · Custo e capacidade prática

Use grupos de recursos com custo e produtividade comparáveis. Se analistas de primeiro e segundo nível tiverem estruturas de custo diferentes, calcule uma taxa para cada grupo.

- **Custo do grupo** é a despesa do período para fornecer aquela capacidade. O piloto inclui salários e encargos do pessoal dedicado.
- **Capacidade prática** é o tempo utilizável no mês. Começa com a escala de trabalho e desconta férias, faltas, pausas e tempo indisponível para a operação. Atividades internas relevantes podem ter um destino próprio no modelo se forem medidas. O mesmo tempo entra uma vez.
- **Taxa de capacidade** = custo do grupo ÷ minutos de capacidade prática. A taxa usa capacidade disponibilizada, independentemente da quantidade de trabalho recebida.
- **Minutos consumidos** = volume por tipo × tempo ativo por caso. Uma equação de tempo pode usar uma base de triagem e adicionar minutos quando houver análise documental ou revisão manual. Cada etapa entra uma vez por grupo que trabalhou nela.
- **Custo atribuído** = minutos consumidos × taxa de capacidade. **Saldo de capacidade** = custo do grupo − custo atribuído. Quando positivo e a medição estiver completa, o saldo representa a capacidade fornecida e não utilizada naquele mês.

Calibre os tempos com registros operacionais ou amostras representativas por tipo e etapa. Registre a fonte, a janela, o tamanho da amostra e a versão do parâmetro. Tempo de espera entre etapas alimenta análise de SLA. Para custeio de equipe, use tempo efetivo de trabalho. Para um caso que atravessa meses, atribua o trabalho ao mês de execução de cada etapa. Custos e eventos do mês precisam usar o mesmo recorte.

Se os minutos consumidos excederem a capacidade prática, sinalize sobrecarga e investigue eventos duplicados, tempos estimados e horas extras. Quando houver horas extras comprovadas, inclua o custo e a capacidade correspondentes. Com dados insuficientes, identifique o saldo como pendente de validação e mantenha a conciliação aritmética. Use precisão decimal e explicite qualquer ajuste de centavos.

## Exemplo com orçamento e realizado

As duas classes são definidas no início do período. Neste exemplo, todos os itens são concluídos no mesmo mês e consomem uma única equipe.

| Medida | Orçamento | Realizado |
| --- | ---: | ---: |
| Custo da equipe | R$ 120.000 | R$ 132.000 |
| Capacidade prática | 12.000 min | 12.000 min |
| Taxa de capacidade | R$ 10/min | R$ 11/min |
| Simples · volume e minutos por caso | 2.000 × 2,0 | 2.100 × 2,0 |
| Complexa · volume e minutos por caso | 1.000 × 5,0 | 1.200 × 5,5 |
| Minutos consumidos | 9.000 | 10.800 |
| Uso da capacidade prática | 75% | 90% |
| Custo atribuído a casos simples | R$ 40.000 | R$ 46.200 |
| Custo atribuído a casos complexos | R$ 50.000 | R$ 72.600 |
| Custo total atribuído a casos | R$ 90.000 | R$ 118.800 |
| Capacidade ociosa | R$ 30.000 | R$ 13.200 |
| Custo médio atribuído por caso | R$ 30,00 | R$ 36,00 |

O realizado atribui **R$ 22 por caso simples** e **R$ 60,50 por caso complexo**. O custo médio de R$ 36,00 usa apenas o custo atribuído dividido pelos 3.300 casos. Para obter o custo total do centro, o relatório recompõe R$ 118.800 de custo atribuído e R$ 13.200 de capacidade ociosa.

## Ponte de variação reconciliada

A ordem adotada é volume → mix → tempo → taxa. Cada etapa troca uma premissa planejada pela realizada e mantém as demais da etapa anterior. A ordem deve ficar fixa entre fechamentos porque pode mudar quanto da interação aparece em cada efeito.

| Etapa | Premissa atualizada | Custo atribuído | Efeito da etapa |
| --- | --- | ---: | ---: |
| Orçamento | 3.000 casos, mix, tempos e taxa planejados | R$ 90.000 | — |
| Volume | 3.300 casos com o mix planejado | R$ 99.000 | +R$ 9.000 |
| Mix | 2.100 simples e 1.200 complexos | R$ 102.000 | +R$ 3.000 |
| Tempo | Casos complexos passam de 5,0 para 5,5 min | R$ 108.000 | +R$ 6.000 |
| Taxa | Custo por minuto passa de R$ 10 para R$ 11 | R$ 118.800 | +R$ 10.800 |
| **Variação do custo atribuído** | | | **+R$ 28.800** |
| Variação do custo da capacidade ociosa | R$ 13.200 − R$ 30.000 | | **−R$ 16.800** |
| **Variação do custo total da equipe** | R$ 132.000 − R$ 120.000 | | **+R$ 12.000** |

O efeito de taxa mede a mudança no custo por minuto. Em um caso com mudança de escala, essa taxa também pode variar pela capacidade prática no denominador. Para abertura de um tipo sem orçamento, use um tempo-padrão aprovado ou destaque a nova atividade em um efeito próprio, mantendo a ponte conciliada. Se o volume orçado for zero, a divisão entre volume e mix fica indefinida até existir uma base de referência.

## Comentário automático e evidência

O motor de cálculo produz os efeitos e as referências aos dados de origem. A IA organiza a leitura, usa os valores já calculados e indica a evidência necessária para validar uma hipótese operacional.

> O custo total da equipe ficou R$ 12 mil acima do orçamento. O custo atribuído aos casos subiu R$ 28,8 mil, dos quais R$ 10,8 mil vieram da maior taxa por minuto. Outros R$ 6 mil vieram do tempo adicional nos casos complexos. A capacidade ociosa em valor caiu R$ 16,8 mil. Para explicar o aumento da taxa, concilie folha, encargos e capacidade prática. Para explicar o tempo adicional, revise a amostra de casos complexos por etapa.

O comentário informa se os tempos foram medidos ou estimados. O relatório guarda a versão da regra e o identificador de origem do fato citado. Uma afirmação sobre falha de processo, fraude ou fornecedor exige evidência própria.

## Regras de aceitação

| Controle | Verificação |
| --- | --- |
| Integridade de entrada | Período fechado, grupos identificados, chaves únicas, tempo e volume não negativos, capacidade prática positiva nos grupos TDABC |
| Conciliação | Lançamentos atribuídos diretamente, grupos de recursos e demais destinos somam a despesa em escopo. Em cada grupo, custo atribuído mais saldo soma o total do grupo |
| Cobertura do direcionador | Casos e consumo sem chave, medição ou critério aparecem em pendências. A visibilidade do saldo evita distribuir a diferença silenciosamente |
| Ponte de variação | Cada etapa usa uma base versionada. A soma dos efeitos com a variação do saldo de capacidade recompõe o desvio do grupo até o centavo |
| Revisão mensal | Operações valida volume, tempos e escala. Controladoria valida a base de custo e a conciliação. FinOps responde pelos direcionadores de tecnologia quando aplicável |

O piloto deve começar com um grupo de recursos, uma competência e duas classes de contestação. O modelo aceita expansão para canal, produto ou novos grupos quando os dados sustentarem a atribuição.

## Referências

- Robert S. Kaplan e Steven R. Anderson, [Time-Driven Activity-Based Costing](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=485443). Base para taxa por unidade de capacidade prática, equações de tempo e capacidade ociosa.
- FinOps Foundation, [Allocation](https://www.finops.org/framework/capabilities/allocation/). Base para atribuição de tecnologia, metadados de alocação e tratamento de custos compartilhados.
