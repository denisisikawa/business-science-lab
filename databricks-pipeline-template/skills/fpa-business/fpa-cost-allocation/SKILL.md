---
name: fpa-cost-allocation
description: Definir apropriação e alocação gerencial de custos por drivers, capacidade e TDABC com conservação de totais. Use para critérios de rateio e custo por objeto; não presume regra fiscal ou contábil.
---

# Alocação, drivers e capacidade

Para análise de negócio, use as definições e dados fornecidos; não exija o checkout inteiro. Se a tarefa envolver código, localize o Finance Evolution Lab e confira README, contrato, adaptador e testes afetados. Não presuma que uma regra documentada já está implementada. Use dados fictícios; não introduza dbt neste pipeline nativo. A skill orienta o trabalho, não concede acesso nem aprovação de negócio.

## Aplicar

Leia [casos de alocação](references/allocation-cases.md) para escolher drivers e avaliar capacidade. Formalize objeto de custo, perímetro, período, natureza gerencial e decisão pretendida.

- Separe custo direto apropriável, indireto alocável e corporativo mantido separado conforme o caso. Não transforme toda despesa em rateio por conveniência.
- Driver precisa de unidade, origem, vigência, grão e justificativa econômica; facilidade de medição não prova causalidade. Não use receita ou headcount como driver universal.
- Partes devem conservar o total alocável, com regra explícita para resíduos de arredondamento. Preserve não alocado/ociosidade quando aplicável, em vez de distribuir para esconder saldo.
- Denominador zero ou cobertura incompleta exigem exceção explícita; não divida por zero nem atribua partes iguais sem decisão aprovada.
- TDABC requer custo dos recursos, capacidade prática, taxa e tempos compatíveis. Ociosidade não é economia automaticamente realizável; demanda acima da capacidade exige investigação.
- Evite dupla contagem entre apropriação direta, pools compartilhados e custo corporativo. Custo médio e marginal respondem perguntas diferentes.
- Mudança de driver altera comparabilidade histórica; explicite versão e simulação antes/depois.

## Entregar

Mapa custo → objeto/driver, fórmula, unidades, cobertura, exceções, regra de resíduos, conservação e impacto. Escreva exemplos financeiros independentes para a equipe técnica testar. Não reivindique TDABC implementado neste template: é conhecimento para uma extensão futura.

## Caso de avaliação

Pool de 100,00 com drivers 1:2 deve distribuir 33,33 e 66,67 sob política explícita de resíduo; total 100,00. Driver todo zero deve retornar exceção ou não alocado segundo política, não custo zero.

## Defaults, modelos e verificações incorporadas

- Primeiro separe direto, indireto e corporativo; não eleja um driver universal para simplificar a análise.
- No exemplo fictício 100 com drivers 1:2, apresente uma política de centavos que conserve 100; não a trate como regra contábil universal.
- Driver ausente/zero produz exceção/não alocado conforme política, não divisão por zero ou rateio igual improvisado.
- Modelo: pool, objeto, driver/unidade, vigência, fórmula, resíduos, ociosidade/não alocado e reconciliação.

Leia [o padrão de trabalho e os exemplos](references/working-patterns.md) para a saída esperada, contraprovas e critérios de aceite. Em implementação, consulte `databricks-pipeline-template/docs/ENGINEERING_STANDARDS.md` se disponível; padrões existentes prevalecem e ausência do checkout não autoriza inventar sua estrutura.
