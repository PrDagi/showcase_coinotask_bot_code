from aiogram import Router, F
from aiogram.types import CallbackQuery

from .methods import *


tg_task_router = Router(name="Tg Task Router")

@tg_task_router.callback_query(F.data.startswith("tg?"))
async def tg_task_verifier(query: CallbackQuery):
    chat_to_join_id = query.data.split("=")[-1]
    tg_user_id = query.message.chat.id
    bot = query.message.bot
    prev_msg = await query.message.edit_text(text="🔃 processing... ")
    task_action_buttons = query.message.reply_markup

    is_enrolled_before = await is_user_enrolled_before(
        task_code=chat_to_join_id, tg_user_id=tg_user_id
    )
    if is_enrolled_before:
        await prev_msg.edit_text(
            text="⚠️ Attempting to enroll in agin is not allowed. try to enroll on other task."
        )
        return

    is_joined = await is_joined_the_chat(tg_user_id, chat_to_join_id, bot)
    if is_joined == "False":
        await prev_msg.delete()
        return

    task_title = query.message.text.split("\n")[0]
    if not is_joined:
        await prev_msg.edit_text(
            text=query.message.text + "\n\n⚠️ Please join the chat",
            reply_markup=task_action_buttons,disable_web_page_preview=True
        )
        return

    SETTINGS = get_admin_settings()
    amount = SETTINGS["reward_amount"]
    #! make the user as enrolled in the task
    await register_task_enrolling(chat_to_join_id, tg_user_id,"joining_chats")
    #! give them the award
    await add_task_reward_to_wallet(amount, tg_user_id)
    await prev_msg.edit_text(
        text=task_title + f"\n\n💰 you earned {amount} $tokens"
    )