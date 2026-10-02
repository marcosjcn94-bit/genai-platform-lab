variable "name" {
  type    = string
  default = "genai-platform-lab"
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,30}$", var.name))
    error_message = "Use 3–31 lowercase letters, numbers or hyphens."
  }
}
variable "application_image" {
  type        = string
  description = "ECR application image pinned by sha256 digest."
  validation {
    condition     = can(regex("@sha256:[a-f0-9]{64}$", var.application_image))
    error_message = "Immutable digest required."
  }
}
variable "gateway_image" {
  type        = string
  description = "ECR gateway image built from litellm/Dockerfile.aws, pinned by digest."
  validation {
    condition     = can(regex("@sha256:[a-f0-9]{64}$", var.gateway_image))
    error_message = "Immutable digest required."
  }
}
variable "desired_count" {
  type        = number
  default     = 0
  description = "Keep zero until images and secret versions have been installed explicitly."
  validation {
    condition     = contains([0, 1], var.desired_count)
    error_message = "This laboratory supports at most one task."
  }
}

variable "enable_admin" {
  type        = bool
  default     = false
  description = "Temporary isolated admin container; disable after bootstrap/export."
}

variable "postgres_version" {
  type    = string
  default = "16.15"
  validation {
    condition     = can(regex("^16\\.[0-9]+$", var.postgres_version))
    error_message = "Use an available PostgreSQL 16 minor version."
  }
}

variable "run_id" {
  type        = string
  description = "Unique lowercase run suffix for the retained final snapshot."
  validation {
    condition     = can(regex("^[a-z0-9]{6,20}$", var.run_id))
    error_message = "Use a unique 6-20 character lowercase alphanumeric run ID."
  }
}

variable "deletion_protection" {
  type        = bool
  default     = true
  description = "Disable only in the explicitly authorized cleanup phase; snapshot stays mandatory."
}
