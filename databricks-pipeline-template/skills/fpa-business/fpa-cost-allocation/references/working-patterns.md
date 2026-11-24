# Especificação de alocação

`Pool | natureza | período | objeto | driver e unidade | fonte/cobertura | denominador | fórmula | centavos/resíduo | não alocado | versão`.

**Bom:** pool 100 e driver 1:2 com saída 33,33/66,67 segundo desempate definido. **Ruim:** arredondar cada parte sem verificar a soma ou usar partes iguais porque falta driver.

## Contraprovas

Driver faltante, total zero, consumo negativo inesperado, dimensão repetida, mistura de períodos e mudança de vigência. Verifique que apropriação direta não volta a entrar no pool compartilhado.

## Capacidade

Recurso 1.000, capacidade prática 100 min, consumo 80 min: taxa 10/min, custo atribuído 800 e saldo 200. Isso reconcilia o recurso, mas não comprova economia realizável. Excesso de capacidade consumida exige avaliação de tempo/denominador/cobertura.

A revisão de negócio escolhe o driver justificável e a política; a engenharia implementa tipos, resíduos e testes. Não declare que o template já oferece TDABC só porque a skill conhece o método.
