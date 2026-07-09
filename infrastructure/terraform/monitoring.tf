resource "grafana_dashboard" "aria_os_overview" {
  config_json = file("${path.module}/../../monitoring/grafana-dashboard.json")
}

resource "grafana_data_source" "prometheus" {
  type       = "prometheus"
  name       = "ARIA OS Metrics"
  url        = "http://prometheus:9090"
  is_default = true
}

resource "grafana_notification_channel" "slack_alerts" {
  name     = "ARIA OS Slack Alerts"
  type     = "slack"
  settings = {
    url = var.slack_webhook_url
  }
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for alert notifications"
  type        = string
  sensitive   = true
  default     = ""
}
