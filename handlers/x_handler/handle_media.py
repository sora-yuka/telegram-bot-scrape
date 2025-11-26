import logging
from typing import List, Dict
from os.path import basename
from aiogram import Router, types
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.exceptions import TelegramBadRequest
from utilities.tweet_handle_video import get_file_size

logger = logging.getLogger(__name__)


class XMediaProcessor:
    def __init__(self):
        self.router = Router(name='media_processing_router')
        
        self.router.message.register(self.send_gif)
        self.router.message.register(self.send_photo)
        self.router.message.register(self.send_video)
    
    async def send_gif(
        self, 
        message: types.Message,
        tweet_gif: List[Dict],
        publisher_data: Dict
    ):
        animation = tweet_gif[0]['url']
        caption = self._build_caption(publisher_data=publisher_data)
        await message.reply_animation(animation=animation, caption=caption)
        
    async def send_photo(
        self,
        message: types.Message,
        tweet_photos: List[Dict],
        publisher_data: Dict
    ):
        caption = self._build_caption(publisher_data=publisher_data)
        
        if len(tweet_photos) == 1:
            photo_url = tweet_photos[0]['url']
            document = types.URLInputFile(ulr=photo_url, filename=basename(photo_url))
            await message.reply_document(document=document, caption=caption)
        else:
            media_group = MediaGroupBuilder(caption=caption)
            for photo in tweet_photos:
                media_group.add(type='photo', media=photo['url'])
            await message.bot.send_media_group(
                chat_id=message.from_user.id, media=media_group.build()
            )
    
    async def send_video(
        self,
        message: types.Message,
        tweet_video: List[Dict],
        publisher_data: Dict
    ):
        video_url = tweet_video[0]['url']
        caption = self._build_caption(publisher_data=publisher_data)
        temporary_message = None
        
        video_size = await get_file_size(url=video_url)
        size_mb = f'{video_size / 1e6:.1f}MB'
        logger.info(f'Video size {size_mb}')
        
        try:
            if video_size <= int(20e6):
                temporary_message = await message.answer(
                    f'Preparing to send video ({size_mb}). Just a moment...'
                )
                await message.answer_video(video=video_url, caption=caption)
                await temporary_message.edit_text(f'Video sent successfully (size: {size_mb}).')
            elif video_size <= int(50e6):
                temporary_message = await message.answer(
                    f'File is larger than expected ({size_mb}). Downloading and uploading... '
                    'This may take few minutes.'
                )
                await message.answer_document(
                    document=types.URLInputFile(
                        url=video_url, 
                        filename=basename(video_url.split("?")[0])
                    ),
                    caption=caption,
                )
                await temporary_message.edit_text(f'Video sent successfully (size: {size_mb}).')
            else:
                await message.reply(
                    f'⚠️ *Video Too Large* ({size_mb})\n\n'
                    "Unfortunately, this file exceeds Telegram's size limit for bots. "
                    f'You can download the video directly using this [link]({video_url}).'
                )
        except (KeyError, TelegramBadRequest) as e:
            logger.error('Error occured while processing video: %s', e)
            await message.reply(
                'Error occured while trying to send media. '
                f'You can download the video directly using this [link]({video_url}).'
            )
        
    def _build_caption(self, publisher_data: Dict) -> str:
        return (
            f'Published by {publisher_data["display name"]} '
            f'[{publisher_data["username"]}]({publisher_data["tweet url"]})'
        )

x_media_processor = XMediaProcessor()
router = x_media_processor.router
