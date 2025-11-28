import json
import logging
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from utilities.tweet_downloader import TweetDownloader
from .twitter_handler.handle_media import twitter_media_processor

logger = logging.getLogger(__name__)

router = Router()

with open("./handlers/prefixes.json", mode="r", encoding="utf-8") as f:
    PREFIXES = json.load(f)

@router.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    user = message.from_user.mention_markdown()
    await message.delete()
    await message.answer(
        f"Greetings {user}.\n"
        "Send me tweet url and I will bring you media."
    )

@router.message()
async def handle_tweet_message(message: types.Message) -> None:        
    tweet_url = None
    words = message.text.split()
    
    for word in words:
        if any(prefix in word for prefix in PREFIXES["x_prefix"]):
            tweet_url = word
            break
    
    if not tweet_url:
        logger.info("User message doesn't match any socials.")
        return
    
    extractor = TweetDownloader()
    
    try:
        tweet_id = extractor.extract_link(tweet_url=tweet_url)
        
        if not tweet_id:
            await message.reply("Invalid tweet URL.")
            return 
        
        tweet = await extractor.scrape_tweet(tweet_id=tweet_id)
        
        if not tweet.media_extended:
            await message.reply("Tweet has no media.")
            return 
        
        await twitter_media_processor.process_and_send(
            message=message, 
            media_list=tweet.media_extended, 
            user_name=tweet.user_name, 
            user_screen_name=tweet.user_screen_name, 
            post_url=tweet.tweet_url
        )
    except Exception as e:
        logger.error(f"Failed to get media on tweet id ({tweet_url}): {e}.")
        await message.reply("An error occured. Please try again later.")
