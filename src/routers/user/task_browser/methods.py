from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from json import load
from ast import literal_eval
from math import ceil
from asyncio import sleep
from datetime import datetime

from src.models import Task, EnrolledTask, DbSession
from sqlalchemy import select, not_, desc


def get_admin_settings():
  setting_path = "data/state_data/admin_settings.json"
  with open(setting_path) as setting_file:
    settings = load(setting_file)
    setting_file.close()
  return settings


def query_tasks(page, tg_user_id):
  per_page = 5
  offset = (page - 1) * per_page

  with DbSession() as session:
    enrolled_tasks = select(
        EnrolledTask.task_code).where(EnrolledTask.tg_user_id == tg_user_id)

    # First, count the total number of tasks excluding enrolled tasks
    total_tasks = (session.query(Task).filter(
        not_(Task.task_code.in_(enrolled_tasks))).count())

    # Then, fetch the tasks for the current page, excluding enrolled tasks
    tasks = (session.query(Task).filter(
        not_(Task.task_code.in_(enrolled_tasks))).order_by(desc(
            Task.id)).limit(per_page).offset(offset).all())

    return {"results": tasks, "page": page, "total": total_tasks}


async def show_available_tasks(page, tg_user_id, task_wrapper_msg: Message):
  tasks = query_tasks(page, tg_user_id)

  results = tasks.get("results")
  if results:
    total_pages = ceil(tasks["total"] / 5)
    current_page = tasks["page"]

    prev_msg = await task_wrapper_msg.edit_text(
        f"▼ Task Browsing Page: {current_page} out of {total_pages}")
    for result in results:
      task_meta = literal_eval(result.task_meta)
      msg_body = None
      reply_buttons = None
      if result.task == "joining_chats":
        msg_body = tg_task_card(task_meta)
        reply_buttons = action_buttons(chat_id=result.task_code)
      else:
        tweeted_datetime = tweeted_date_fmt(task_meta["tweeted_at"])
        tweet_id = result.task_code
        msg_body = x_task_card(task_meta, tweeted_datetime, tweet_id)
        reply_buttons = action_buttons(tweet_id=tweet_id,
                                       tweeted_datetime=tweeted_datetime)

      #! send the msg
      prev_msg = await prev_msg.reply(text=msg_body,
                                      reply_markup=reply_buttons,
                                      parse_mode="html",
                                      disable_web_page_preview=True)
      await sleep(0.3)

    next_page = current_page + 1
    if current_page < total_pages:
      await prev_msg.reply(
          text=f"Go To Next Page ▼",
          reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
              InlineKeyboardButton(text=f"➡️ Page {next_page}",
                                   callback_data=f"load_more_task:{next_page}")
          ]]))
  else:
    await task_wrapper_msg.edit_text(text="No new available task")


def tweeted_date_fmt(tweeted_date):
  tweeted_datetime = datetime.strptime(tweeted_date, "%a %b %d %H:%M:%S %z %Y")

  return tweeted_datetime


def x_task_card(task_meta, tweeted_datetime, tweet_id):
  SETTINGS = get_admin_settings()

  reward_amount = SETTINGS["reward_amount"]
  temp = """
<b>Engage with <a href="https://x.com/{username}">@{username}</a> {posted_at} tweet!</b>

<b>📃 Task</b>: Retweet,Reply,Like
<b>💰 Reward</b>: {reward_amount} tokens for each action
<b>☑ Complete Task</b>: https://x.com/{username}/status/{tweet_id}
"""
  return temp.format(username=task_meta["username"],
                     posted_at=tweeted_datetime.strftime("%a %b %d,%Y"),
                     reward_amount=reward_amount,
                     tweet_id=tweet_id)


def tg_task_card(task_meta):
  SETTINGS = get_admin_settings()

  reward_amount = SETTINGS["reward_amount"]
  temp = """
<b>Join {chat_title} {chat_type}</b>

<b>📃 Task</b>: Joining Chat
<b>💰 Reward</b>: {reward_amount} token
<b>☑ Complete Task</b>: {join_link}
"""
  return temp.format(chat_title=task_meta["chat_title"],
                     chat_type=task_meta["chat_type"],
                     reward_amount=reward_amount,
                     join_link=task_meta["task_meta"])


def action_buttons(tweet_id=None, tweeted_datetime=None, chat_id=None):
  kbd = []
  if tweet_id:
    tweeted_at = datetime.timestamp(tweeted_datetime)
    kbd.append([
        InlineKeyboardButton(text="🔻 Claim Reward",
                             callback_data="x?{'i':" + str(tweet_id) +
                             ",'d':" + str(tweeted_at) + "}")
    ])
  else:
    kbd.append([
        InlineKeyboardButton(text="🔻 Claim Reward",
                             callback_data=f"tg?i={chat_id}")
    ])

  return InlineKeyboardMarkup(inline_keyboard=kbd)
