mock_provider "aws" {
  mock_data "aws_availability_zones" {
    defaults = { names = ["us-east-2a", "us-east-2b"] }
  }
  mock_resource "aws_iam_role" {
    defaults = { arn = "arn:aws:iam::000000000000:role/synthetic" }
  }
}

variables {
  application_image = "example.invalid/application@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  gateway_image     = "example.invalid/gateway@sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
  run_id            = "test001"
}

run "safe_defaults" {
  command = apply
  assert {
    condition     = contains(jsondecode(aws_ecs_task_definition.lab.container_definitions)[1].command, "/config/logging.json")
    error_message = "Gateway must retain sanitized logging."
  }
  assert {
    condition     = strcontains(jsondecode(aws_ecs_task_definition.lab.container_definitions)[1].healthCheck.command[1], "readiness") && strcontains(jsondecode(aws_ecs_task_definition.lab.container_definitions)[2].healthCheck.command[1], "ready")
    error_message = "Gateway and API health must verify readiness."
  }
  assert {
    condition     = length(jsondecode(aws_ecs_task_definition.lab.container_definitions)) == 3 && !contains([for secret in jsondecode(aws_ecs_task_definition.lab.container_definitions)[2].secrets : secret.name], "LITELLM_MASTER_KEY")
    error_message = "Administrative credentials must stay out of the API/default task."
  }
  assert {
    condition     = startswith(aws_db_instance.lab.engine_version, "16.") && aws_db_instance.lab.deletion_protection && !aws_db_instance.lab.skip_final_snapshot && endswith(aws_db_instance.lab.final_snapshot_identifier, "test001")
    error_message = "PostgreSQL major and protected unique final snapshot required."
  }
}

run "temporary_admin" {
  command = apply
  variables { enable_admin = true }
  assert {
    condition     = length(jsondecode(aws_ecs_task_definition.lab.container_definitions)) == 4 && jsondecode(aws_ecs_task_definition.lab.container_definitions)[3].name == "admin" && contains([for secret in jsondecode(aws_ecs_task_definition.lab.container_definitions)[3].secrets : secret.name], "LITELLM_MASTER_KEY")
    error_message = "Opt-in admin must have its own container and master credential."
  }
}

run "cleanup_keeps_backup" {
  command = apply
  variables { deletion_protection = false }
  assert {
    condition     = !aws_db_instance.lab.deletion_protection && !aws_db_instance.lab.skip_final_snapshot && !aws_ecr_repository.images["application"].force_delete
    error_message = "Cleanup must preserve snapshot and refuse accidental image deletion."
  }
}

