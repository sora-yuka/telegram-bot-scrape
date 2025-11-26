import re 
import requests
from typing import List, Optional, Dict

class XLinkExtractor:
    _x_api_url = 'https://api.vxtwitter.com/Twitter/status/'

    def scrape_media(self, tweet_id: int) -> List[Dict]:
        response = self._scrape(tweet_id)
        return response['media_extended']
    
    def scrape_details(self, tweet_id: int) -> Dict:
        response = self._scrape(tweet_id)
        user_data = {
            'display name': response['user_name'], 
            'username': f"@{response['user_screen_name']}",
            'tweet url': response['tweetURL'],
        }
        return user_data
    
    def extract_link(self, tweet_url: str) -> Optional[List[Dict]]:
        tweet_id = re.search(r'/status/(\d+)', tweet_url).group(1)
        return tweet_id or None
    
    def _scrape(self, tweet_id: int) -> Dict:
        request = requests.get(f'{self._x_api_url}{tweet_id}')
        request.raise_for_status()
        return request.json()
