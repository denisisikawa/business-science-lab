# Padrões de engenharia do Finance Evolution Lab · versão 1.0

## Escopo e precedência

Este documento escolhe **defaults locais do laboratório**, não uma norma universal
Databricks. Instruções do usuário e padrões efetivos do repositório/organização
têm precedência. Não renomeie objetos existentes, mova módulos ou migre dados só
para adequar um exemplo. Registre divergências e proponha uma migração no escopo
solicitado. Não há instalação global, criação de catálogo ou implantação neste ato.

Quando a tarefa é puramente analítica, não exija acesso a todos os arquivos de
engenharia: use o material disponível e solicite apenas a informação financeira
material que faltar. Quando há implementação, confira o checkout e a versão real.

## Como poupar perguntas sem inventar decisões

1. Leia contrato/configuração e use o padrão existente.
2. Para artefato novo deste laboratório, aplique o default abaixo e registre-o.
3. Faça uma pergunta somente se a resposta alterar significado, acesso, custo
   relevante, histórico, perda de dados ou um contrato externo não definido.
4. Conclua trabalho independente enquanto a decisão material está pendente.
5. Não invente calendário fiscal, taxa de câmbio, orçamento ou aprovação para evitar uma pergunta.

Os defaults reduzem redescoberta e escolhas mecânicas; não eliminam aprendizado
de negócio nem a responsabilidade do analista de revisar a regra e a evidência.
Não há redução de tokens, custo ou tempo medida nesta entrega.

## Medallion: responsabilidade e critério de saída

| Camada | Responsabilidade | Critério de saída |
|---|---|---|
| Bronze | Conteúdo recebido e metadados de lote/origem; sem regra financeira silenciosa | Entrada localizável e schema mínimo de ingestão |
| Silver | Tipagem, chave, versão, conflito e destinos dos registros | Contrato e reconciliação de destinos aprovados |
| Gold | Agregação por grão de decisão e regra financeira explícita | Valores/contagens reconciliados e definição de consumo |
| Ops | Auditoria, rejeições, descartes e resultados de controle | Motivo, referência ao lote e política de retenção |

Camadas são responsabilidades lógicas, não exigência de copiar tudo três vezes.
Não leia Bronze diretamente em um relatório aprovado para contornar qualidade.
Quarentena não desaparece para o número “bater”. Não transforme Bronze em cópia
irrestrita de dados pessoais: retenção e autorização continuam necessárias.

## Nomes propostos para objetos novos em Unity Catalog

Padrão: `catalog.schema.object`. Identificadores em inglês, `snake_case`, sem
espaços, acentos, nomes de pessoas ou sufixos `final`, `final2`, `new`.

| Tipo | Default do laboratório | Exemplo de design, não objeto implantado |
|---|---|---|
| Catálogo | `finance_lab_<env>`; env `dev`, `test`, `prod` | `finance_lab_dev` |
| Schema | Responsabilidade da camada | `bronze`, `silver`, `gold`, `ops` |
| Tabela Bronze | Assunto + `_raw` | `finance_lab_dev.bronze.cost_transactions_raw` |
| Tabela Silver | Assunto e grão estável | `finance_lab_dev.silver.cost_transactions` |
| Tabela Gold | Assunto + grão | `finance_lab_dev.gold.cost_monthly` |
| Rejeitados/descartados | Assunto + disposição | `ops.cost_transactions_rejected`, `ops.cost_transactions_superseded` |
| View | `vw_` + finalidade | `gold.vw_cost_monthly_approved` |
| Função | Verbo/resultado explícito | `ops.normalize_cost_category` |
| Job | Domínio + propósito + ambiente | `finance_cost_pipeline_dev` |
| Tarefa | Verbo + camada/assunto | `ingest_bronze`, `transform_silver`, `aggregate_gold` |
| Coluna | Significado + sufixo de unidade quando necessário | `updated_at`, `transaction_count`, `amount_cents` |

`month`, `amount`, `currency` e demais campos do contrato atual são preservados.
Não renomeie por preferência editorial. Sufixos `_at` para instante, `_date` para
data, `_id` para identificador e `_count` para contagem são convenções para novos
campos. Não misture `amount_cents` (inteiro) com `amount` (decimal monetário).
Use nomes plenamente qualificados em código remoto quando o ambiente exigir.
Não interpolar livremente identificadores recebidos de usuário em SQL.

**Estado atual:** o adaptador usa paths Delta e o backend local usa SQLite.
A nomenclatura Unity Catalog acima é um blueprint. Registrar uma managed table
exige um desenho e permissões próprios, não apenas substituir o nome do path.

## Diretórios: preservar o que funciona e separar responsabilidades

```text
databricks-pipeline-template/
  notebooks/                   # entradas existentes e módulos adjacentes atuais
  src/finance_pipeline/        # destino para módulos novos quando necessário
  config/                     # configuração sem segredos por ambiente
  contracts/                  # contratos versionados quando materializados
  resources/                  # descrições de jobs/deployment quando implementadas
  standards/                  # política e planos de design verificáveis
  scripts/                    # verificadores locais
  docs/                       # decisões, uso e operação
  skills/                     # conhecimento por tarefa
```

