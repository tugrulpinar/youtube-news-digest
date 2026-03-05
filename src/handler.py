import json
import logging
import os

import boto3

from youtube import get_latest_video_id
from transcript import get_transcript
from summarizer import summarize
from notifier import send_email

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

SSM_PARAM_LAST_VIDEO = os.environ.get(
    "SSM_PARAM_LAST_VIDEO", "/youtube-digest/last-video-id"
)


def _get_last_video_id() -> str | None:
    """Read the last processed video ID from SSM Parameter Store."""
    ssm = boto3.client("ssm")
    try:
        resp = ssm.get_parameter(Name=SSM_PARAM_LAST_VIDEO)
        return resp["Parameter"]["Value"]
    except ssm.exceptions.ParameterNotFound:
        return None


def _set_last_video_id(video_id: str) -> None:
    """Store the last processed video ID in SSM Parameter Store."""
    ssm = boto3.client("ssm")
    ssm.put_parameter(
        Name=SSM_PARAM_LAST_VIDEO, Value=video_id, Type="String", Overwrite=True
    )


def handler(event, context):
    """Lambda entry point — triggered by EventBridge on a schedule."""
    logger.info("Event: %s", json.dumps(event))

    # 1. Get the latest video from the channel
    video_id = get_latest_video_id()
    if not video_id:
        logger.info("No videos found. Exiting.")
        return {"statusCode": 200, "body": "No videos found"}

    # 2. Skip if we already processed this video
    last_video_id = _get_last_video_id()
    if video_id == last_video_id:
        logger.info("Video %s already processed. Exiting.", video_id)
        return {"statusCode": 200, "body": "Already processed"}

    logger.info("New video found: %s", video_id)

    # 3. Get transcript
    transcript = get_transcript(video_id)
    logger.info("Transcript length: %d characters", len(transcript))

    # 4. Summarize
    summary = summarize(transcript)
    logger.info("Summary generated (%d chars)", len(summary))

    # 5. Send email
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    email_body = f"New video summary\n\nVideo: {video_url}\n\n{summary}"
    send_email(subject="New YouTube Video Summary", message=email_body)

    # 6. Remember this video so we don't process it again
    _set_last_video_id(video_id)

    return {"statusCode": 200, "body": f"Processed video {video_id}"}
