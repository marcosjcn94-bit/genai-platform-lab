# Conclusão do GenAI Platform Lab

Plano aprovado em 2026-10-02; execução na branch `implementation` a partir de `fc9ccf1`.
Repositório público: https://github.com/marcosjcn94-bit/genai-platform-lab

## Critérios

- [x] Stack local e acesso Git/Docker recuperados; segredos e PostgreSQL preservados.
- [x] API, identidade, consumo e persistência após reinício validados.
- [x] Fallback, falha total e deadlines com tentativas limitadas comprovados.
- [x] Traces correlacionados e telemetria sem conteúdo sensível comprovados.
- [x] Carga mock de 60 s/concorrência 4 e Ollama medidos.
- [x] Fixture e exportação sanitizada reconciliadas no PySpark.
- [x] Databricks: equivalência da fixture e Parquet idempotente confirmados pelo usuário.
- [x] Terraform/imagem AWS validados sem provisionamento; CI pública verde.
- [x] Recuperação/rollback demonstrados e documentação atualizada para publicação.

## Registro

- Pre-flight: API e testes consomem os contratos HTTP/exportação v1 existentes;
  CI precisa da observabilidade antes de executar o teste de traces.
- Decisão: manter a branch de implementação existente e os volumes da demo;
  outro worktree não resolve o acesso ao Docker e dividiria a evidência de runtime.
- Docker acessível fora do sandbox; serviços antigos parados e API em `Created`.
- Baseline: `uv run --frozen pytest -q`: 26 passed, 6 deselected;
  aviso de depreciação do Starlette/AnyIO registrado, sem alteração de dependências.
- Ollama HTTP respondeu; `qwen3:4b` e `llama3.2:3b` disponíveis.
- GitHub público já contém `fc9ccf1`; publicar somente por fast-forward.
- AWS continua sem autorização de provisionamento.
- Stack/identidades recuperadas: API live/ready 200; gateway e PostgreSQL saudáveis.
- Configuração global Codex: backup feito, tabelas inline OTel normalizadas sem
  mudar valores, TOML validado e raiz `.git` explícita adicionada. CLI 0.160.0
  carrega; a política gerenciada desta sessão continua exigindo execução autorizada.
- Integração: 6 passed (API/gateway, vertical, três cenários de confiabilidade,
  traces/métricas). Reexecução direta também passou em 132,66 s.
- Benchmark: regressão RED (4 falhas) -> GREEN (30 testes unitários); p95 por
  nearest rank e somente respostas do modelo primário entram nas latências.
- Ollama primário: 10 chamadas, zero falhas; primeira 31,974 s; warm p50 5,464 s,
  warm p95 7,020 s. Benchmark local, sem SLO de produção.
- PySpark fixture: BATCH_OK; Terraform fmt/validate passam; imagem AWS construída
  localmente. Nenhum recurso AWS criado.
- Databricks: inventário de automação não expõe navegador/sessão. Preparar notebook
  único com fixture incorporada; execução Free Edition depende do login do usuário.
- Carga: 775 requisições/60 s/concorrência 4, zero erros, p95 0,421923 s.
- Reserva Ollama via API: `llama3.2:3b`, 31 tokens na chamada sintética.
- Persistência: 804 registros idênticos após reiniciar banco/gateway.
- Batch real: 804 registros e 7 grupos app/model reconciliados com o relatório.
- Rollback: duas imagens distintas, live/ready/chat saudáveis, 804 registros
  preservados; imagem atual restaurada.
- Notebook local: primeira execução revelou `DoubleType` rejeitando duração inteira;
  converter duração para float no adaptador da fixture, sem mudar a transformação.
  Reexecução passou: NOTEBOOK_LOCAL_OK. Célula de Volume depende do Databricks.
- CI `37021265817`: cinco jobs verdes, incluindo integração completa e duas imagens.
- Configuração global também carregou via `codex features list`; não foi feita
  inferência em subprocesso Codex nem alterado o perfil gerenciado da sessão atual.
- Privacidade: 804 traces e logs examinados; segredos locais e canários verificados
  ausentes. Esta verificação não substitui auditoria completa de segurança.
