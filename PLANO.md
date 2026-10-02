Planejamento recomendado: genai-platform-lab

# MVP local e custo zero
- LiteLLM Proxy como gateway, com duas rotas de modelo local via Ollama, usando modelos que você já demonstrou no Prompt Evaluation Lab.
- Fallback, timeout e retries limitados, com uma falha simulada reproduzível.
- PostgreSQL do gateway como persistência de usage/spend; um relatório de consumo por aplicação.
- FastAPI pequena para identificar app_id e encaminhar requests ao gateway.
- Prometheus, Grafana e OpenTelemetry para latência, erros, painel e traces.
- Docker Compose para subir a demo localmente.
- GitHub Actions para lint, testes e build da imagem.
- Teste de carga curto contra modelos locais ou mock.
- Terraform para definir a infra AWS e validar configuração sem provisionar por padrão.
- Projeto AWS gratuito já criado; região selecionada: `us-east-2`. Conferir plano, saldo de créditos, serviços permitidos e custo previsto antes de qualquer provisionamento.
- Runbook de release e rollback.
- Conta Databricks Free Edition já criada; incluir avaliação prática após o batch PySpark local.
LiteLLM já oferece gateway, logging/cost tracking e roteamento com retries/fallbacks, evitando criar outro gateway ou um segundo ledger. Documentação oficial LiteLLM, arquitetura do proxy, roteamento.

# Extensões
- PySpark: recomendado após o MVP. A vaga cita Spark/Lakehouse. Um único job batch local que lê eventos sintéticos, agrega tokens, custo estimado, latência e erros por aplicação/dia/modelo e grava Parquet é evidência suficiente para o escopo inicial. API PySpark Structured Streaming
- AWS deploy real: requisito condicionado ao custo. ECS/Fargate, RDS e rede consomem créditos. Permanecer no plano gratuito e jamais exceder seus créditos; sem margem comprovada, entregar Terraform validado e demo local. Deploy temporário exige autorização explícita para essa execução, estimativa, monitoramento e destruição.

Manter app_id no relatório de consumo e fora das labels de Prometheus; labels por usuário/aplicação podem gerar cardinalidade alta. Boas práticas do Prometheus, nomenclatura e cardinalidade. Instrumentar FastAPI e requests com OpenTelemetry; excluir prompts, PII e segredos dos traces. Docs Python do OpenTelemetry.

# MCPs, tools, hooks e skills
- Context7 MCP: consultar documentação atual de LiteLLM, FastAPI, OTel e Spark durante a implementação. O ambiente desta sessão tem acesso a ele.
- GitHub MCP ou gh: útil para issues/PR e releases, mas não é necessário para o MVP; GitHub Actions já atende CI.
- Docker Compose, pytest/unittest, Ruff, Terraform CLI e k6: tools suficientes para build/run, validação, testes e carga. A escolha entre k6 e ferramenta menor deve ser feita na implementação conforme o ambiente local.
- Skills do Codex: TDD e debugging sistemático na implementação; verificação antes de declarar pronto; execução paralela apenas para tarefas independentes.
- Hooks: não recomendo hook customizado inicialmente. Lint/format como comandos explícitos e CI são mais simples de explicar e depurar. Adicionar pre-commit só se o ciclo local demonstrar valor.

# Estrutura e AGENTS.md
Estrutura pequena, com preferência por arquivos de autoria manual abaixo de 250 linhas:

genai-platform-lab/
├── app/                 # main.py, schemas.py, gateway_client.py, telemetry.py
├── litellm/config.yaml
├── observability/       # prometheus.yml e provisionamento do Grafana
├── data/                # eventos sintéticos e jobs/aggregate_usage.py
├── infra/terraform/     # main.tf, variables.tf, outputs.tf, iam.tf
├── tests/{unit,integration,fixtures}/
├── scripts/load_test.js
├── .github/workflows/ci.yml
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── .env.example
├── README.md
└── AGENTS.md

# AGENTS.md (criado; revisar durante a implementação)
# Objetivo
Demonstrar engenharia de plataforma GenAI alinhada à vaga da Experian,
com foco em gateway, metering, observabilidade e confiabilidade.

# Produto final
Demo local reproduzível com LiteLLM, duas rotas Ollama, fallback limitado,
FastAPI fina, PostgreSQL, Prometheus, Grafana, OpenTelemetry e CI.
PySpark batch e Terraform são extensões. AWS deploy depende de créditos
ou orçamento aprovado no escopo futuro.

# Stack e arquitetura
LiteLLM é a autoridade de usage/spend; não criar ledger paralelo.
FastAPI encaminha e identifica app_id. PostgreSQL persiste usage.
Prometheus guarda métricas operacionais de baixa cardinalidade.
Não adicionar RAG, embeddings ou vector DB: já são competências demonstradas.

