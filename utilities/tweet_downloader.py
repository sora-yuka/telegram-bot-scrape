import re 
import aiohttp
import logging
from typing import List, Optional, Dict
from dataclasses import dataclass

logger = logging.getLogger()


@dataclass
class DownloadResult:
    user_name: str
    user_screen_name: str
    tweet_url: str
    media_extended: List


class TweetDownloader:
    _api_url = "https://api.vxtwitter.com/Twitter/status/"
    
    def extract_link(self, tweet_url: str) -> Optional[List[Dict]]:
        try:
            tweet_id = re.search(r'/status/(\d+)', tweet_url).group(1)
            return tweet_id or None
        except Exception as e:
            logger.error(f"Error occured while extracting tweet url: {e}")
            return
    
    async def get_file_size(url: str) -> Optional[int]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url) as response:
                    content_length = response.headers.get("Content-Length")
                    return int(content_length) if content_length else None
        except Exception as e:
            logger.error(f"Error occured while getting file size: {e}")
            return
    
    async def scrape_tweet(self, tweet_id: int) -> DownloadResult:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._api_url}{tweet_id}") as response:
                response.raise_for_status()
                data = await response.json()
        return DownloadResult(
            user_name=data["user_name"],
            user_screen_name=data["user_screen_name"],
            tweet_url=data["tweetURL"],
            media_extended=data["media_extended"]
        )
