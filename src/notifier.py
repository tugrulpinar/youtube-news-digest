import os
import logging

import boto3

logger = logging.getLogger(__name__)

SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]


def send_email(subject: str, message: str) -> None:
    """Publish a message to the SNS topic (which delivers to subscribed emails)."""
    client = boto3.client("sns")
    client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=subject[:100],  # SNS subject max is 100 chars
        Message=message,
    )
    logger.info("Email sent via SNS topic %s", SNS_TOPIC_ARN)
