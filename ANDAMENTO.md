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
- Databricks remoto: usuário informou `DATABRICKS_FIXTURE_OK: resultados iguais
  ao PySpark local` e `DATABRICKS_PARQUET_OK: reexecução idempotente` em 2026-10-02.
  Evidência informada pelo usuário; esta sessão não inspecionou o workspace remoto.
- Terraform 1.13.3: fmt/validate; imagem AWS construída localmente e na CI.
  Nenhum plan/apply nem recurso AWS criado.
- CI pública ampliada, execução 37021265817: lint, unidade, integração completa
  e builds das imagens aplicação/gateway passaram. Execuções posteriores devem
  ser conferidas no GitHub para o commit final.
- Commit `1169697` e tag `v0.1.0`: CI 37024332345 e 37024823542 concluídas com sucesso.
- Avaliação AWS concluída: arquitetura revisada e custos públicos
  calculados com Decimal: US$ 0,76 para cenário de quatro horas com reservas;
  premissas e pendências em `docs/aws-evaluation-2026-10-02.md`. Nenhum provisionamento.

## Limites e dependências externas

- Databricks remoto concluído conforme resultado informado pelo usuário; notebook
  reproduzível e passos permanecem em `docs/databricks.md`.
- AWS não provisionada; deploy depende de verificação financeira e autorização
  específica. A entrega local e declarativa não depende desse deploy.
- Antes do deploy: sanitização no comando ECS, administração isolada, versão
  PostgreSQL explícita, plugin/permissões ECS Exec, saúde da API e limpeza/backup.
  Conferência financeira pertence ao pre-flight local privado. Apresentação do
  portfólio após AWS.
- Configuração global Codex preservada com backup, TOML validado e raiz `.git`
  explícita adicionada; CLI nativo carregou. Políticas gerenciadas podem prevalecer,
  portanto não há garantia irrestrita de escrita em todas as sessões/perfis.
- Aviso de depreciação Starlette/AnyIO nos testes; não impede os resultados.
- Métricas de desempenho são do laboratório local, não SLO/benchmark de produção.
- Persistência de spend é assíncrona; o relatório mantém cobertura provisória e
  ausência de campos como nulos. Evidência batch não prova completude da fonte.

Evidências brutas locais estão em `.tools/` e `artifacts/`, ignorados pelo Git.
Comandos, decisões e acompanhamento: `docs/execution-2026-10-02.md`.
