# Playbook de revisão

## Modelo de achado

`Severidade | arquivo/trecho | condição que dispara | efeito financeiro/operacional | correção ou evidência necessária`.

Classificação ilustrativa: bloqueador quando altera dado material sem recuperação/critério; alto para risco concreto de duplicação ou perda; menor para documentação inconsistente sem mudança de cálculo. Use a política real da equipe quando houver, sem inventar materialidade monetária.

**Bom:** apontar que um INNER JOIN elimina grupos sem par e exigir teste de grupo ausente. **Ruim:** aprovar porque o total consolidado e o lint passaram.

## Aceite

Confira regra, exemplos e convenção financeira; depois tipos, chaves, destinos, replay e diferenças entre runtimes. Compare comando/revisão executados com o diff. Deixe explícitas as verificações não realizadas.

Use revisão independente para mudança crítica conforme política. Um segundo prompt, outra skill ou outro “chapéu” do mesmo autor não representa segregação de aprovação. Não altere branch protection ou permissões para viabilizar a entrega.
