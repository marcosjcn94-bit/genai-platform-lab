# Avaliação AWS — 2026-10-02

Resultado: desenho adequado para uma demonstração interna temporária com mock;
**deploy ainda não liberado**. Avaliação não cria recursos nem comprova operação
na nuvem. Apresentação do portfólio permanece para depois da etapa AWS.

## Verificação técnica e privacidade

- O desenho declara recursos regionais em `us-east-2`. Estado financeiro,
  identidade, quotas e inventário pertencem ao pre-flight privado local,
  ignorado pelo Git; este relatório público não os reproduz.
- ECS, ECR, RDS, VPC, CloudWatch e Secrets Manager constam da
  [lista oficial da nova experiência gratuita](https://docs.aws.amazon.com/accounts/latest/reference/supported-services-sign-up-new.html).
  Estar na lista não torna seu uso gratuito nem comprova permissões de criação.
- Terraform `fmt -check` e `validate` passaram nesta avaliação. Imagens locais
  application/gateway: Linux/amd64. Nenhum `plan`, `apply`, push ECR ou segredo criado.

## Custos públicos em USD

Preços on-demand consultados em 2026-10-02, região Ohio. Catálogos publicados entre
setembro e outubro de 2026; SKUs, datas e fórmulas por componente estão em
[aws-costs-2026-10-02.json](aws-costs-2026-10-02.json).
O endpoint público de preços em `us-east-1` não cria recursos nessa região.

| Componente | Preço usado |
|---|---:|
| Fargate Linux/x86, vCPU | US$ 0,04048/vCPU-h |
| Fargate memória | US$ 0,004445/GiB-h |
| RDS PostgreSQL db.t4g.micro Single-AZ | US$ 0,016/h |
| RDS gp3 | US$ 0,115/GB-mês |
| IPv4 público da task | US$ 0,005/h |
| ECR privado | US$ 0,10/GB-mês |
| Secrets Manager | US$ 0,40/segredo-mês + US$ 0,000005/chamada |
| Logs Standard: ingestão / armazenamento | US$ 0,50/GB / US$ 0,03/GB-mês |
| Snapshot PostgreSQL cobrável | US$ 0,095/GB-mês |
| CPU extra T4g | US$ 0,075/vCPU-h |

Fontes regionais: [ECS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonECS/current/us-east-2/index.json),
[RDS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/us-east-2/index.json),
[ECR](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonECR/current/us-east-2/index.json),
[Secrets](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSSecretsManager/current/us-east-2/index.json),
[CloudWatch](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/us-east-2/index.json);
[IPv4](https://aws.amazon.com/vpc/pricing/).

Premissas: uma task (1 vCPU/3 GiB), um RDS/20 GB, dois segredos, ECR 2 GB.
Reservas por execução: logs 0,1 GB; 1.000 leituras de segredo; tráfego entre AZs
1 GB a US$ 0,02 combinado; saída internet 1 GB a US$ 0,09; CPU extra 1 vCPU-h;
snapshot 20 GB, ECR 2 GB e logs 0,1 GB por 72 h após encerramento. Reservas não
são limites aplicados pelo código. ECR usa tamanho comprimido real; 2 GB é premissa.

| Tempo de recursos ativos | Estimativa com essas reservas |
|---|---:|
| 2 horas | US$ 0,61 |
| 4 horas | US$ 0,76 |
| 24 horas | US$ 2,35 |
| 730 horas | US$ 58,36 |

Cálculo Decimal: custo base/h = `0,04048 + 3×0,004445 + 0,016 + 0,005`;
custos recorrentes/mês = `20×0,115 + 2×0,10 + 2×0,40`; prorrateio usando 730 h/mês.
Somar as reservas discriminadas no JSON. O cenário de 730 h mantém o mesmo
pequeno uso sintético; não estima carga de produção. Créditos e franquias não
foram descontados; impostos/câmbio não incluídos. Tempos efetivos de criação,
retries, exclusão e resíduos podem elevar o valor.

Fontes: [transferência entre AZs](https://aws.amazon.com/blogs/architecture/exploring-data-transfer-costs-for-aws-managed-databases/),
[saída internet](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSDataTransfer/current/us-east-2/index.json).
Segredos marcados para exclusão não são cobrados durante a recuperação,
conforme [documentação](https://docs.aws.amazon.com/secretsmanager/latest/userguide/manage_delete-secret.html).

## Pontos a preparar antes do deploy

1. **Logs:** `main.tf` sobrescreve o comando do gateway e omite
   `--log_config /config/logging.json` presente na imagem. Preservar o filtro
   sanitizado e provar com canários antes de enviar logs ao CloudWatch.
   [ECS command substitui CMD](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/create-task-definition.html).
2. **Administração:** criar definição temporária de tarefa/processo administrativo
   para bootstrap/export, com master key fora da API e sem valor em argumentos,
   logs ou state. O runbook descreve intenção; o artefato executável ainda falta.
3. **PostgreSQL:** `engine_version` não está fixado;
   escolher versão 16 disponível para manter o major da demo local e validar
   migrations/TLS. Não confiar no padrão variável do serviço.
4. **ECS Exec:** plugin Session Manager não encontrado no PATH/nos diretórios
   Amazon inspecionados. Instalar/verificar antes da demo; permissões do operador
   para Exec e para criar IAM/serviços ainda não foram comprovadas.
   [Requisitos ECS Exec](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-exec.html).
5. **Saúde:** incluir verificação da API e comprovar readiness/migrations no RDS.
   Health atual do gateway é liveness; não garante disponibilidade do banco.
6. **Destruição:** `desired_count=0` não impede cobrança do RDS/armazenamento.
   `deletion_protection=true`, snapshot final obrigatório e ECR `force_delete=false`
   exigem sequência explícita. Nome fixo do snapshot final deve evitar colisões
   em demonstrações futuras. Não apagar backup sem autorização específica.

## Próxima execução concreta

Proposta para revisão: **até quatro horas de recursos ativos**, uso sintético,
reserva operacional de **US$ 2 em créditos**. A reserva não é teto automático
de faturamento; parar cedo se o tempo/custo previsto deixar de caber nela.

Antes de pedir autorização de provisionamento, preparar os seis pontos acima e
um plano Terraform sanitizado. Confirmar região em AWS Settings > View all
projects > Overview > Additional Info > Region; validade de créditos e limite
de gastos em Billing. Revisar criação, evidências, prazo e política de backup/
limpeza como uma execução única. Usuário decide a autorização concreta.

Ao executar posteriormente: manter task zero até imagens e segredos estarem
prontos; ativar uma task; provar health, duas identidades, consumo/fallback;
exportar evidências sanitizadas; encerrar service/RDS/rede e verificar resíduos.
Não há API pública, ALB/NAT, Ollama ou stack Grafana/Jaeger declarados na AWS;
a demo de nuvem usa mock e acesso interno ECS Exec. Não promete paridade com
todas as funcionalidades locais, produção ou alta disponibilidade.
