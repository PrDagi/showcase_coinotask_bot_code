from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Text, Index
from src.models import ModelsBase
from datetime import datetime


class Task(ModelsBase):
  __tablename__ = "tasks"

  id = Column(BigInteger, primary_key=True, autoincrement=True)
  task_code = Column(String(50))
  task = Column(String(50))
  task_meta = Column(Text)
  task_created_at = Column(DateTime, default=datetime.now())
  is_notified_to_users = Column(Boolean, default=False)

  def __repr__(self) -> str:
    return "<Task(id='%s',task_code='%s', task='%s', task_meta='%s', task_created_at='%s', is_notified_to_users='%s')>" % (
        self.id, self.task_code, self.task, self.task_meta,
        self.task_created_at, self.is_notified_to_users)
