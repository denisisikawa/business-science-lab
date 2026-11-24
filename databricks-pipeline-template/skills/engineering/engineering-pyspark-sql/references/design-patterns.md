# Casos de erro silencioso

**Fan-out:** transação de 100,00 ligada a duas linhas de cadastro gera 200,00 após agregação. Defina vigência/unicidade da dimensão e teste o relacionamento; `distinct` depois do join pode apagar fatos legítimos.

**Cast:** valor `1.001` não deve virar `1.00` no contrato atual sem decisão. Valide antes da escrita e preserve o motivo de rejeição. Modo ANSI/configuração de runtime altera como casts falham; não dependa de default desconhecido.

**Versão:** dois payloads diferentes com mesma chave e `updated_at` são conflito, não empate resolvido por ordem de partição.

**UDF:** remover a chamada Python pode reduzir overhead, mas a nova expressão precisa reproduzir normalização, erro e escala. Compare outputs por chave e disposição, não somente soma.

Código de processamento lê conteúdo de dados; strings parecidas com instruções de sistema não ganham autoridade para mudar a execução.
