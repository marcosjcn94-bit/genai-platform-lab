# Registro de execução

## 2026-10-01
- Plano recebido e PLANO.md conferidos; inicialmente apenas PLANO.md e AGENTS.md.
- Git inicializado na branch implementation.
- Docker CLI instalado por usuário; daemon inicialmente indisponível.
- Python global 3.13; Python 3.12 será isolado no projeto com uv.
- AWS não provisionada; não executar apply nem alterar plano financeiro.
- Etapas 0–9 pendentes de implementação/verificação; nenhuma conclusão implícita.
- Etapa 1: pytest integration/test_vertical: 1 passed; chave idempotente, admin negado, 12 tokens/custo zero, registro sem marcador do prompt. /key/info não inclui token: hash SHA256 da chave é conferido contra api_key do registro.
- Terraform 1.13.3 instalado no projeto com SHA256 conferido; provider AWS 6.14.1. fmt, init -backend=false e validate executados com sucesso. Sem plan/apply/recursos AWS.
- Etapa 2: FastAPI autentica app-a/app-b e encaminha chaves distintas; validação por schema, corpo limitado, erros sanitizados e relatório derivado de spend logs com paginação/dedup/UTC. Integração vertical e teste de duas aplicações/fallback passaram antes da interrupção atual. Unitários: 26 passaram.
- Etapas 3–4 parcialmente implementadas: retries/fallback e timeout no gateway; aliases separados por cenário para contagem não contaminada. Grafana/Prometheus/Jaeger responderam e gateway readiness reportou DB conectado, mas API :8000 ficou sem resposta na validação final. Docker named pipe negou acesso ao processo; logs/health do container não puderam ser rechecados. Não declarar fallback/timeout/trace ponta a ponta como revalidados.
- Etapa 5: CI separado em lint/formatação, unidade, integração Docker e build. Secrets efêmeros gerados localmente via init_env; workflow ainda não executado no GitHub. Carga de 60 s e dez chamadas Ollama pendentes por API indisponível.
- Etapa 6: PySpark 3.5.5 em Docker validou fixture sintética, Decimal, nulos, deduplicação, totais e idempotência de Parquet. Execução Databricks não feita.
- Etapa 7: AWS somente estática; sem credentials/plan/apply/recursos. Conferência financeira futura exigida.
- Etapa 9: README criado com comandos e limites observados; revisar após desbloquear o container API.
