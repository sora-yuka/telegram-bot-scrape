import json
from aiogram import Router, types
from aiogram.filters import CommandStart
from .x_handler.handle_reply import *
from utilities.tweet_extractor import XLinkExtractor

extractor = XLinkExtractor()
router = Router(name='user_router')

@router.message(CommandStart())
async def command_start(message: types.Message):
    user = message.from_user.mention_markdown()
    await message.delete()
    await message.answer(
        f'Greetings {user}.\n' 
        'Send me tweet url and I will bring you media in best available quality'
    )
    
@router.message()
async def handle_message(message: types.Message):
    with open('./handlers/prefixes.json', mode='r', encoding='utf-8') as f:
        prefixes = json.load(f)
        
        if any(message.text.startswith(prefix) for prefix in prefixes['x_prefix']):
            tweet_id = await get_tweet_id(message)
            
            if not tweet_id:
                await message.reply('Could not found any x links in the message.')
                return 
            
            try:
                media = extractor.scrape_media(tweet_id)
                publisher = extractor.scrape_details(tweet_id)
                
                if not media:
                    await message.reply('Post has no media')
                    
                await reply_with_media(message, media, publisher)
                        
            except Exception as e:
                logger.error(f'Error occured on tweet id - {tweet_id}. {e}')
                await message.reply('An error occured. Please try again later.')
        else:
            logger.info('User message does not matched any socials prefix')
