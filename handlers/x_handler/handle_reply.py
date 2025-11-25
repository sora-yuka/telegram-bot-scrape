from typing import List, Dict
from aiogram import Router, types
from .handle_media import *
from utilities.extractor import XLinkExtractor

extractor = XLinkExtractor()
router = Router(name='bot_reply_router')

@router.message()
async def get_tweet_id(message: types.Message):
    url = message.text
    
    try:
        return extractor.extract_link(url) or None
    except Exception as e:
        print(e)
        await message.reply("Couldn't unshortened the link.")
        
@router.message()
async def reply_with_media(
    message: types.Message,
    tweet_media: List[Dict[str, str]],
    publisher_data: Dict[str, str],
):
    photos = [media for media in tweet_media if tweet_media[0]['type'] == 'image']
    videos = [media for media in tweet_media if tweet_media[0]['type'] == 'video']
    gifs = [media for media in tweet_media if tweet_media[0]['type'] == 'gif']
    
    if photos:
        await send_message(message, photos, publisher_data)
    if videos:
        await send_video(message, videos, publisher_data)
