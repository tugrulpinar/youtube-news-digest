import os
import logging
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

YOUTUBE_API_KEY = os.environ["YOUTUBE_API_KEY"]
CHANNEL_ID = os.environ["YOUTUBE_CHANNEL_ID"]


def get_latest_video_id() -> str | None:
    """Return the video ID of the most recent upload on the channel."""
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    response = (
        youtube.search()
        .list(
            channelId=CHANNEL_ID,
            order="date",
            part="id",
            type="video",
            maxResults=1,
        )
        .execute()
    )

    items = response.get("items", [])
    if not items:
        logger.warning("No videos found for channel %s", CHANNEL_ID)
        return None

    return items[0]["id"]["videoId"]
