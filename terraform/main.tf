data "aws_caller_identity" "current" {}

# ─── ECR Repository ──────────────────────────────────────────────────────────

resource "aws_ecr_repository" "digest" {
  name                 = "youtube-digest"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }
}

# ─── SNS Topic + Email Subscription ──────────────────────────────────────────

resource "aws_sns_topic" "digest" {
  name = "youtube-digest-topic"
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.digest.arn
  protocol  = "email"
  endpoint  = var.email_address
}

# ─── SSM Parameter (last processed video ID) ─────────────────────────────────

resource "aws_ssm_parameter" "last_video" {
  name  = "/youtube-digest/last-video-id"
  type  = "String"
  value = "none"

  lifecycle {
    ignore_changes = [value]
  }
}

# ─── IAM Role for Lambda ─────────────────────────────────────────────────────

resource "aws_iam_role" "lambda" {
  name = "youtube-digest-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "lambda" {
  name = "youtube-digest-lambda-policy"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"
      },
      {
        Effect   = "Allow"
        Action   = "sns:Publish"
        Resource = aws_sns_topic.digest.arn
      },
      {
        Effect   = "Allow"
        Action   = ["ssm:GetParameter", "ssm:PutParameter"]
        Resource = aws_ssm_parameter.last_video.arn
      },
      {
        Effect   = "Allow"
        Action   = "bedrock:InvokeModel"
        Resource = "arn:aws:bedrock:${var.aws_region}::foundation-model/${var.bedrock_model_id}"
      }
    ]
  })
}

# ─── Lambda Function (Docker image) ──────────────────────────────────────────

resource "aws_lambda_function" "digest" {
  function_name = "youtube-digest"
  role          = aws_iam_role.lambda.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.digest.repository_url}:${var.image_tag}"
  timeout       = 120
  memory_size   = 256

  environment {
    variables = {
      YOUTUBE_API_KEY      = var.youtube_api_key
      YOUTUBE_CHANNEL_ID   = var.youtube_channel_id
      SNS_TOPIC_ARN        = aws_sns_topic.digest.arn
      SSM_PARAM_LAST_VIDEO = "/youtube-digest/last-video-id"
      BEDROCK_MODEL_ID     = var.bedrock_model_id
      BEDROCK_REGION       = var.aws_region
    }
  }
}

# ─── EventBridge Schedule ────────────────────────────────────────────────────

resource "aws_cloudwatch_event_rule" "schedule" {
  name                = "youtube-digest-schedule"
  description         = "Check YouTube channel for new videos"
  schedule_expression = var.schedule_expression
}

resource "aws_cloudwatch_event_target" "lambda" {
  rule = aws_cloudwatch_event_rule.schedule.name
  arn  = aws_lambda_function.digest.arn
}

resource "aws_lambda_permission" "eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.digest.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.schedule.arn
}
