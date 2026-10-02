# Andamento

Atualizado em 2026-10-01. Este arquivo registra o que foi executado e os limites ainda abertos.

## Validado

- 26 testes unitários passam; Ruff lint e formatação passam.
- Integração vertical LiteLLM/PostgreSQL/mock: uma chamada sintética persistida, 12 tokens, custo de laboratório zero e identidade da chave reconciliada por hash. Bootstrap idempotente e endpoint administrativo negado ao cliente.
- Integração API + gateway com duas aplicações e fallback: passou anteriormente nesta execução; repetir após a correção mais recente do health check.
- PySpark 3.5.5 executado em container: totais conhecidos, Decimal, nulos, deduplicação e reexecução Parquet passaram com fixture sintética.
- Terraform 1.13.3: `fmt -check`, `init -backend=false` e `validate` passam; nenhum `plan`, `apply` ou recurso AWS foi criado.
- Gateway, readiness do banco, Prometheus, Jaeger, Grafana e Ollama responderam localmente nesta sessão.

## Pendente / bloqueado

- A porta local da FastAPI (8000) não responde nesta sessão. O gateway responde; acesso ao Docker named pipe foi negado ao processo, impedindo ler logs e inspecionar o health do container. Portanto não foram repetidos agora integração API, cenários de confiabilidade, carga de 60 s ou teste ponta a ponta de OTel.
- Integração Ollama por meio da API e benchmark sequencial de dez chamadas não executados.
- Databricks: notebook e fixture prontos; execução não verificada.
- AWS: somente Terraform validado estaticamente; nenhum deploy. Qualquer deploy requer conferência financeira e autorização explícita.
- GitHub Actions: workflow criado; execução remota não verificada.
