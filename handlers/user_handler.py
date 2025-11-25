from aiogram import Router, types
from aiogram.filters import CommandStart
from .x_handler.handle_reply import *
from utilities.extractor import XLinkExtractor

extractor = XLinkExtractor()
router = Router(name='user_router')

@router.message(CommandStart())
async def command_start(message: types.Message):
    user = message.from_user.mention_markdown()
    await message.delete()
    print(user)
    await message.answer(
        f'Greetings {user}.\n' 
        'Send me tweet url and I will bring you media in best available quality'
    )
    
@router.message()
async def handle_message(message: types.Message):
    tweet_id = await get_tweet_id(message)
    
    if not tweet_id:
        await message.reply('Could not found any x links in the message.')
        return 
    
    at_least_one_media_sent = False
    
    try:
        media = extractor.scrape_media(tweet_id)
        publisher = extractor.scrape_details(tweet_id)
        
    
        if not media:
            await message.reply('Post has no media')
            
        if await reply_with_media(message, media, publisher):
            at_least_one_media_sent = True
                
    except Exception as e:
        print(tweet_id, e)
        await message.reply('An error occured. Please try again later.')