- Revisão independente final não identificou problemas críticos, importantes ou
  menores. Notebook remoto/Volume seguem pendentes; primeira chamada Ollama não
  comprova carregamento a frio controlado.
- Databricks: importar `data/databricks_demo.ipynb` e executar conforme
  `docs/databricks.md`; sem navegador autenticado disponível, execução remota bloqueada.
- Verificação final: 30 unidades passam; Ruff/sintaxe JSON/YAML passam; arquivos
  versionados sem os segredos locais verificados. Grafana serve seis painéis e
  Prometheus aceita suas seis consultas. Publicação mantém a branch `implementation`.
- Fechamento: commit `1169697`, tag `v0.1.0`; ambas as CI passaram (37024332345,
  37024823542). Usuário confirmou os dois marcadores Databricks em 2026-10-02,
  encerrando o bloqueio remoto registrado anteriormente.
- Nova orientação: ignorar `1.md`; avaliar AWS sem provisionar. Apresentação do
  portfólio somente após a etapa AWS.
- Avaliação concluída: `docs/aws-evaluation-2026-10-02.md` e JSON de custos.
  Dados do pre-flight financeiro/inventário ficam fora do Git; Terraform
  fmt/validate passam. Preparação do deploy segue pendente; nenhum recurso criado.

- Continuação: testes nativos Terraform demonstraram RED nos contratos de logging,
  readiness, admin, versão DB e proteção/snapshot. Correção mínima: três cenários
  GREEN com provider simulado; fmt/validate passam. CI ganhou job Terraform.
- Plano autenticado privado passou: 26 criações, zero alterações/exclusões; task
  zero, digests fictícios. Não aplicar o plano. Sessão AWS CLI traduzida para
  credenciais temporárias somente na memória do processo; nenhum recurso criado.
- Decisão: admin temporário na mesma task evita segunda task; timeout não substitui
  redeploy sem admin. Readiness/TLS e limpeza reais continuam gates da execução AWS.
- Imagem AWS local: comandos ECS e gateway config AWS executados com API/admin
  temporários; DB conectado, API ready, bootstrap idempotente no banco local
  existente e chamada mock passaram. Logs sem canário e segredos locais verificados;
  master key ausente da API. Containers de teste removidos. PostgreSQL local sem
  TLS não comprova migrations/TLS no RDS nem tempo de inicialização no Fargate.
- Revisão independente final do diff desta preparação: nenhum defeito crítico,
  importante ou menor confirmado. Não adicionar timeout de dependência ECS sem
  evidência; validar startup e ECS Exec na execução real autorizada.

## Demo AWS autorizada e encerrada

- Usuário confirmou Session Manager, validade de créditos e demo de até quatro
  horas. Plano gratuito, margem financeira, região, quota e PostgreSQL conferidos.
- ECR criado antes do plano completo; imagens reais por digest publicadas. Plano
  antigo não aplicado. Provisionamento manteve task zero até instalar segredo runtime.
- Fargate HEALTHY e ECS Exec; RDS 16.15/TLS 1.3; bootstrap duas vezes; autenticação,
  duas aplicações, fallback de três tentativas e falha limitada a quatro passaram.
- Quatro registros exportados em JSON/CSV; três sucessos reconciliados por app/ID
  e tokens. Admin removido por redeploy; os quatro registros permaneceram no RDS.
- Inspeção de 585 eventos CloudWatch sem canário e segredos verificados. Credenciais
  AWS usadas em memória; autenticação Docker temporária removida; configuração
  global e dependências da aplicação preservadas.
- Execução 17:48–18:26 UTC, aproximadamente 38 minutos. Serviço zerado, ECR esvaziado,
  proteção de exclusão desabilitada e destroy de 25 recursos com snapshot obrigatório.
  Estado Terraform vazio; inventário direto conferiu ausência de infraestrutura ativa.
- Snapshot final criado disponível/criptografado e depois excluído com autorização
  específica do usuário. Conferência às 18:52 UTC confirmou zero snapshot final,
  backups automáticos e bancos da demo; relatórios locais preservados.
  Segredo runtime em recuperação; faturamento ainda não consolidado.
  [Relatório](aws-demo-2026-10-02.md).
