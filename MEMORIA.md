# Registro de execução

## 2026-10-02

- Continuação AWS: comando preserva logging sanitizado; health exige DB conectado
  e API ready; admin temporário separado da API; PostgreSQL 16.15, proteção de
  exclusão parametrizada e snapshot com run_id único. Três testes Terraform passam.
- Plano autenticado privado de preparação: 26 criações, zero alterações/exclusões;
  desired_count=0, digests fictícios. Não aplicar esse plano; nenhum recurso criado.
  Provider precisou de credenciais temporárias em memória, sem arquivo/terminal.
- Ensaio local da imagem AWS passou: DB/API ready, bootstrap no DB existente,
  chamada mock, canário/segredos ausentes dos logs e API sem master key. Não valida
  RDS/TLS. Containers temporários removidos; instalação do plugin ainda a confirmar.

- Fechamento Databricks: usuário informou `DATABRICKS_FIXTURE_OK` (equivalência
  local/remoto) e `DATABRICKS_PARQUET_OK` (reexecução idempotente). Não houve
  inspeção direta do workspace pelo Codex; o bloqueio remoto anterior foi resolvido.
- CI do commit `1169697` e tag `v0.1.0` passou. Usuário pediu fechamento da
  documentação e avaliação AWS, mantendo apresentação do portfólio para depois.
- `1.md` deve ser ignorado, conforme orientação direta do usuário.
- Avaliação AWS: dados de autenticação, estado financeiro, quotas e inventário
  ficam no pre-flight privado local ignorado pelo Git. O relatório público
  documenta arquitetura, preços públicos e preparação anterior ao deploy.
- Custos regionais públicos obtidos por Bulk Price List; cálculo Decimal e JSON
  versionado. Cenário quatro horas + reservas: US$ 0,764761, sem descontar créditos.
- Revisão revelou comando ECS omitindo log_config sanitizado, administração
  temporária ainda sem artefato, PostgreSQL major não fixado (padrão consultado
  variável), plugin Session Manager ausente e sequência de limpeza pendente.
  Terraform fmt/validate passaram; nenhuma infraestrutura foi modificada.
- Coleta privada sanitizada por allowlist; identificadores não incluídos no Git.

- Plano aprovado e repositório público informado: https://github.com/marcosjcn94-bit/genai-platform-lab.
- `docker compose ps --all` é o comando correto; `--al` não existe.
- Docker funcionou fora da restrição da sessão. API em `Created` aguardava gateway;
  build/start/health e bootstrap recuperaram a stack sem correção da API.
- Configuração global Codex tinha tabelas inline OTel multilinha incompatíveis com
  TOML 1.0. Backup feito, formatação normalizada preservando valores, raiz explícita
  `.git` adicionada e `codex features list` passou. Não substitui política gerenciada.
- 30 unitários, 6 integrações, lint/formatação; fallback/deadlines/traces reais passaram.
- Benchmark Ollama: p95 incorreto e falhas misturadas às latências corrigidos com
  4 testes RED->GREEN. Dez chamadas primárias sem falha; reserva também validada.
- Carga mock: 775 chamadas/60 s/concorrência 4, zero erros, p95 422 ms.
- Persistência/rollback: 804 eventos idênticos preservados. Parquet real reconciliou
  804 eventos/7 grupos; fixture e idempotência PySpark passaram novamente.
- Notebook único gerado e executado parcialmente no Spark local. `createDataFrame`
  exige float para DoubleType, ao contrário da leitura JSON que converte inteiros.
  Adaptador da fixture corrigido; Databricks remoto pendente por falta de navegador.
- CI pública 37021265817 passou os cinco jobs; imagem AWS validada sem provisionamento.
- Privacidade: 804 traces e logs do runtime sem marcadores sensíveis. Valores reais
  dos segredos locais ausentes das 324 revisões de arquivos dos 7 commits inspecionados.
- Valores de carga/Ollama são observações desta máquina; não resultados de produção.

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
