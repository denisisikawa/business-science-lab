---
name: engineering-medallion-design
description: Projetar ou revisar Bronze, Silver, Gold e saídas operacionais de pipelines financeiros Databricks com critérios de promoção e grão explícitos.
---

# Arquitetura medalhão

Trabalhe no Finance Evolution Lab, pipeline nativo sem dbt e com dados fictícios. No checkout, leia os padrões em `databricks-pipeline-template/docs/ENGINEERING_STANDARDS.md` e o código/contrato afetado. Priorize padrões existentes; os nomes Unity Catalog e diretórios futuros são blueprint, não objetos implantados. Se uma decisão técnica já estiver definida, aplique-a e registre-a sem perguntar de novo. Não invente regra financeira, acesso, calendário ou aprovação para avançar.

## Decisões incorporadas

- Bronze preserva entrada/lote/origem; Silver aplica contrato e versões; Gold entrega grão de decisão; Ops contém rejeições/descartes/auditoria.
- Parta das camadas atuais. Não copie dados três vezes apenas para preencher um desenho e não contorne Silver para publicar número “mais rápido”.
- Declare por saída: fonte, grão, chave, moeda, transformação, destino de inválidos, critério de saída e consumidores.
- Separe fato transacional de agregação mensal. Dados reconciliados não são automaticamente semanticamente corretos na origem.
- Preserve quarentena, disposição dos registros e evidência de falha. Bloqueio de publicação exige mecanismo real além do diagrama.

## Exemplo e contraexemplo

Correto: transações tipadas por origem/chave em Silver; Gold por mês/centro/categoria. Incorreto: somar Bronze e chamar de Gold sem resolver versões e rejeições.

## Verificar

Mapeie cada regra à camada e teste, confira contagem/valores por destino e desenhe falha parcial. Para blueprint novo, gere plano compatível com `standards/example-plan.json` e use o verificador documentado; isso valida só declarações.

## Entrega padrão

Tabela `camada | fonte | grão | chave | regra | inválidos | critério de saída | estado` e fluxo legível. Marque implementado, testado ou proposto. Leia [o exemplo de desenho](references/design-patterns.md) para transições e exceções.

## Exceção que exige decisão

Nova fonte sem chave/versão ou mudança de grão histórico: avance no desenho independente, mas não invente critério de deduplicação/CDC.