# Economia de tokens e FinOps
Padrão local com Ollama/mock. Chamadas remotas e carga limitada são opt-in.
Definir max tokens, timeout e retries finitos.
Nunca executar terraform apply, criar recursos AWS ou ativar serviço pago
sem autorização explícita para essa execução.

# Convenções
Arquivos manuais preferencialmente com até 250 linhas.
Segredos somente em ambiente local, nunca em Git ou traces.
Documentar setup e comandos no README.

# Workflow dos agentes
Ler este arquivo e os contratos antes de editar.
Paralelizar apenas arquivos independentes; evitar edição simultânea
da config LiteLLM, contrato FastAPI e metering.
O coordenador integra, revisa e executa os critérios de validação.

# Validação
Testes unitários e integração local; carga curta contra Ollama/mock.
Validar Terraform com fmt/validate sem provisionar por padrão.
Distinguir resultados locais, configuração validada e deploy AWS real.

# testes
Gateway: requisição válida obtém resposta; modelo inexistente retorna erro compreensível.
Fallback: primário simulado com timeout/5xx e secundário saudável; resultado registra modelo final; chamadas respeitam o teto de retry.
Timeout: upstream lento não mantém a API pendurada indefinidamente.
Metering: tokens e custo do registro de exemplo ficam atribuídos à aplicação correta e reconciliam com o uso do gateway.
Persistência: parar/reiniciar Compose não apaga os registros de uso.
API: valida payload, retorna códigos apropriados e não expõe credenciais nem mensagens internas de upstream.
Observabilidade: métricas cobrem requests, erros e latência; traces não contêm prompt, conteúdo pessoal, authorization header ou chaves.
Cardinalidade: app_id, usuário e chave não são labels de métricas; atribuição por app é feita no relatório de consumo.
Health: readiness identifica dependências indisponíveis; liveness não faz inferência.
CI: lint, testes de unidade, integração local e build da imagem são etapas separadas e reprodutíveis.
Carga: executar cenário curto contra provedor local/mock, guardar comando e resultados; definir p95 e taxa de erro como medidas observadas, sem inventar SLO de produção.
Terraform: fmt, validate e revisão de plano; por padrão, sem apply.
Rollback: voltar a uma imagem/configuração anterior, obter health saudável e demonstrar como os registros de uso permanecem no banco.

# Retries/fallback: LiteLLM controla política central; timeout por chamada e poucos retries com backoff. Evitar retry simultâneo na FastAPI para não multiplicar tentativas e custo.
Health checks: liveness simples; readiness verifica banco/gateway sem gerar inferência.
Tracing: instrumentar FastAPI e HTTP; propagar trace ID; sanitizar headers e excluir conteúdo de prompts. OTel: sanitização de headers
Métricas: requests, respostas com erro, latência por rota/modelo, tokens agregados e fallback count. Evitar labels de alta cardinalidade. LiteLLM também expõe métricas de gateway/uso; conferir configuração oficial atual antes de fixar os nomes no dashboard. Métricas do LiteLLM
Metering: app_id passa como dimensão de atribuição do gateway; PostgreSQL registra spend/usage conforme LiteLLM. Relatório agrupa período, aplicação e modelo. Não chamar custo estimado local de fatura real: separar tokens medidos, preço de tabela e custo faturado, se disponível.
Testes de carga: script mínimo em modo local, modelo mock/local e duração baixa. Reportar cenário, máquina e resultado para que números não pareçam benchmark de produção.
Rollback: tag de imagem anterior, configuração versionada e passo de health check; em deploy temporário, documentar destruir infraestrutura e confirmar ausência de recursos ativos.

# commits automáticos a cada final de tarefa

# não fazer testes desnecessários

# presar pela velocidade de execução do projeto

# criar ADR.md na raiz do projeto para registrar as decisões arquiteturais mais relevantes. breve resumo do motivo da escolha

# criar MEMORIA.md na raiz do projeto para registrar o que foi aprendido durante a execução do projeto

# deixar para criar o README.md apenas no final do projeto

# Plano de execução no Codex — atualizado em 2026-10-01

## Resultado esperado

Demonstrar gateway, autenticação por aplicação, consumo atribuído, fallback, métricas, traces, processamento PySpark e infraestrutura declarativa. O texto da vaga não está disponível; este arquivo define o escopo. Evidências devem distinguir execução local, configuração AWS validada e eventual deploy real. No planejamento inicial, Git ainda não estava inicializado; o estado atual está em `ANDAMENTO.md`.

