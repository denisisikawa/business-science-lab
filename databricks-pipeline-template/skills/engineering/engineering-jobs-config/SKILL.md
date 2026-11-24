---
name: engineering-jobs-config
description: Desenhar jobs e configuração por ambiente com DAG, parâmetros, timeout, retries e identidade de execução, respeitando esteiras existentes.
---

# Jobs e configuração

Trabalhe no Finance Evolution Lab, pipeline nativo sem dbt e com dados fictícios. No checkout, leia os padrões em `databricks-pipeline-template/docs/ENGINEERING_STANDARDS.md` e o código/contrato afetado. Priorize padrões existentes; os nomes Unity Catalog e diretórios futuros são blueprint, não objetos implantados. Se uma decisão técnica já estiver definida, aplique-a e registre-a sem perguntar de novo. Não invente regra financeira, acesso, calendário ou aprovação para avançar.

## Decisões incorporadas

- Separe config de ambiente e código; parâmetros identificam origem/destino, lote, período, versão da regra e transação quando aplicável.
- DAG inicial: ingestão Bronze → transformação Silver → agregação Gold; testes e publicação têm dependências explícitas quando implantados.
- Default de design ilustrativo: dev, timeout 900 s, retry zero até idempotência demonstrada. Não recomende esse timeout como SLA universal.
- Dependências não podem ser cíclicas nem apontar tarefa inexistente. Paralelize apenas trabalho independente.
- Configure retries somente com política de dados e evidência relevante; evitar dois disparos do mesmo job não evita duplicação de suas escritas.
- Segredos por mecanismo privado; não gravar em notebooks, JSON versionado, logs ou argumentos expostos. Identidade de implantação não é a identidade do autor.
- Reutilize esteira/bundles existentes se houver. Não faça deploy nem crie cron/serviço adicional por inferência.

## Exemplo e contraexemplo

Correto: tarefa Silver depende da Bronze bem-sucedida e falha impede o próximo passo configurado. Incorreto: ativar retries em append não idempotente ou dizer que a falha reverte todos os outputs.

## Verificar

Gere plano e execute o verificador local para nomes, campos e DAG. Valide payload com ferramenta oficial/versionada antes de uso remoto; plano de design não é Jobs API nem Bundle pronto.

## Entrega padrão

Tabela de tarefas/dependências/parâmetros/timeout/retry, identidade, política de falha e itens não implantados. Leia [os casos de operação](references/design-patterns.md).

## Exceção que exige decisão

Nova permissão, custo remoto, origem com credencial ou escrita produtiva não são autorizados por um template.
