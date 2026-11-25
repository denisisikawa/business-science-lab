# Desenho da reconciliação financeira

[Voltar ao caso explicado](../README.md)

## Contrato de comparação

- Entrada de referência: `stg_finance_costs`, já tipada, no grão de lançamento.
- Saída: `fct_monthly_costs`, no grão mês × centro de custo × categoria.
- Valor: soma decimal BRL com escala 2; comparação exata, sem tolerância.
- Contagem: quantidade de linhas de staging em cada grupo.
- Cobertura: presença do grupo nos dois lados, com `FULL OUTER JOIN`.
- Falha: qualquer grupo ausente/extra, medida nula, valor ou contagem divergente.
- Dependências dbt: `ref` para os dois modelos; o teste usa o estado construído.

## Por que não conferir apenas o consolidado?

Uma diferença positiva pode cancelar outra negativa. O teste compara cada grupo,
mas mantém os dois valores e contagens no retorno para diagnóstico. Não interpreta
as divergências como perda financeira nem determina sua causa automaticamente.

## Por que não usar INNER JOIN ou preencher tudo com zero?

O join interno pode excluir um grupo sem par. Preencher todos os nulos com zero
pode confundir inexistência, medida ausente e zero legítimo. O marcador
`actual_present` e a contagem esperada identificam os lados presentes. Testes de
não nulidade e de chave continuam necessários: esta comparação não os substitui.

## Independência e limite da referência

A referência é recalculada do staging, não lida do próprio total reportado. Isso
permite detectar erros introduzidos na transformação ou na saída. Entretanto,
ambos os lados compartilham o staging: um erro de negócio já presente nele pode
ser reproduzido corretamente pelo mart e passar. Validar classificação e fonte
exige outra evidência independente.

## Investigar uma falha

1. Identifique mês, centro e categoria retornados; preserve a revisão e a entrada.
2. Compare os lançamentos de staging com a saída para esse grupo.
3. Verifique filtros, joins, agregação, duplicação e classificação alterados.
4. Separe defeito técnico de mudança de regra financeira.
5. Corrija em desenvolvimento e acrescente contraexemplo relevante.
6. Reconstrua e teste; revisão e publicação seguem a esteira autorizada.

O teste falha o comando dbt com dados divergentes. Isso não constitui rollback
multi-modelo nem bloqueio automático de todos os consumidores de tabelas que já
foram atualizadas. Publicação de versão aprovada precisa de desenho adicional.

## Duas evidências complementares

**Cenários negativos do seed:** o script `check_reconciliation_mutations.py`
carrega modelos já construídos em cópias de memória e modifica a saída, caso a
caso. O arquivo original é anexado read-only. São sete cenários selecionados,
não cobertura exaustiva nem taxa de precisão.

**Exemplo didático de R$ 100 mil:** `demonstrate_offsetting_errors.py` monta quatro
lançamentos em memória, constrói o mart com o modelo SQL compilado real e altera
R$ 10 mil em sentidos opostos. Confere o total constante e exatamente duas
linhas divergentes. Não abre a base persistente e não altera o seed do projeto.

Os dois scripts executam o teste compilado, em vez de recriar a regra financeira
em Python. `manifest.json` fornece os nomes das relações para as cópias locais.
O fluxo é específico ao laboratório local e depende dos artefatos de um build
anterior; não é um mecanismo portátil de produção para qualquer adaptador.

## Extensões que precisam de decisões de negócio

| Tema | Decisão necessária |
|---|---|
| Orçamento | Grão, versão e calendário compatíveis com realizado |
| Créditos | Quando um total negativo/zero é válido |
| Moedas | Taxa, data, fonte, direção e arredondamento |
| Período ausente | Calendário esperado e prazo de disponibilização |
| Alteração histórica | Versão de fechamento, backfill e reprodução |
| Classificação incorreta na origem | Cadastro/contrato/razão de referência independente |

Essas extensões são propostas, não funcionalidades implementadas por este caso.

## Cobertura independente — extensão de 25/11/2026

`finance_reporting_scope` é um seed tipado e separado dos fatos; declara os 18
grupos esperados do caso fictício. `assert_reporting_scope_coverage` compara a
união das chaves do escopo/staging/mart e retorna indicadores de presença. Assim,
perda simultânea de um grupo nos dois fatos não fica invisível. Grupos extras
também falham; o teste de validade do escopo trata duplicação, nulos/brancos e
mês fora do primeiro dia. A decisão de quais grupos exigir é de negócio.

O helper novo executa os controles compilados em cópias em memória, com a base
original read-only. Sete cenários de cobertura: mês inteiro perdido nos dois
lados, fatos totalmente vazios, um grupo perdido nos dois, perda só no staging,
perda só no mart, grupo inesperado nos dois e escopo excluindo grupo observado.
Três cenários do escopo: duplicata, data não mensal e centro vazio. Casos de
perda compartilhada confirmam também que a reconciliação antiga não os detecta.

Isto não verifica pontualidade/freshness, calendário fiscal empresarial ou dados
realmente esperados fora do contrato declarado. Se escopo e fatos forem mudados
incorretamente juntos, o controle pode passar; revisão e versão do escopo são
parte da governança. Nenhum valor ausente é preenchido automaticamente com zero.
