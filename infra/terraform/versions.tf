terraform {
  required_version = ">= 1.13.3, < 2.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "6.14.1" }
  }
}
provider "aws" {
  region = "us-east-2"
  default_tags {
    tags = { Project = "genai-platform-lab", Environment = "temporary-demo" }
  }
}
data "aws_caller_identity" "current" {}
data "aws_availability_zones" "available" { state = "available" }
