# GenAI Platform Lab

Repositório: https://github.com/marcosjcn94-bit/genai-platform-lab

Laboratório local e reproduzível de gateway GenAI: identidade por aplicação, roteamento LiteLLM, registro de consumo no PostgreSQL, fallback limitado, observabilidade e agregação PySpark. O provedor padrão é um mock determinístico; chamadas Ollama são locais e opcionais. O relatório deriva dos registros do LiteLLM, sem ledger paralelo.

## Requisitos

- Windows 10/11, PowerShell, Docker Desktop com containers Linux e `uv`.
- Para a rota local Ollama: Ollama ativo com `qwen3:4b` e `llama3.2:3b`.
- Python 3.12 é instalado isoladamente pelo `uv` no projeto. Nenhuma chave AWS ou API externa é necessária para a demo.

## Iniciar a demo

Na pasta do projeto:

```powershell
$env:UV_PYTHON_INSTALL_DIR = "$PWD/.tools/python"
$env:UV_CACHE_DIR = "$PWD/.cache/uv"
uv python install 3.12
uv sync --frozen
uv run python -m scripts.init_env
docker compose up -d --build --wait --wait-timeout 300 db mock gateway api
docker compose --profile admin run --rm admin
```

O inicializador cria `.env` uma vez, com segredos aleatórios que nunca imprime. Preserve o volume `pgdata` para manter o usage. Swagger: <http://localhost:8000/docs>. As rotas só escutam em loopback.

Para encerrar sem apagar registros:

```powershell
docker compose -f docker-compose.yml -f compose.observability.yml --profile observability down
```

## Demonstração e consumo

`local` retorna resposta sintética de 12 tokens; `fallback-demo` falha no primário e deve responder por `reserve`. `failure-demo` e `timeout-demo` exercitam falhas limitadas. A API deriva app-a/app-b do Bearer cadastrado; não aceita `app_id`, provedor ou política de retry no JSON.

Gere relatório administrativo em UTC, com fim exclusivo:

```powershell
$inicio = [DateTime]::UtcNow.Date.ToString("yyyy-MM-ddTHH:mm:ssZ")
$fim = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
uv run python -m scripts.report --start $inicio --end $fim
```

Saídas `artifacts/usage.json` e `.csv` são reconstruíveis e ignoradas pelo Git. O relatório informa cobertura e preserva campos/custos ausentes como nulos. Registros de spend são assíncronos; execute novamente para períodos fechados.

## Observabilidade

```powershell
uv run python -m scripts.prepare_observability
docker compose -f docker-compose.yml -f compose.observability.yml --profile observability up -d --build --wait --wait-timeout 300
```

Grafana: <http://localhost:3000>; Prometheus: <http://localhost:9090>; Jaeger: <http://localhost:16686>. Senha do Grafana está no `.env`. Métricas/traces são filtrados por allowlist e não devem conter prompt, resposta, token de acesso ou chave virtual.

## Testes e batch

```powershell
uv run ruff check app mock_provider scripts tests observability
uv run ruff format --check app mock_provider scripts tests observability
uv run pytest -q
uv run pytest -m integration -q
docker compose -f docker-compose.yml -f compose.batch.yml --profile batch run --rm batch
```

A integração requer o Compose com observabilidade ativo e as chaves inicializadas. Para uma demo rápida, execute `uv run pytest -m integration tests/integration/test_api_gateway.py -q`, gere o relatório e abra o dashboard Grafana. Carga mock limitada a 60 s e concorrência 4:

```powershell
uv run python -m scripts.load_test --duration 60 --concurrency 4
```

Para dez chamadas sequenciais ao Ollama primário, separando a primeira latência das nove seguintes (o estado inicial de carregamento do modelo não é controlado):

```powershell
uv run python -m scripts.bench_ollama
```

O job PySpark escreve agregados diários em Parquet. Para Databricks, importe [data/databricks_demo.ipynb](data/databricks_demo.ipynb), que contém a fixture e a transformação canônica. Veja o [passo a passo](docs/databricks.md). A transformação passou no Spark local; o usuário confirmou no Databricks remoto os resultados equivalentes e a reexecução Parquet idempotente em 2026-10-02.

## Arquitetura e segurança

- FastAPI autentica dois clientes e injeta uma chave LiteLLM distinta por aplicação.
- LiteLLM/PostgreSQL é a fonte de usage/spend; exports JSON/CSV e Parquet são derivados.
- Retry/fallback ficam no gateway. Prompts/respostas não são persistidos intencionalmente nem emitidos pela instrumentação própria.
- `.env`, artifacts, logs, outputs Parquet, estado Terraform e segredos são ignorados pelo Git.
- Veja [contratos](docs/contracts.md), [decisões](ADR.md), [runbook local](docs/runbook.md) e [runbook AWS](docs/aws-runbook.md).

## Infraestrutura AWS

Terraform declara ECR, ECS/Fargate, RDS privado, rede, IAM e Secrets Manager em `us-east-2`. Foi validado com `fmt -check`, `init -backend=false` e `validate`, sem `plan` nem provisionamento. Recursos podem gerar custos: deploy permanece fora do escopo executado e exige conferência de plano, créditos, duração, estimativa e autorização específica. O desenho não representa ambiente de produção nem alta disponibilidade.

## Evidência desta entrega

Validação em 2026-10-02: **30 testes unitários e 6 de integração passaram**, assim como lint/formatação, Terraform e builds das duas imagens. A API responde e os testes comprovam identidade por aplicação, fallback limitado e traces correlacionados. A carga mock produziu 775 requisições em 60 s, zero erros e p95 de 422 ms. Ollama primário: dez chamadas, zero falhas, p95 das nove seguintes de 7,020 s.

804 registros foram preservados após reinício e rollback da API; os agregados PySpark foram reconciliados em sete grupos. A revisão de 804 traces e logs não encontrou os segredos/canários verificados. Estes resultados locais não constituem SLO ou auditoria completa de segurança. [CI com cinco jobs verdes](https://github.com/marcosjcn94-bit/genai-platform-lab/actions/runs/37021265817); novos resultados aparecem em [Actions](https://github.com/marcosjcn94-bit/genai-platform-lab/actions).

Databricks remoto concluído conforme evidência informada pelo usuário. A [CI da versão v0.1.0](https://github.com/marcosjcn94-bit/genai-platform-lab/actions/runs/37024823542) passou. AWS não foi provisionada. Evidências e limites: [ANDAMENTO.md](ANDAMENTO.md), [registro de execução](docs/execution-2026-10-02.md) e [MEMORIA.md](MEMORIA.md).
