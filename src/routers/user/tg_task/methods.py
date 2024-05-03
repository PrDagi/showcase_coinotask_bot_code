from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest

from json import load

from sqlalchemy import select, update, case
from src.models import DbSession, EnrolledTask, User


def get_admin_settings():
  setting_path = "data/state_data/admin_settings.json"
  with open(setting_path) as setting_file:
    settings = load(setting_file)
    setting_file.close()
  return settings


async def is_user_enrolled_before(task_code: str, tg_user_id: str) -> bool:
  """checks if the user is enorlled in the task before"""
  stmt = select(EnrolledTask).where(EnrolledTask.task_code == task_code,
                                    EnrolledTask.tg_user_id == tg_user_id)
  with DbSession() as session:
    result = session.execute(stmt).fetchone()
    return bool(result)


async def is_joined_the_chat(user_id, chat_id, bot) -> bool:
  """
    Checks if the user is a member of the specified channel/group
    """

  try:
    member_info = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)

    if member_info.status == ChatMemberStatus.LEFT:
      return False
    else:
      return True

  except TelegramBadRequest as e:
    return "False"


async def register_task_enrolling(task_code,
                                  tg_user_id,
                                  task_type="joining_chats"):
  with DbSession() as session:
    new_record = EnrolledTask(task_code=task_code,
                              task=task_type,
                              tg_user_id=tg_user_id)
    session.add(new_record)
    session.commit()


async def add_task_reward_to_wallet(reward_amount, tg_user_id):
  stmt = (update(User).where(User.tg_user_id == tg_user_id])).values(duko_balance=reward_amount + User.duko_balance))

  # Execute the update statement
  with DbSession() as session:
    session.execute(stmt)
    session.commit()
    return True
