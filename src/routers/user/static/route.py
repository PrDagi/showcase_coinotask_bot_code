from aiogram import Router,F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from html import escape
from src.models import User, DbSession


static_router = Router(name="Static Router")

def is_registered(tg_user_id):
    with DbSession() as session:
        q_result = (
            session.query(User.id)
            .where(User.tg_user_id == tg_user_id)
            .first()
        )
        return bool(q_result)


@static_router.message(F.text.regexp(r"^/start$"))
async def welcome(message: Message,state: FSMContext):
    processing_msg = await message.answer(text="🔃 processing... ")

    overview_msg = f"""
Welcome <b>{message.from_user.first_name}</b>,This is <b>WORK FOR YOUR BAG 🤖</b>

you will never receive a notification from me without earning something.

It easy:
1️⃣ you receive a notification about new tasks
2️⃣ you complete tasks like
-> (liking,retweeting,replying) for a tweet task
-> joining telegram group/channels task
3️⃣ you earn tokens 💰

Tap the ☰ menu to see all available commands
"""

    tg_user_id = message.from_user.id
    if not is_registered(tg_user_id):
        register_msg = """
To start i need only to know your Twitter(X) username,send me here the username with the @...
"""
        overview_msg += register_msg
        await state.set_state("LinkTwitterState:x_username")
      

    await processing_msg.edit_text(text=overview_msg,parse_mode=ParseMode.HTML)