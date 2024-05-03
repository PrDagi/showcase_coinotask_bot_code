from aiogram import Router, F
from aiogram.types import CallbackQuery

from ast import literal_eval
from .methods import *

tweet_task_router = Router(name="Tweet Task Router")


@tweet_task_router.callback_query(F.data.startswith("x?"))
async def claim_x_reward(query: CallbackQuery):
  message = query.message
  task_title = message.text.split("\n")[0]
  task_action_buttons = message.reply_markup
  prev_msg = await message.edit_text(text="🔃 processing... ")

  query_data = literal_eval(query.data.split("?")[-1])

  tg_user_id = message.chat.id
  tweet_id = str(query_data["i"])
  tweeted_at_timestamp = query_data["d"]
  user_x_id = await get_user_x_id(tg_user_id)

  is_enrolled_before = await is_user_enrolled_before(task_code=tweet_id,
                                                     tg_user_id=tg_user_id)
  if is_enrolled_before:
    await prev_msg.edit_text(
        text=
        "⚠️ Attempting to enroll in agin is not allowed. try to enroll on other task."
    )
    return

  #! start
  main_msg = f"""
{task_title}

Task Completion Checks List:
🔃 checking retweet...
"""
  prev_msg = await prev_msg.edit_text(text=main_msg)

  #! retweet
  retweeted = await is_retweeted(
      user_x_id=user_x_id,
      tweet_id=tweet_id,
      tweeted_at_timestamp=tweeted_at_timestamp,
  )
  prev_msg = await prev_msg.edit_text(
      text=check_list_msg("Retweet", retweeted, main_msg))

  #! reply
  prev_msg = await prev_msg.edit_text(text=prev_msg.text +
                                      "\n🔃 checking reply...")
  replied = await is_replied(
      user_x_id=user_x_id,
      tweet_id=tweet_id,
      tweeted_at_timestamp=tweeted_at_timestamp,
  )
  prev_msg = await prev_msg.edit_text(
      text=check_list_msg("Reply", replied, prev_msg.text))

  #! like
  prev_msg = await prev_msg.edit_text(text=prev_msg.text +
                                      "\n🔃 checking like...")
  liked = await is_liked(
      user_x_id=user_x_id,
      tweet_id=tweet_id,
      tweeted_at_timestamp=tweeted_at_timestamp,
  )
  prev_msg = await prev_msg.edit_text(
      text=check_list_msg("Like", liked, prev_msg.text))

  is_task_completed = retweeted and replied and liked
  if not is_task_completed:
    await prev_msg.edit_text(
        text=query.message.text + "\n\n⚠️ Please complete the remaining tasks",
        reply_markup=task_action_buttons,disable_web_page_preview=True
    )
    return

  SETTINGS = get_admin_settings()
  amount = SETTINGS["reward_amount"] * 3
  #! make the user as enrolled in the task
  await register_task_enrolling(tweet_id, "tweeting", tg_user_id)
  #! give them the award
  await add_task_reward_to_wallet(amount, tg_user_id)
  await prev_msg.edit_text(text=prev_msg.text +
                           f"\n\n💰 you earned {amount} $tokens")
