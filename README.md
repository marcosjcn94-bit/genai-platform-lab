# GenAI Platform Lab

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
docker compose down
```

## Demonstração e consumo

`local` retorna resposta sintética de 12 tokens; `fallback-demo` falha no primário e deve responder por `reserve`. `failure-demo` e `timeout-demo` exercitam falhas limitadas. A API deriva app-a/app-b do Bearer cadastrado; não aceita `app_id`, provedor ou política de retry no JSON.

Gere relatório administrativo em UTC, com fim exclusivo:

```powershell
uv run python -m scripts.report --start 2026-10-01T00:00:00Z --end 2026-10-02T00:00:00Z
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
uv run ruff check app mock_provider scripts tests
uv run ruff format --check app mock_provider scripts tests
uv run pytest -q
uv run pytest -m integration -q
docker compose -f docker-compose.yml -f compose.batch.yml --profile batch run --rm batch
```

A integração requer o Compose ativo. Carga mock limitada a 60 s e concorrência 4:

```powershell
uv run python -m scripts.load_test --duration 60 --concurrency 4
```

Para dez chamadas sequenciais ao Ollama primário, separando a primeira latência (carregamento) das nove seguintes:

```powershell
uv run python -m scripts.bench_ollama
```

O job PySpark escreve agregados diários em Parquet. Notebook Databricks e fixture estão em `data/`; a execução remota ainda não foi verificada.

## Arquitetura e segurança

- FastAPI autentica dois clientes e injeta uma chave LiteLLM distinta por aplicação.
- LiteLLM/PostgreSQL é a fonte de usage/spend; exports JSON/CSV e Parquet são derivados.
- Retry/fallback ficam no gateway. Prompts/respostas não são persistidos intencionalmente nem emitidos pela instrumentação própria.
- `.env`, artifacts, logs, outputs Parquet, estado Terraform e segredos são ignorados pelo Git.
- Veja [contratos](docs/contracts.md), [decisões](ADR.md), [runbook local](docs/runbook.md) e [runbook AWS](docs/aws-runbook.md).

## Infraestrutura AWS

Terraform declara ECR, ECS/Fargate, RDS privado, rede, IAM e Secrets Manager em `us-east-2`. Foi validado com `fmt -check`, `init -backend=false` e `validate`, sem `plan` nem provisionamento. Recursos podem gerar custos: deploy permanece fora do escopo executado e exige conferência de plano, créditos, duração, estimativa e autorização específica. O desenho não representa ambiente de produção nem alta disponibilidade.

## Evidência desta entrega

Ver [ANDAMENTO.md](ANDAMENTO.md) e [MEMORIA.md](MEMORIA.md). Na última validação, 26 testes unitários e lint/formatação passaram; integração vertical e batch passaram. A API local não respondeu durante a verificação final e o acesso ao Docker named pipe foi negado, então reliability, carga, integração Ollama e trace ponta a ponta ficaram pendentes. O workflow em `.github/workflows/ci.yml` foi criado, mas não executado no GitHub.
