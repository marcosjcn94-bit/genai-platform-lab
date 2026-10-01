output "cluster_name" { value = aws_ecs_cluster.lab.name }
output "service_name" { value = aws_ecs_service.lab.name }
output "repositories" { value = { for name, repo in aws_ecr_repository.images : name => repo.repository_url } }
output "database_endpoint" {
  value     = aws_db_instance.lab.endpoint
  sensitive = true
}
output "runtime_secret_arn" {
  value     = aws_secretsmanager_secret.runtime.arn
  sensitive = true
}
