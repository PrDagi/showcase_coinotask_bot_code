import threading
import asyncio

from fastapi import FastAPI
from aiogram import Dispatcher
from aiogram.types import BotCommand, Update

from src.tg_bot_instance import tGBot
from src.routers import Routers as all_routes
from src.models import ModelsBase, DbEngine

from src.x_bot.xtracker.notifcation_sender import send_notification
from src.x_bot.xtracker.x_tracker import track_tweets

WEBHOOK_URL = '.........'

app = FastAPI()

dp = Dispatcher()
dp.include_routers(*all_routes)


async def set_bot_cmd():
  commands = [
      BotCommand(command="/link_twitter",
                 description="add or change your twitter(x) username"),
      BotCommand(
          command="/wallet",
          description="view wallet balance and withdrawal tokens",
      ),
      BotCommand(
          command="/browse_tasks",
          description="view new available tasks",
      )
  ]
  await tGBot.set_my_commands(commands=commands)


async def on_startup():
  webhook_info = await tGBot.get_webhook_info()
  print(">>>>>>>>>>>>>>>>>b", webhook_info)
  # set webhook
  if webhook_info.url != WEBHOOK_URL:
    webhook_info = await tGBot.set_webhook(url=WEBHOOK_URL)
    print(">>>>>>>>>>>>>>>>>a", webhook_info)

  # set
  await set_bot_cmd()
  # Create the models table in the database
  ModelsBase.metadata.create_all(DbEngine)


@app.get("/")
async def test():
  return {"message": "Hello world"}


@app.post("/tg_webhook")
async def handle_webhook(update: dict):
  print(">>update", update)
  telegram_update = Update(**update)
  print(">>tg update", telegram_update)
  await dp.feed_webhook_update(tGBot, telegram_update)


async def bg_tasks():
  await asyncio.gather(track_tweets(), send_notification())


def main():
  # set up
  app.add_event_handler("startup", on_startup)

  # run it
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
  main_thread = threading.Thread(target=main)

  try:
    main_thread.start()
    asyncio.run(bg_tasks())
  except Exception as e:
    print("Error:", e)
