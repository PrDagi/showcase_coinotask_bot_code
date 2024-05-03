from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from .methods import *

browse_tasks_router = Router(name="Brose Tasks Router")


@browse_tasks_router.message(Command("browse_tasks"))
@browse_tasks_router.message(F.text == "🔍 Browse Tasks")
async def browse_tasks(message: Message):
  loading_msg = await message.reply(text="🔃 browsing tasks... ")
  tg_user_id = message.chat.id
  await show_available_tasks(1, tg_user_id, loading_msg)


@browse_tasks_router.callback_query(F.data.startswith("load_more_task:"))
async def load_more_tasks(query: CallbackQuery):
  await query.answer()

  loading_msg = await query.message.edit_text(text="🔃 browsing tasks... ")
  tg_user_id = query.from_user.id
  page = int(query.data.split(":")[-1])
  await show_available_tasks(page, tg_user_id, loading_msg)
