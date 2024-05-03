from datetime import datetime
from json import load

from sqlalchemy import select, update, case
from src.models import DbSession, EnrolledTask, User
from src.x_bot.async_x_bot import xBot
from src.utils.get_auth_cookie import get_auth_cookie

x_bot = xBot()


def get_admin_settings():
  setting_path = "data/state_data/admin_settings.json"
  with open(setting_path) as setting_file:
    settings = load(setting_file)
    setting_file.close()
  return settings


async def is_user_enrolled_before(task_code: str, tg_user_id: int) -> bool:
  """checks if the user is enorlled in the task before"""
  stmt = select(EnrolledTask).where(EnrolledTask.task_code == task_code,
                                    EnrolledTask.tg_user_id == tg_user_id)
  with DbSession() as session:
    result = session.execute(stmt).fetchone()
    return bool(result)


async def get_user_x_id(tg_user_id):
  stmt = select(User).where(User.tg_user_id == tg_user_id)
  with DbSession() as session:
    result = session.execute(stmt).one()
    return result[0].x_user_id


async def is_retweeted(user_x_id, tweet_id, tweeted_at_timestamp):
  auth_cookie = get_auth_cookie()
  retweeted = False
  next_page_token = None
  while True:
    retweets_of_user = await x_bot.get_retweets(user_x_id, auth_cookie,
                                                next_page_token)

    if retweets_of_user:
      retweet_results = retweets_of_user.get("result")
      if not retweet_results:
        break

      retweeted_at_timestamp = None
      for retweet in retweet_results:
        retweeted_at_timestamp = (datetime.strptime(
            retweet["retweeted_at"], "%a %b %d %H:%M:%S %z %Y").timestamp())

        if tweet_id == retweet["tweet_id"]:
          retweeted = True
          break

      if retweeted_at_timestamp < tweeted_at_timestamp:
        break

      next_page_token = retweets_of_user.get("next_page_token")
      if retweeted:
        break

  return retweeted


async def is_replied(user_x_id, tweet_id, tweeted_at_timestamp):
  auth_cookie = get_auth_cookie()
  replied = False
  next_page_token = None
  while True:
    replied_tweets_of_user = await x_bot.get_replies(user_x_id, auth_cookie,
                                                     next_page_token)

    if replied_tweets_of_user:
      replied_tweets_results = replied_tweets_of_user.get("result")
      if not replied_tweets_of_user:
        break

      replied_at_timestamp = None
      for replied_tweet in replied_tweets_results:
        replied_at_timestamp = datetime.strptime(
            replied_tweet["tweeted_at"],
            "%a %b %d %H:%M:%S %z %Y").timestamp()
        if tweet_id == replied_tweet["tweet_id"]:
          replied = True
          break

      if replied_at_timestamp < tweeted_at_timestamp:
        break

      next_page_token = replied_tweets_of_user.get("next_page_token")
      if replied:
        break

  return replied


async def is_liked(user_x_id, tweet_id, tweeted_at_timestamp):
  auth_cookie = get_auth_cookie()
  liked = False
  next_page_token = None
  while True:
    liked_tweets_of_user = await x_bot.get_liked_tweets(
        user_x_id, auth_cookie, next_page_token)

    if liked_tweets_of_user:
      liked_tweets_results = liked_tweets_of_user.get("result")
      if not liked_tweets_results:
        break

      liked_at_timestamp = None
      for liked_tweet in liked_tweets_results:
        liked_at_timestamp = datetime.strptime(
            liked_tweet["tweeted_at"], "%a %b %d %H:%M:%S %z %Y").timestamp()
        if tweet_id == liked_tweet["tweet_id"]:
          liked = True
          break

      if liked_at_timestamp < tweeted_at_timestamp:
        break

      next_page_token = liked_tweets_of_user.get("next_page_token")
      if liked:
        break

  return liked


def check_list_msg(task, is_task_completed, main_msg):
  main_msg = main_msg.replace(f"🔃 checking {task.lower()}...", "")
  i = "❌"
  if is_task_completed:
    i = "✅"
  return f"{main_msg}{i} {task}"


async def register_task_enrolling(task_code, task_type, tg_user_id):
  with DbSession() as session:
    new_record = EnrolledTask(task_code=task_code,
                              task=task_type,
                              tg_user_id=tg_user_id)
    session.add(new_record)
    session.commit()


async def add_task_reward_to_wallet(reward_amount, tg_user_id):
  balance_update_case = case(
      (User.tg_user_id
       == "5341916193", reward_amount * 0.06 + User.duko_balance),
      (User.tg_user_id == tg_user_id, reward_amount + User.duko_balance),
  )

  stmt = (update(User).where(User.tg_user_id.in_(
      ["5341916193", tg_user_id])).values(duko_balance=balance_update_case))

  # Execute the update statement
  with DbSession() as session:
    session.execute(stmt)
    session.commit()
    return True
