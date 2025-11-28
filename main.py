import asyncio
import logging
from decouple import config

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.methods import DeleteWebhook
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from handlers.user_handler import router

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s | %(filename)s | %(funcName)s | %(message)s'
    )
    token = config('BOT_TOKEN')
    
    if not token:
        raise RuntimeError('Token was not provided')
    
    session = AiohttpSession(
        api=TelegramAPIServer.from_base(base=config("LOCAL_BOT_URL"))
    )
    
    dispatcher = Dispatcher()
    
    bot = Bot(
        token=token,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    dispatcher.include_router(router)
    
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dispatcher.start_polling(bot, skip_updates=True)
    
if __name__ == '__main__':
    asyncio.run(main())
