# Massa sintética · Custos bancários

Dados fictícios de janeiro a dezembro de 2025, com orçamento e realizado. A base representa três produtos, sete áreas internas e nove contratos. As tabelas usam identificadores estáveis para relacionar volumes, valores, responsáveis e direcionadores. Os volumes são agregados. Cada linha representa um tipo de evento em um produto, canal, mês e cenário.

## Arquivos

| Arquivo | Linhas | Grão ou uso |
| --- | ---: | --- |
| [`areas.csv`](example/areas.csv) | 7 | Área interna responsável por custos ou produtos |
| [`produtos.csv`](example/produtos.csv) | 3 | Cartões, Conta e Pagamentos, e Crédito Pessoal |
| [`contratos.csv`](example/contratos.csv) | 9 | Contrato com vigência, mensalidade base, tarifa e evento faturável, quando aplicável |
| [`volumetria.csv`](example/volumetria.csv) | 240 | Mês × cenário × produto × canal × evento |
| [`custos.csv`](example/custos.csv) | 288 | Mês × cenário × item de custo. Valor fixo, variável e total em BRL |
| [`direcionadores.csv`](example/direcionadores.csv) | 312 | Mês × cenário × direcionador × produto |
| [`capacidade.csv`](example/capacidade.csv) | 24 | Mês × cenário × equipe de contestação. Minutos de capacidade prática e de trabalho consumido |

Os CSVs usam UTF-8, vírgula como delimitador e ponto decimal. Some volumes de um mesmo evento para o uso correspondente. Autorizações, análises e contratações representam eventos operacionais distintos. Campos vazios indicam que o atributo não se aplica. Os períodos contratuais são inclusivos.

## Como segmentar

| Natureza | Tratamento | Casos na amostra |
| --- | --- | --- |
| `direto` | Apropriar ao `produto_direto_id` | Processador de cartões, motor de pagamentos, motor de crédito e tronco dedicado a Cartões |
| `indireto` | Distribuir pelo direcionador do mesmo mês e cenário | Cloud por horas de computação, licenças por assentos, WAN por links ativos, aluguel e facilities por m² ocupados |
| `indireto` · TDABC | Dividir o custo da equipe pela capacidade prática e aplicar a taxa aos minutos trabalhados | Contestação simples e complexa. Ociosidade corresponde ao saldo entre custo da equipe e custo atribuído |
| `corporativo` | Manter no centro de custo corporativo na visão gerencial | Aluguel do escritório corporativo e equipe da diretoria |

As colunas `natureza` e `categoria` respondem a perguntas diferentes. Telecom aparece como custo direto no tronco dedicado e como indireto na WAN. Aluguel aparece tanto como indireto na operação quanto como corporativo no escritório. A área dona do contrato permite responsabilizar quem administra o gasto. O produto identifica a operação que consome ou recebe o custo.

### Como cruzar os arquivos

- Vincule `custos.contrato_id` a `contratos.contrato_id`. Os itens internos têm este campo vazio. Use as colunas de valor de `custos.csv` como fato mensal. `contratos.csv` registra as condições de referência.
- Para contratos variáveis, some os volumes do evento faturável por mês, cenário e produto. Multiplique pela tarifa e arredonde a cobrança variável ao centavo. O valor total soma a cobrança variável à parcela fixa.
- Para custos compartilhados por consumo, ligue a linha de custo ao direcionador por mês e cenário. Divida o consumo do produto pelo consumo total do direcionador e aplique a participação ao valor da despesa.
- Para o TDABC, use `capacidade.csv` como denominador da taxa. Vincule `I01` à folha de contestação em `custos.csv`. Os minutos de trabalho saem da soma de volume × tempo ativo nas linhas de contestação. A [metodologia](../BANKING_COSTING.md) explica a conciliação de capacidade.

### Exemplo · aluguel de julho no realizado

O contrato de aluguel operacional `C07` tem despesa de **R$ 79.800,00**. Os produtos ocupam 1.040 m². Cartões ocupa 420 m² e recebe **R$ 32.226,92**. Conta e Pagamentos recebe R$ 26.088,46, e Crédito Pessoal, R$ 21.484,62. O aluguel corporativo `C09` permanece em Diretoria Corporativa.

Na amostra há sazonalidade de volume no fim do ano, reajuste simulado de 5% em WAN e aluguel operacional a partir de julho, aumento de custo da equipe de contestação a partir de março e maior tempo por contestação complexa em meses selecionados. Esses eventos facilitam exercícios de orçamento versus realizado.

## Reprodução

A partir da raiz do repositório, com Python 3.11 ou superior:

```bash
python macro-fpa/synthetic-banking/generate.py --year 2025 --seed 42 --output dados-banco
```

A semente controla os volumes realizados. O gerador produz as tabelas de entrada para exercícios de custeio. A aplicação das regras de rateio aos valores mensais é uma etapa posterior.

## Sandbox interativo

[Banking Cost Intelligence — Cost Impact Explorer](https://denisisikawa.github.io/business-science-lab/banking-cost-sandbox/) aplica as regras desta massa sintética, apresenta a ponte de variação por dimensão e permite investigar origens, testar premissas e conferir a conciliação. [Documentação e testes](COST_IMPACT_EXPLORER.md).
