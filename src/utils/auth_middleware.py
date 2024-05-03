from aiogram import BaseMiddleware
from aiogram.types import Message,InlineKeyboardMarkup,InlineKeyboardButton

from src.models import User, DbSession


class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message,data):
        processing_msg = await event.reply(text="🔃 processing... ")
        
        tg_user_id = event.from_user.id
        if self.is_registered(tg_user_id):
            await processing_msg.delete()
            return await handler(event,data)
        else:
            msg = """
⚠️ Please ⬇️ link your twitter username first to access the bot.
"""
            await processing_msg.delete()
            await event.reply(text=msg,reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="𝕏 Link ",callback_data="link_twitter")]
                ]
            ))


    def is_registered(self,tg_user_id):
        with DbSession() as session:
            q_result = (
                session.query(User.id)
                .where(User.tg_user_id == tg_user_id)
                .first()
            )
            return bool(q_result)
