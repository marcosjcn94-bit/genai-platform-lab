# AWS: implantação ainda não autorizada

Estado: somente declaração; nunca confundir validate com implantação.
Avaliação realizada: [custos, pendências e próxima execução](aws-evaluation-2026-10-02.md).
Dados de plano/inventário são privados e ficam fora do Git; nenhum recurso criado.
Região fixa us-east-2. Uma task Fargate com mock, sem API pública, sem NAT/ALB.
RDS privado single-AZ exige subnet group em duas AZs; isso não habilita Multi-AZ.
ECS Exec exige filesystem gravável, Session Manager plugin e permissão do operador.
A task possui apenas canais ssmmessages; execução possui ECR/logs/segredo específico.
Wildcards nos canais SSM e ECR authorization são necessários pelo serviço.
Sessões Exec não gravam conteúdo; CloudTrail registra a chamada administrativa.

## Gate financeiro obrigatório
Conferir AWS Settings > View all projects > Overview > Additional Info > Region.
Conferir Billing: FREE/PAID, créditos restantes, validade e limite de gastos.
Conferir serviços permitidos e estimar para a duração concreta:
Fargate 1 vCPU/3 GB, RDS db.t4g.micro + 20 GB gp3 + backups,
IPv4 público por hora, ECR armazenamento, Secrets Manager (runtime + senha RDS),
CloudWatch ingestão/retenção, tráfego de saída e snapshots remanescentes.
Sem saldo, duração e preços atuais confirmados, a estimativa está pendente.
Não executar apply, publicar imagens ou povoar segredos sem autorização concreta.
Avaliação atual não executou plan autenticado; esse plano deve ser preparado e
revisado antes de solicitar a autorização de criação.

## Sequência após autorização concreta
1. Resolver as pendências da avaliação; revisar plan, custos e horário de destruição; manter desired_count=0 inicialmente. Isso não impede cobrança do RDS e armazenamento após criação.
2. Criar recursos autorizados; construir `application` com o `Dockerfile` da raiz e `gateway` com `docker build -f litellm/Dockerfile.aws -t <tag> .`; publicar ambas por digest no ECR. A imagem AWS inclui config local de rede para o mock e instrumentação sanitizada.
3. Fora do Terraform, preencher segredo JSON runtime com DATABASE_URL (TLS requerido),
   LITELLM_MASTER_KEY, APP_A_TOKEN/B_TOKEN, APP_A_GATEWAY_KEY/B_GATEWAY_KEY e METRICS_TOKEN.
   Senha RDS é gerenciada pelo serviço; não copiar para Git/terminal/log.
4. Atualizar digests e desired_count=1; aguardar saúde do gateway.
5. Executar bootstrap administrativo de forma temporária e interna, removendo o
   acesso ao master key após execução. Não expor master key no container API.
6. ECS Exec no API: health, duas chamadas sintéticas e exportação administrativa
   isolada. Não colar segredos em argumentos ou conteúdo de sessão.
7. Monitorar custos. Antes de destruir: exportar evidência sanitizada e backup aprovado.
   Desabilitar deletion_protection explicitamente; planejar snapshot final.
   Esvaziar ECR somente após confirmar os digests; destruir recursos autorizados.
   Conferir snapshots, segredos em recuperação, logs, imagens e interfaces residuais.

A configuração não é um deploy de produção: um único banco/task; sem HA.