`tests/` do repositório já contém os testes do pipeline. Não crie uma segunda
suíte paralela sem necessidade. `src`, `config`, `contracts` e `resources` acima
são destinos convencionados para evoluções, não pastas já implementadas. Notebook
coordena parâmetros e chamada de módulo; regra testável não deve depender de
estado oculto de células. Se mover módulos, preserve import/entrypoint e valide
o notebook sincronizado. Não despeje outputs, segredos ou venv dentro de `src`.

## Transformações e precisão

- Schema explícito, casts verificados, projeção de colunas e datas/fusos definidos.
- BRL e Decimal(18,2) no Spark; centavos inteiros no backend local. Créditos válidos.
- Antes de join, declare cardinalidade e chaves; teste fan-out e registros sem par.
- Antes de merge, resolva duplicatas/conflitos determinísticos na origem.
- Prefira funções Spark nativas quando equivalentes e testadas. Não substitua o
  normalizador compartilhado/UDF atual sem demonstrar paridade do contrato.
- Evite `collect`/`toPandas` sobre dados sem limite. Pequenas métricas agregadas são
  outro caso; documente cardinalidade esperada.
- `fillna(0)`, `dropDuplicates` e `overwriteSchema` não são políticas de negócio.

## Jobs e configuração

Configuração externa distingue ambiente, origem, destino, período, lote, versão
transacional e versão de regra. Segredos por mecanismos privados do ambiente;
nenhum segredo em arquivo de exemplo, argumento exposto ou prompt.

Default de **design ilustrativo**: dev, timeout de tarefa 900 segundos e retry
zero até haver idempotência demonstrada. Não é SLA nem sizing recomendado para
produção. O plano deve declarar dependências acíclicas e comportamento diante de
falha. Token que evita duplicar um disparo de job não prova idempotência das
escritas feitas pelo job. Uma falha posterior não reverte automaticamente tabelas
já gravadas.

## Testes e observabilidade

| Escopo | Verificar | O que não comprova |
|---|---|---|
| Unidade | Regra, fronteira e contraprova com resultado independente | Runtime remoto |
| Integração local | Tipos Spark, janelas, paridade | Delta/JDBC e acesso produtivo |
| Persistência | Retry, merge, colisão, rollback no backend relevante | Outra tecnologia de armazenamento |
| Operação | Falha parcial, recuperação, promoção e consumo | Conformidade universal |

Logs estruturados devem identificar lote, revisão, etapa, disposição, duração e
resultado sem registrar payload sensível ou token. Métrica ausente não vira zero.
Freshness precisa de calendário/SLA; alerta precisa de dono e ação definidos.

## Performance e custo: default é medir

Defina volume, janela, runtime/compute, número de ações, shuffle, spill, tempo e
custo quando disponível. Compare resultados financeiros antes/depois. Sem uma
base comparável, entregue hipótese e plano de medição, não percentual de ganho.
Não imponha particionamento, cache, broadcast, `repartition(1)` ou cluster maior
como regra universal. Tecnologia/feature depende da versão do runtime e dos dados.

## Verificador de plano: mecanismo executável limitado

[Política JSON](../standards/engineering.json) e [plano ilustrativo](../standards/example-plan.json)
materializam parte dos defaults. Da raiz do repositório:

```bash
python databricks-pipeline-template/scripts/check_engineering_plan.py --plan databricks-pipeline-template/standards/example-plan.json
python -m pytest tests/test_engineering_plan.py -q
```

O verificador confere versão de política, ambiente, nomes/catálogos, campos mínimos,
tipos, grão/chave do contrato, diretórios relativos seguros e dependências/retry
**declarados**. Sua saída não cria objetos, lê dados, consulta IAM ou demonstra que
a tarefa é idempotente. Uma referência de evidência preenchida também não prova
que essa evidência é verdadeira; revisão humana e execução relevante continuam
necessárias. O plano não é um payload de API/Bundle pronto para deploy.

Objetos fora desse blueprint (outra moeda, grão, política, função/modelo/volume)
pedem revisão da política e testes específicos, não remoção silenciosa da validação.
O verificador não analisa código arbitrário nem valida uma organização inteira.

## Referências primárias e decisões locais

- [Medallion Databricks](https://learn.microsoft.com/en-us/azure/databricks/lakehouse/medallion).
- [Objetos e namespace Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects).
- [Tuning Spark](https://spark.apache.org/docs/latest/sql-performance-tuning.html).
- [Retries de Jobs](https://docs.databricks.com/api/jobs/v2/run).

Consultadas em 23/11/2026. Nomes, pastas, exemplos e timeout são decisões
ilustrativas deste laboratório; não foram prescritos universalmente pelo fabricante.
