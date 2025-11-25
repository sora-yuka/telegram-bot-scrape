__all__ = ('router',)

from aiogram import Router 
from .user_handler import router as user_router

router = Router(name='main')
router.include_routers(
    user_router, 
    # list other routers...
)
