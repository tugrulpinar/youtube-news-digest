output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.digest.arn
}

output "sns_topic_arn" {
  description = "ARN of the SNS topic"
  value       = aws_sns_topic.digest.arn
}

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.digest.repository_url
}
