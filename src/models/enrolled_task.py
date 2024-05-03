from sqlalchemy import Column, String, BigInteger, Index
from src.models import ModelsBase


class EnrolledTask(ModelsBase):
  __tablename__ = "enrolled_tasks"

  id = Column(BigInteger, primary_key=True, autoincrement=True)
  # Unique identifier of the task. It will be tweet_id for tweet tasks, and chat_id for Telegram tasks.
  task_code = Column(String(50))
  # To store task names as a string, e.g., for tweet tasks "retweet/like/ ..."" or for tg "join_channel/join_group
  task = Column(String(50))
  # Identifier of the user who enrolled in the task
  tg_user_id = Column(BigInteger)

  def __repr__(self):
    return "<EnrolledTask(id='%s',task_code='%s', task='%s', tg_user_id='%s', is_earned='%s')>" % (
        self.id,
        self.task_code,
        self.task,
        self.tg_user_id,
        self.is_earned,
    )
