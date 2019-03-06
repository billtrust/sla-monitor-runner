resource "aws_sns_topic" "sla-monitor-report-processing" {
  name = "sla-monitor-result-published-${var.aws_env}"
}