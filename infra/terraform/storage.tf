resource "aws_ecr_repository" "images" {
  for_each             = toset(["application", "gateway"])
  name                 = "${var.name}/${each.key}"
  image_tag_mutability = "IMMUTABLE"
  force_delete         = false
  image_scanning_configuration { scan_on_push = true }
}
resource "aws_cloudwatch_log_group" "lab" {
  name              = "/ecs/${var.name}"
  retention_in_days = 3
}
resource "aws_secretsmanager_secret" "runtime" {
  name_prefix             = "${var.name}-runtime-"
  description             = "Populate JSON outside Terraform; no secret values in state."
  recovery_window_in_days = 7
}
resource "aws_db_subnet_group" "lab" {
  name       = var.name
  subnet_ids = aws_subnet.private[*].id
}
resource "aws_db_instance" "lab" {
  identifier                  = var.name
  engine                      = "postgres"
  engine_version              = var.postgres_version
  instance_class              = "db.t4g.micro"
  allocated_storage           = 20
  storage_type                = "gp3"
  storage_encrypted           = true
  db_name                     = "gateway"
  username                    = "gateway"
  manage_master_user_password = true
  db_subnet_group_name        = aws_db_subnet_group.lab.name
  vpc_security_group_ids      = [aws_security_group.db.id]
  publicly_accessible         = false
  multi_az                    = false
  backup_retention_period     = 1
  deletion_protection         = var.deletion_protection
  skip_final_snapshot         = false
  final_snapshot_identifier   = "${var.name}-final-${var.run_id}"
  auto_minor_version_upgrade  = true
}
