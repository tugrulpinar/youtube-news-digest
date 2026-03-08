import logging
import os
import time
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
INITIAL_BACKOFF = 5


def get_transcript(video_id: str) -> str:
    """Fetch and return the full transcript text for a YouTube video."""
    proxy_username = os.environ.get("WEBSHARE_PROXY_USERNAME")
    proxy_password = os.environ.get("WEBSHARE_PROXY_PASSWORD")

    if proxy_username and proxy_password:
        logger.info("Using Webshare proxy for transcript fetch")
        ytt_api = YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username=proxy_username,
                proxy_password=proxy_password,
            )
        )
    else:
        logger.warning("No proxy credentials found, fetching without proxy")
        ytt_api = YouTubeTranscriptApi()

    for attempt in range(MAX_RETRIES):
        try:
            fetched_transcript = ytt_api.fetch(video_id, languages=['tr'])
            return " ".join(segment.text for segment in fetched_transcript)
        except Exception as e:
            if "429" in str(e) and attempt < MAX_RETRIES - 1:
                wait = INITIAL_BACKOFF * (2 ** attempt)
                logger.warning(f"Rate limited (attempt {attempt + 1}/{MAX_RETRIES}), waiting {wait}s")
                time.sleep(wait)
            else:
                raise