O ambiente inspecionado tem 16 GB de RAM, GPU Intel Iris Xe e modelos Ollama `qwen3:4b`, `llama3.2:3b`, `qwen2.5-coder:7b`, `qwen2.5:1.5b` e `qwen2.5:3b`. Usar `qwen3:4b` e `llama3.2:3b` como candidatos inicial e reserva, fixando a escolha após uma medição curta. Docker Desktop está instalado, mas o daemon estava parado. Mock determinístico cobre CI e falhas reproduzíveis.

## Decisões de arquitetura a provar cedo

- **Identidade:** criar uma chave virtual LiteLLM por aplicação. FastAPI autentica o cliente e deriva `app_id` da credencial; não confiar em `app_id` informado pelo cliente. Ela seleciona a chave interna correspondente. A master key permanece no servidor. Fazer uma fatia vertical com uma aplicação, uma chamada e um registro atribuído antes de ampliar. [Chaves virtuais](https://docs.litellm.ai/docs/proxy/virtual_keys).
- **Medição:** LiteLLM/PostgreSQL são a fonte de usage/spend. Relatório usa logs paginados e relaciona chave/equipe à aplicação. Não depender de metadados personalizados de spend logs, recurso Enterprise. Não criar segundo ledger. Em Ollama local, mostrar tokens e requisições; custo faturado de API é zero. Qualquer preço hipotético precisa de rótulo separado. [Spend tracking](https://docs.litellm.ai/docs/proxy/cost_tracking).
- **Confiabilidade:** LiteLLM controla timeout, retries finitos com backoff e fallback primário -> secundário. FastAPI não faz outro retry. Fixar teto de tentativas e `max_tokens`; provar o modelo que atendeu e o número de tentativas com falha simulada. [Roteamento](https://docs.litellm.ai/docs/routing).
- **API e segurança:** endpoint de chat com schema pequeno, limite de payload, autenticação por aplicação e erros 4xx/502/504 sem segredos ou mensagens internas. Liveness não infere; readiness verifica dependências sem chamar modelo. `.env.example` não contém valores reais; segredos ficam fora do Git.
- **Observabilidade:** Prometheus/Grafana para métricas; acrescentar Jaeger local como destino OTLP dos traces OpenTelemetry. Propagar `traceparent`; não enviar prompt, resposta, PII, Authorization ou chaves a spans/logs. Não usar `app_id`, usuário ou chave como label Prometheus. Conferir nomes reais das métricas antes de fixar dashboard. Jaeger local tem retenção temporária. [LiteLLM OTel](https://docs.litellm.ai/docs/proxy/logging), [Jaeger](https://www.jaegertracing.io/docs/2.21/getting-started/).
- **Infraestrutura AWS:** Terraform descreve uma demo mínima com provedor mock; Ollama no host Windows não fica automaticamente acessível na AWS. Recursos regionais do projeto ficam em `us-east-2`. Não prometer paridade operacional com o Compose se a nuvem usar mock.

## Etapas e paralelismo

Cada tarefa termina com evidência curta e commit próprio. O coordenador faz os commits em série para evitar disputa no índice Git. Limitar agentes paralelos a 2–3 fluxos com arquivos independentes e contexto restrito a contratos e arquivos relevantes.

| Etapa | Entrega verificável | Dependência e paralelismo |
| --- | --- | --- |
| 0. Fundação | Inicializar Git; revisar `AGENTS.md`; criar `ADR.md`, `MEMORIA.md`, `.gitignore`, estrutura mínima, contratos de API/identidade/eventos e versões fixas; verificar Docker/Ollama. | Sequencial: define interfaces. |
| 1. Fatia vertical | Compose com PostgreSQL/LiteLLM, rota Ollama e mock, chave virtual, uma chamada e log atribuído. | Sequencial: valida a hipótese de medição gratuita. |
| 2. Núcleo | Segunda aplicação, FastAPI autenticada, relatório por período/app/modelo, fallback e erros seguros. | Gateway, contrato da API e metering têm um responsável único. |
| 3. Visibilidade e CI | Prometheus/Grafana/Jaeger/OTel; testes de unidade e integração com mock; GitHub Actions para lint, testes e build separados. | Observabilidade e CI em paralelo após contrato da etapa 1. |
| 4. Demo local | Integração Ollama, persistência após reinício, carga curta, release/rollback e resultados observados. | Script de carga e runbook em paralelo; integração pelo coordenador. |
| 5. PySpark | Exportação derivada dos logs sem segundo ledger, fixture sintética, agregação dia/app/modelo de tokens, erros, latência e custo registrado; Parquet e reconciliação. | Paralelo ao Terraform após estabilizar schema. |
| 6. Terraform | Infra AWS mínima com mock, IAM mínimo, variáveis, outputs, estimativa e destruição; `fmt`, `init -backend=false`, `validate`. | Paralelo ao PySpark; `plan` só com perfil e contexto válidos. |
| 7. Databricks | Avaliar cotas da Free Edition; executar a mesma amostra sintética em notebook/job se permitido; comparar agregados com PySpark local. | Pode iniciar junto às etapas 5–6; usuário faz login se necessário. |
| 8. Entrega | Revisar ADR/MEMORIA; escrever README somente agora, com setup Windows, demo de 3–5 minutos, evidências reais, CI, runbook e limites. | Após integração final. |

## Agent Toolkit for AWS

Seguir o [setup oficial](https://raw.githubusercontent.com/aws/agent-toolkit-for-aws/refs/heads/main/setup-instructions/setup.md), verificando sua versão na execução. Região selecionada do projeto: `us-east-2`; perfil AWS CLI escolhido: `marcosjcn94`. Não guardar URL com login, e-mail, identificador de conta ou credenciais no Git.

1. Verificar/instalar AWS CLI v2 e `uv` de origem oficial, inspecionando os instaladores. Ambos estavam ausentes do PATH em 2026-10-01; o terminal desta sessão não alcançou os instaladores, então reavaliar conexão. Preservar configurações existentes.
2. Configurar `aws configure set region us-east-2 --profile marcosjcn94`; executar `aws login --region us-east-2 --profile marcosjcn94`. Usuário autentica no navegador, sem enviar chaves ou senhas ao Codex. Segundo o guia, as credenciais valem 12 horas e podem ser renovadas por até 90 dias sem novo login no navegador.
3. Verificar `aws sts get-caller-identity --profile marcosjcn94` sem registrar identificadores completos no Git.
4. Executar assistente interativo `aws configure agent-toolkit --yes --region us-east-1 --profile marcosjcn94`. `us-east-1` é a região do serviço Agent Toolkit, não dos recursos do projeto.
5. Fazer backup antes de alterar configuração global do Codex. Na entrada `aws-mcp` criada pelo assistente, adicionar somente `AWS_MCP_PROXY_PROFILES=marcosjcn94`, mantendo comando, argumentos, transporte e outros MCPs. Se já existir `aws-mcp`, reconciliar antes de editar. Verificar catálogo com `aws agent-toolkit list-available-skills --region us-east-1 --profile marcosjcn94` e testar uma ferramenta em sessão nova.
6. As [regras da nova experiência AWS](https://raw.githubusercontent.com/aws/agent-toolkit-for-aws/refs/heads/main/rules/aws-starter-rules.md) já estão em bloco delimitado no `AGENTS.md`, preservando instruções do projeto. Conferir atualização dessas regras quando o toolkit estiver instalado. Não criar recursos regionais fora de `us-east-2`.

## Limite financeiro e ações humanas

- Permanecer no plano gratuito do projeto AWS. Antes de provisionar, conferir `aws freetier get-account-plan-state`, saldo e validade de créditos, serviços permitidos, estimativa de **todos** os recursos e limite de gastos em AWS Settings. ECS, RDS e serviços relacionados aparecem na [lista de serviços da nova experiência gratuita](https://docs.aws.amazon.com/accounts/latest/reference/supported-services-sign-up-new.html), mas podem consumir créditos.
- `terraform fmt` e `validate` não criam recursos. Sem margem comprovada dentro dos créditos gratuitos, entregar Terraform validado e demo local. Nunca executar `apply`, criar recursos ou ativar plano pago sem autorização explícita para a execução concreta. Deploy autorizado deve ter duração curta, monitoramento, `destroy` e verificação de recursos/custos remanescentes.
- Usuário intervém apenas no login AWS do navegador, no assistente interativo, em eventual login Databricks e na autorização de deploy real após revisar estimativa/saldo. Codex prepara artefatos e evidências antes de pedir decisão.

## Validação enxuta adicional

- Duas aplicações isoladas: credencial ausente/inválida e `app_id` falsificado não acessam uso alheio.
- Fallback registra modelo atendente e teto de tentativas; timeout lento não deixa a API pendurada.
- Traces e logs inspecionados quanto a prompt, PII e segredos; sem labels de alta cardinalidade.
- CI usa mock; Ollama real fica no teste local. Carga registra cenário, hardware, comando, p95 e taxa de erro observados, sem SLO inventado.
- Batch PySpark determinístico confere com amostra derivada/sintética. Databricks, se acessível, produz a mesma agregação; suas cotas não são garantia de execução contínua. [Limitações da Free Edition](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations).
- Terraform: `fmt`, `init -backend=false` e `validate`; `plan` quando possível. Validação estática não equivale a deploy. Rollback retorna imagem/configuração anterior sem perder logs PostgreSQL. [Terraform validate](https://developer.hashicorp.com/terraform/cli/commands/validate).






