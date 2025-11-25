import asyncio
import logging
from decouple import config

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from handlers import router 

async def main():
    logging.basicConfig(level=logging.INFO)
    token = config('BOT_TOKEN')
    
    if not token:
        raise RuntimeError('Token was not provided')
    
    dispatcher = Dispatcher()
    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    dispatcher.include_router(router)
    
    await dispatcher.start_polling(bot)
    
if __name__ == '__main__':
    asyncio.run(main())
