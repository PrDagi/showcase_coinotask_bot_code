from aiogram import Bot
from src.utils.env_vars import get_env_var

bot_token = get_env_var("BOT_TOKEN")
tGBot = Bot(token=bot_token)