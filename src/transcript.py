import logging
from youtube_transcript_api import YouTubeTranscriptApi

logger = logging.getLogger(__name__)


def get_transcript(video_id: str) -> str:
    """Fetch and return the full transcript text for a YouTube video."""
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join(segment["text"] for segment in transcript_list)
