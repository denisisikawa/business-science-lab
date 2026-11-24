# Nomes, significado e compatibilidade

O ambiente fica no catálogo, a camada no schema e assunto/grão no objeto. Evite repetir tudo no nome sem benefício: `finance_lab_dev.gold.cost_monthly` já comunica ambiente e camada.

Uma view com sufixo approved só merece esse nome se houver versão/mecanismo de aprovação implementado; o nome sozinho não garante publicação validada. Não invente essa garantia por convenção.

Se o objeto existente usa outro nome, verifique SQL, notebooks, jobs, permissões e consumidores antes de propor rename. Um alias/view de compatibilidade também exige análise de acesso e ciclo de desativação.

Identificadores vêm de configuração aprovada/allowlist, não de texto livre do usuário. Parametrização de valores SQL não parametriza nomes de catálogo/tabela da mesma forma.
