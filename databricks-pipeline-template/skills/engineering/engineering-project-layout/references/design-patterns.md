# Separar responsabilidades sem refatoração decorativa

Exemplo futuro: notebook coleta parâmetros → módulo aplica transformação → teste usa DataFrame pequeno e verifica resultado independente. O normalizador puro pode continuar compartilhado pelo backend local e pelos workers Spark.

Antes de mover qualquer módulo: busque imports e caminhos, confira `HERE`, wrappers `.ipynb`, sincronizador e distribuição para executores. Uma execução no driver não comprova import no worker.

Dados gerados e arquivos DuckDB/SQLite pertencem a outputs locais ignorados. Fixtures pequenas e sintéticas podem ser versionadas para reprodução. Nunca mova dados de empregadores para fixtures públicas.

Critério de aceite: os comandos documentados continuam funcionando de checkout limpo e não dependem de variáveis/células ocultas. Se não houver runtime remoto, registre o limite.
