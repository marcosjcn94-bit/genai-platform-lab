locals {
  logging = {
    logDriver = "awslogs"
    options = {
      awslogs-group         = aws_cloudwatch_log_group.lab.name
      awslogs-region        = "us-east-2"
      awslogs-stream-prefix = "lab"
    }
  }
}
resource "aws_ecs_cluster" "lab" {
  name = var.name
  configuration {
    execute_command_configuration { logging = "NONE" }
  }
}
resource "aws_ecs_task_definition" "lab" {
  family                   = var.name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"
  memory                   = "3072"
  execution_role_arn       = aws_iam_role.execution.arn
  task_role_arn            = aws_iam_role.task.arn
  container_definitions = jsonencode([
    {
      name             = "mock", image = var.application_image, essential = true
      command          = ["uvicorn", "mock_provider.main:app", "--host", "127.0.0.1", "--port", "8001", "--no-access-log"]
      linuxParameters  = { initProcessEnabled = true }
      logConfiguration = local.logging
    },
    {
      name        = "gateway", image = var.gateway_image, essential = true
      command     = ["--config", "/config/config.yaml", "--port", "4000", "--host", "127.0.0.1"]
      environment = [{ name = "LITELLM_LOG", value = "ERROR" }]
      secrets = [for key in ["DATABASE_URL", "LITELLM_MASTER_KEY"] :
      { name = key, valueFrom = "${aws_secretsmanager_secret.runtime.arn}:${key}::" }]
      linuxParameters  = { initProcessEnabled = true }
      logConfiguration = local.logging
      healthCheck = {
        command  = ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://127.0.0.1:4000/health/liveliness')\""]
        interval = 15, timeout = 5, retries = 5, startPeriod = 120
      }
    },
    {
      name        = "api", image = var.application_image, essential = true
      environment = [{ name = "GATEWAY_URL", value = "http://127.0.0.1:4000" }]
      secrets = [for key in ["APP_A_TOKEN", "APP_B_TOKEN", "APP_A_GATEWAY_KEY", "APP_B_GATEWAY_KEY", "METRICS_TOKEN"] :
      { name = key, valueFrom = "${aws_secretsmanager_secret.runtime.arn}:${key}::" }]
      dependsOn        = [{ containerName = "gateway", condition = "HEALTHY" }]
      linuxParameters  = { initProcessEnabled = true }
      logConfiguration = local.logging
    }
  ])
}
resource "aws_ecs_service" "lab" {
  name                               = var.name
  cluster                            = aws_ecs_cluster.lab.id
  task_definition                    = aws_ecs_task_definition.lab.arn
  desired_count                      = var.desired_count
  launch_type                        = "FARGATE"
  enable_execute_command             = true
  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 100
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }
  network_configuration {
    subnets          = [aws_subnet.public.id]
    security_groups  = [aws_security_group.task.id]
    assign_public_ip = true
  }
  depends_on = [aws_iam_role_policy.execution, aws_iam_role_policy.exec_channels]
}
