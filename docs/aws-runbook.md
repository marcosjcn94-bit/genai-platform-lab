# AWS: demo temporária validada e encerrada

Estado em 2026-10-02: demo autorizada executada e 25 recursos Terraform removidos;
snapshot final excluído com autorização específica e segredo runtime em recuperação por sete dias.
Evidências, duração e custo residual: [execução real](aws-demo-2026-10-02.md).
As etapas abaixo orientam uma nova execução, sujeita a nova autorização concreta.
Avaliação realizada: [custos, pendências e próxima execução](aws-evaluation-2026-10-02.md).
Dados de plano/inventário são privados e ficam fora do Git.
Região fixa us-east-2. Uma task Fargate com mock, sem API pública, sem NAT/ALB.
RDS privado single-AZ exige subnet group em duas AZs; isso não habilita Multi-AZ.
ECS Exec exige filesystem gravável, Session Manager plugin e permissão do operador.
A task possui apenas canais ssmmessages; execução possui ECR/logs/segredo específico.
Wildcards nos canais SSM e ECR authorization são necessários pelo serviço.
Sessões Exec não gravam conteúdo; CloudTrail registra a chamada administrativa.

## Gate financeiro obrigatório
Autorização desta demo e da exclusão de seu snapshot já atendida. Para futuras
execuções, `AGENTS.md` e `PLANO.md` exigem autorização concreta antes de apply,
criação de recursos ou ativação de plano pago, com saldo/plano/estimativa conferidos.
Publicação de imagens e instalação de segredos integram o escopo do deploy autorizado.
Exclusão de snapshot exige autorização específica, conforme a limpeza abaixo.
Preparação local, testes, documentação e preparação da apresentação não têm
exigência adicional de autorização nesses arquivos.

Conferir AWS Settings > View all projects > Overview > Additional Info > Region.
Conferir Billing: FREE/PAID, créditos restantes, validade e limite de gastos.
Conferir serviços permitidos e estimar para a duração concreta:
Fargate 1 vCPU/3 GB, RDS db.t4g.micro + 20 GB gp3 + backups,
IPv4 público por hora, ECR armazenamento, Secrets Manager (runtime + senha RDS),
CloudWatch ingestão/retenção, tráfego de saída e snapshots remanescentes.
Sem saldo, duração e preços atuais confirmados, a estimativa está pendente.
Não executar apply, publicar imagens ou povoar segredos sem autorização concreta.
Plano privado de preparação: 26 criações, zero alterações/exclusões, task zero e
digests fictícios. Não aplicar esse arquivo. Regenerar/revisar na execução
autorizada; plan não comprova permissões de criação.

## Preparação local

```powershell
.tools/terraform/terraform.exe -chdir=infra/terraform fmt -check -recursive
.tools/terraform/terraform.exe -chdir=infra/terraform validate
.tools/terraform/terraform.exe -chdir=infra/terraform test -no-color
& "$env:ProgramFiles/Amazon/SessionManagerPlugin/bin/session-manager-plugin.exe" --version
```

Testes usam provider simulado, inclusive `command=apply`; não criam recursos.
Plugin exige administrador: [instalação AWS](https://docs.aws.amazon.com/systems-manager/latest/userguide/install-plugin-windows.html).
Provider 6.14.1 não reconheceu diretamente a sessão `aws login` neste ambiente;
usar credenciais temporárias capturadas em memória ou perfil separado com
`credential_process`, conforme [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html).
Não imprimir exportação de credenciais nem gravá-la em arquivo.
Plan, state, tfvars, identificadores e logs privados permanecem fora do Git.

## Sequência após autorização concreta
1. Resolver as pendências da avaliação; revisar plan, custos e horário de destruição; manter desired_count=0 inicialmente. Isso não impede cobrança do RDS e armazenamento após criação.
2. Criar recursos autorizados; construir `application` com o `Dockerfile` da raiz e `gateway` com `docker build -f litellm/Dockerfile.aws -t <tag> .`; publicar ambas por digest no ECR. A imagem AWS inclui config local de rede para o mock e instrumentação sanitizada.
3. Fora do Terraform, preencher segredo JSON runtime com DATABASE_URL (TLS requerido),
   LITELLM_MASTER_KEY, APP_A_TOKEN/B_TOKEN, APP_A_GATEWAY_KEY/B_GATEWAY_KEY e METRICS_TOKEN.
   Senha RDS é gerenciada pelo serviço; não copiar para Git/terminal/log.
4. Atualizar digests reais, `desired_count=1` e `enable_admin=true`; revisar plan
   e aplicar somente dentro da autorização. Aguardar gateway com DB conectado e
   API ready. PostgreSQL fixado em 16.15; reconferir disponibilidade no dia.
5. Executar bootstrap administrativo de forma temporária e interna, removendo o
   acesso administrativo ao master key após execução. API nunca recebe master key.
   Admin é container opcional na mesma task; processo expira em uma hora, mas
   isso não remove a referência ao segredo da definição. Redeploy obrigatório
   com `enable_admin=false`; esperar task anterior parar e confirmar remoção.
6. ECS Exec no API: health, duas chamadas sintéticas e exportação administrativa
   isolada. Não colar segredos em argumentos ou conteúdo de sessão.
   Para exportar, habilitar admin temporariamente, obter a nova task e desabilitar
   depois. Exemplo PowerShell após deploy autorizado:

   ```powershell
   $taskArn = aws ecs list-tasks --profile marcosjcn94 --region us-east-2 --cluster genai-platform-lab --service-name genai-platform-lab --query 'taskArns[0]' --output text
   aws ecs execute-command --profile marcosjcn94 --region us-east-2 --cluster genai-platform-lab --task $taskArn --container admin --interactive --command 'python -m scripts.bootstrap'
   aws ecs execute-command --profile marcosjcn94 --region us-east-2 --cluster genai-platform-lab --task $taskArn --container admin --interactive --command 'python -m scripts.report --start 2026-10-02T00:00:00Z --end 2026-10-03T00:00:00Z --output /tmp/usage'
   ```

   Substituir intervalo pelos limites UTC da execução e aguardar spend assíncrono.
   Recuperar JSON/CSV de `/tmp` antes de parar a task; guardar somente em artefatos
   locais ignorados pelo Git. Gateway mantém sua master key necessária ao serviço.
7. Monitorar custos. Antes de destruir: exportar evidência sanitizada e backup aprovado.
   Aplicar `deletion_protection=false` antes do destroy autorizado; snapshot final
   permanece obrigatório. Manter `run_id` único (6–20 alfanuméricos minúsculos)
   durante toda a execução; sufixo evita colisões entre demos.
   Esvaziar ECR somente após confirmar os digests; destruir recursos autorizados.
   Conferir snapshots, segredos em recuperação, logs, imagens e interfaces residuais.
   Snapshot retido continua gerando armazenamento: excluir apenas com autorização
   específica, após recuperar as evidências necessárias.

A configuração não é um deploy de produção: um único banco/task; sem HA.
