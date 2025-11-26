__all__ = ('router',)

from aiogram import Router 
from .user_handler import router as user_router
from .x_handler.handle_media import router as x_router

router = Router(name='main')
router.include_routers(
    user_router, 
    x_router,
)
