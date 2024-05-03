from sqlalchemy import Column, BigInteger, Float, Index
from src.models import ModelsBase


class User(ModelsBase):
  __tablename__ = "users"

  id = Column(BigInteger, primary_key=True, autoincrement=True)
  tg_user_id = Column(BigInteger)
  x_user_id = Column(BigInteger)
  duko_balance = Column(Float, server_default="0")

  def __repr__(self) -> str:
    return "<User(id='%s',tg_user_id='%s', x_user_id='%s', duko_balance='%s')>" % (
        self.id, self.tg_user_id, self.x_user_id, self.duko_balance)
