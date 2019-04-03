resource "aws_s3_bucket" "sla-monitor-runner-logs-bucket" {
  # Rename this bucket to something unique
  bucket = "sla-monitor-runner-logs-${var.aws_env}-${var.aws_region}"

  acl = "private"

  lifecycle_rule {
    enabled = true

    expiration {
      days = 3
    }
  }
}
