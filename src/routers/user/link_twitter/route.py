from aiogram import Router, F
from aiogram.types import Message,CallbackQuery,ReplyKeyboardMarkup,KeyboardButton
from aiogram.filters import StateFilter,Command
from aiogram.fsm.context import FSMContext

from src.x_bot.async_x_bot import xBot
from src.utils.get_auth_cookie import get_auth_cookie
from src.routers.bot_route_list import BOT_ROUTES
from .methods import *

link_twitter_router = Router(name="link_twitter router")
x_bot = xBot()

@link_twitter_router.message(Command("link_twitter"))
async def ask_x_username(message: Message, state: FSMContext):
    await message.reply(
        text="𝕏 Enter your Twitter(X) Username?\n(e.g: @my_username)"
    )

    await state.set_state("LinkTwitterState:x_username")

@link_twitter_router.callback_query(F.data == "link_twitter")
async def ask_x_username(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.edit_text(
        text="𝕏 Enter your Twitter(X) Username?\n(e.g: @my_username)"
    )

    await state.set_state("LinkTwitterState:x_username")


@link_twitter_router.message(
    StateFilter("LinkTwitterState:x_username"),
    F.content_type == "text",
    F.text.regexp(r"^@[A-Za-z0-9_]+$"),
)
async def x_username(message: Message, state: FSMContext):
    processing_msg = await message.reply("𝕏 linking your twitter...")

    username = message.text.replace("@", "")
    tg_user_id = message.chat.id
    
    #! get user x id
    x_id = await x_bot.get_user_x_id(username,get_auth_cookie())
    if not x_id:
        await processing_msg.edit_text(text=f"⚠️ unable to link @{username},please try agin!")
        return

    #! check the username
    is_exist = is_username_exist(x_id)
    if is_exist:
        await processing_msg.edit_text(text="⚠️ the entered username(𝕏) exist,please try other!")
        return

    #! save the username
    save_username(tg_user_id,x_id)
    await processing_msg.delete()
    await message.reply(
        text=f"✅ you have successfully linked your twitter username.\n\nTap `🔍 Browse Tasks` button to see available tasks",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🔍 Browse Tasks")]
            ],
            resize_keyboard=True
        )
    )

    await state.clear()


@link_twitter_router.message(
    StateFilter("LinkTwitterState:x_username"),F.text.not_in(BOT_ROUTES)
)
async def incorrect_x_username(message: Message):
    await message.reply(text="⚠️ Please enter the correct twitter/x @username!")