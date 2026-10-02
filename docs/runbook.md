# Operação local e recuperação

## Preparação
No PowerShell, defina UV_PYTHON_INSTALL_DIR como .tools/python e UV_CACHE_DIR como .cache/uv. Execute uv python install 3.12, uv sync --frozen, uv run python -m scripts.init_env e docker compose up -d --build --wait --wait-timeout 300 db mock gateway api. Gere as chaves idempotentes: docker compose --profile admin run --rm admin.
O arquivo .env é local e ignorado pelo Git. A chave master fica somente em admin e gateway.

## Demo
Swagger em http://localhost:8000/docs. Alias local usa mock; fallback-demo falha no primário e retorna reserve. failure-demo e timeout-demo demonstram erro total e deadline artificial de 35s. /health/live não consulta dependências. /health/ready verifica gateway e banco sem inferência.

## Relatório
uv run python -m scripts.report --start 2026-10-01T00:00:00Z --end 2026-10-02T00:00:00Z. Os arquivos artifacts/usage.json e .csv são reconstruíveis e ignorados pelo Git. Intervalo UTC [início,fim). Persistência de logs é assíncrona; repita intervalos fechados. Campos e custos ausentes são nulos, custo zero é a política explícita de laboratório.

## Observabilidade
Execute uv run python -m scripts.prepare_observability e docker compose -f docker-compose.yml -f compose.observability.yml --profile observability up -d --build --wait --wait-timeout 300. Grafana :3000, Prometheus :9090 e Jaeger :16686 em localhost. O dashboard expõe volume, erros, p95, tokens, fallback e chamadas do gateway. Métricas do gateway/API têm labels allowlist; spans contêm modelo normalizado, status e tokens; logs omitem payload e URL.

## Ollama, batch e CI
Ollama precisa servir host.docker.internal:11434 com qwen3:4b e llama3.2:3b presentes. Aliases ollama e ollama-reserve. Execução mock de carga: uv run python -m scripts.load_test --duration 60 --concurrency 4. O script grava somente agregados em artifacts/load.json.
Batch: docker compose -f docker-compose.yml -f compose.batch.yml --profile batch run --rm batch. Validação com fixture: mesmo comando seguido do argumento /workspace/data/jobs/test_batch.py. O job grava Parquet em artifacts/daily. Notebook Databricks e fixture sintética existem; execução na conta ainda não foi feita. Cheque as cotas Free Edition antes de rodar.

## Parar, preservar e rollback
docker compose down preserva volume PostgreSQL; não use docker compose down -v se precisa dos registros. pg_dump salva backup local antes de migrations/recriação. Rollback: checkout do commit de imagem/config anterior, rebuild e verificação de health e consumo. A CI limpa apenas seu banco efêmero sintético após executar integração.
