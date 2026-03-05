import json
import logging
import os

import boto3

logger = logging.getLogger(__name__)

BEDROCK_MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"
)
BEDROCK_REGION = os.environ.get("BEDROCK_REGION", "us-east-1")

PROMPT_TEMPLATE = (
    "Sen yardımcı bir asistansın. Aşağıdaki YouTube video transkriptini, "
    "ana çıkarımları madde madde belirterek kısa ve iyi yapılandırılmış bir özet haline getir. "
    "Özeti 300 kelimenin altında tut.\n\n"
    "Transkript:\n{transcript}"
)


def summarize(transcript: str) -> str:
    """Use Amazon Bedrock (Claude) to summarize the transcript."""
    client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
            "messages": [
                {
                    "role": "user",
                    "content": PROMPT_TEMPLATE.format(transcript=transcript),
                }
            ],
        }
    )

    response = client.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=body,
    )

    result = json.loads(response["body"].read())
    return result["content"][0]["text"]
