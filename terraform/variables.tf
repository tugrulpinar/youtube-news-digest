variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "youtube_api_key" {
  description = "YouTube Data API v3 key"
  type        = string
  sensitive   = true
}

variable "youtube_channel_id" {
  description = "YouTube channel ID to monitor"
  type        = string
}

variable "email_address" {
  description = "Email address to receive summaries"
  type        = string
}

variable "schedule_expression" {
  description = "EventBridge schedule expression"
  type        = string
  default     = "cron(0 14 * * ? *)"
}

variable "bedrock_model_id" {
  description = "Bedrock model ID for summarization"
  type        = string
  default     = "anthropic.claude-3-5-sonnet-20241022-v2:0"
}

variable "image_tag" {
  description = "Docker image tag for the Lambda container image"
  type        = string
  default     = "latest"
}
