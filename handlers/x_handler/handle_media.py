import asyncio
from typing import List, Dict
from os.path import basename
from aiogram import Router, types
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.exceptions import TelegramBadRequest
import requests
from requests.exceptions import RequestException
from tempfile import TemporaryFile


router = Router(name='media_processing_router')

@router.message()
async def send_message(
    message: types.Message,
    tweet_photos: List[Dict[str, str]],
    publisher_data: Dict[str, str],
):
    print(publisher_data['tweet url'])
    caption = f'Published by {publisher_data["display name"]} [{publisher_data["username"]}]({publisher_data["tweet url"]})'
    photos = MediaGroupBuilder(caption=caption)
    photo_url = tweet_photos[0]['url']
    
    if len(tweet_photos) == 1:
        await message.reply_document(
            document=types.URLInputFile(url=photo_url, filename=basename(photo_url)),
            caption=caption
        )
    else:
        for photo in tweet_photos:
            photos.add(type='photo', media=photo['url'])
        await message.bot.send_media_group(
            chat_id=message.from_user.id,
            media=photos.build(),
        )

@router.message()
async def send_video(
    message: types.Message,
    tweet_video: List[Dict[str, str]],
    publisher_data: Dict[str, str]
):
    caption = f'Published by {publisher_data["display name"]} [{publisher_data["username"]}]({publisher_data["tweet url"]})'
    video_url = tweet_video[0]['url']
    
    try:
        request = requests.get(video_url, stream=True)
        request.raise_for_status()
        
        if (video_size := int(request.headers['Content-length'])) <= int(20e6):
            temporary_message = await message.answer('Preparing for sending. Just a moment...')
            await asyncio.sleep(3)
            
            await message.reply_video(video=video_url, caption=caption)
            await temporary_message.delete()
        elif video_size <= 50e6:
            temporary_message = await message.reply('File bigger than expected. Please, wait a bit longer...')
            await asyncio.sleep(6)
            
            await message.reply_document(
                document=types.URLInputFile(url=video_url, filename=basename(video_url)),
                caption=caption,
            )
            await temporary_message.delete()
        else:
            await message.reply(
                'Video is too large for Telegram. Use direct link to download:\n'
                f'{video_url}'
            )
            
    except(requests.HTTPError, KeyError, TelegramBadRequest, RequestException) as e:
        await temporary_message.delete()
        await message.reply(f'Error occured while trying to proccess video. Use direct link: [{"url"}]({video_url})')
        print(e)
