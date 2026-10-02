# Andamento

Atualizado em 2026-10-02. Evidência local e CI verificadas nesta execução.
Repositório: https://github.com/marcosjcn94-bit/genai-platform-lab

## Validado

- 30 testes unitários e 6 integrações; Ruff lint/formatação passam.
- Docker acessível com execução autorizada. API live/ready, gateway, PostgreSQL
  e serviços de observabilidade saudáveis. API anterior estava em `Created`,
  aguardando gateway; não foi necessária correção do código da API.
- Duas aplicações autenticadas; consumo reconciliado pela identidade persistida
  da chave; bootstrap idempotente e acesso administrativo negado ao cliente.
- Fallback retorna reserva; falha total retorna 502; upstream lento é limitado;
  contadores reais confirmam teto de quatro tentativas. Timeout 504 coberto na unidade.
- Trace API/gateway correlacionado e labels Prometheus restritas. Inspeção adicional
  de 804 traces e logs API/gateway/mock sem marcadores de prompt ou segredos locais.
- Carga mock: 60 s, concorrência 4, 775 requisições, zero erros; p50 286 ms,
  p95 422 ms e máximo 1,902 s. Windows 11, i7-1255U, 12 threads, RAM 15,7 GiB.
- Ollama `qwen3:4b`: dez chamadas sem falhas; primeira 31,974 s, warm p50 5,464 s
  e p95 7,020 s. Reserva `llama3.2:3b` também respondeu pela API.
- 804 registros mantidos idênticos após reinício PostgreSQL/gateway e após rollback
  entre imagens distintas. Imagem atual restaurada e health/chat conferidos.
- PySpark 3.5.5: fixture com Decimal/nulos/deduplicação/Parquet idempotente;
  exportação real sanitizada com 804 registros e 7 grupos app/model reconciliada.
- Notebook Databricks único gerado do job canônico, compilado e transformação/
  assertions executadas no Spark local. Célula de Volume não executada localmente.
- Terraform 1.13.3: fmt/validate; imagem AWS construída localmente e na CI.
  Nenhum plan/apply nem recurso AWS criado.
- CI pública ampliada, execução 37021265817: lint, unidade, integração completa
  e builds das imagens aplicação/gateway passaram. Execuções posteriores devem
  ser conferidas no GitHub para o commit final.

## Limites e dependências externas

- Databricks remoto ainda não executado: sessão sem navegador conectado.
  Importar `data/databricks_demo.ipynb`; seguir `docs/databricks.md`.
- AWS não provisionada; deploy depende de verificação financeira e autorização
  específica. A entrega local e declarativa não depende desse deploy.
- Configuração global Codex preservada com backup, TOML validado e raiz `.git`
  explícita adicionada; CLI nativo carregou. Políticas gerenciadas podem prevalecer,
  portanto não há garantia irrestrita de escrita em todas as sessões/perfis.
- Aviso de depreciação Starlette/AnyIO nos testes; não impede os resultados.
- Métricas de desempenho são do laboratório local, não SLO/benchmark de produção.
- Persistência de spend é assíncrona; o relatório mantém cobertura provisória e
  ausência de campos como nulos. Evidência batch não prova completude da fonte.

Evidências brutas locais estão em `.tools/` e `artifacts/`, ignorados pelo Git.
Comandos, decisões e acompanhamento: `docs/execution-2026-10-02.md`.
