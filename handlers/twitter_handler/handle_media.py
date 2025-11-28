import logging
from os.path import basename
from typing import List, Dict
from aiogram import types
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.utils.chat_action import ChatActionSender

logger = logging.getLogger(__name__)


class TwitterMediaProcessor:
    @staticmethod
    def _build_caption(user_name: str, user_screen_name: str, tweet_url: str) -> str:
        return f"Published by {user_name} [@{user_screen_name}]({tweet_url})"
    
    @staticmethod
    def _categorize_media(media_list: List[Dict]) -> Dict[str, List[Dict]]:
        categorized = {"photos": [], "videos": [], "gifs": []}
        
        for media in media_list:
            media_type = media.get("type", "").lower()
            
            if media_type == "image":
                categorized["photos"].append(media) 
            if media_type == "video":
                categorized["videos"].append(media)
            if media_type == "gif":
                categorized["gifs"].append(media)
        return categorized
    
    async def send_photos(
        self,
        message: types.Message,
        photos: List[Dict],
        caption: str
    ) -> None:
        try:
            async with ChatActionSender.upload_photo(chat_id=message.chat.id, bot=message.bot):
                if len(photos) == 1:
                    photo_url = photos[0]["url"]
                    document = types.URLInputFile(url=photo_url, filename=basename(photo_url))
                    await message.reply_document(document=document, caption=caption)
                else:
                    media_group = MediaGroupBuilder(caption=caption)
                    
                    for photo in photos:
                        media_group.add_photo(media=photo["url"])
                    
                    await message.bot.send_media_group(
                        chat_id=message.chat.id, media=media_group.build()
                    )
        except Exception as e:
            logger.error(f"Failed to send photos: {e}")
            raise
    
    async def send_videos(
        self,
        message: types.Message,
        videos: List[Dict],
        caption: str
    ) -> None:
        try:
            async with ChatActionSender.upload_video(chat_id=message.chat.id, bot=message.bot):
                if len(videos) == 1:
                    video_url = videos[0]["url"]
                    await message.reply_video(video=video_url, caption=caption)
                else:
                    media_group = MediaGroupBuilder(caption=caption)
                    
                    for video in videos:
                        media_group.add_video(media=video["url"])
                    
                    await message.bot.send_media_group(
                        chat_id=message.chat.id, media=media_group.build()
                    )
        except Exception as e:
            logger.error(f"Failed to send video: {e}")
            raise

    async def send_gifs(
        self,
        message: types.Message,
        gifs: List[Dict],
        caption: str
    ) -> None:
        try:
            last_index = len(gifs) - 1
            for i, gif in enumerate(gifs):
                animation_url = gif["url"]
                await message.reply_animation(
                    animation=animation_url, 
                    caption=caption if i == last_index else None
                )
        except Exception as e:
            logger.error(f"Failed to send GIFs: {e}")
            raise
    
    async def process_and_send(
        self,
        message: types.Message,
        media_list: List[Dict],
        user_name: str,
        user_screen_name: str,
        post_url: str
    ) -> None:
        if not media_list:
            await message.reply("No media found in this post.")
            return 
        
        caption = self._build_caption(user_name, user_screen_name, post_url)
        categorized = self._categorize_media(media_list)
        
        if categorized['photos']:
            await self.send_photos(message, categorized['photos'], caption)
        
        if categorized['videos']:
            await self.send_videos(message, categorized['videos'], caption)
        
        if categorized['gifs']:
            await self.send_gifs(message, categorized['gifs'], caption)


twitter_media_processor = TwitterMediaProcessor()
