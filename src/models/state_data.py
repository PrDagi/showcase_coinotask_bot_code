from sqlalchemy import Column,Integer
from sqlalchemy.dialects.postgresql import JSONB
from src.models import ModelsBase


class StateData(ModelsBase):
  __tablename__ = "state_data"

  id = Column(Integer, primary_key=True, autoincrement=True)
  x_tracked_accounts = Column(JSONB)
  admin_settings = Column(JSONB)

  def __repr__(self) -> str:
    return "<StateData(x_tracked_accounts='%s',admin_settings='%s')>" % (
      self.x_tracked_accounts,      
      self.admin_settings
    )
