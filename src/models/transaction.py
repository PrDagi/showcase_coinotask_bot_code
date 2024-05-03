from sqlalchemy import Column, BigInteger, Float, String, Enum, Index
from src.models import ModelsBase


class Transaction(ModelsBase):
  __tablename__ = "transactions"

  id = Column(BigInteger, primary_key=True, autoincrement=True)
  transaction_signature = Column(
      String(200), server_default=None)  # to track the tracsction
  amount = Column(Float)
  # pending=at strate ,completed= at amount reaches the user,waiting=>if payer have low amount wait him to diopside
  status = Column(Enum('pending',
                       'completed',
                       'failed',
                       name='transaction_status'),
                  server_default="pending")
  tg_user_id = Column(BigInteger)

  def __repr__(self):
    return "<Transaction(id=%s%,transaction_signature='%s', amount='%s', status='%s', tg_user_id='%s')>" % (
        self.id,
        self.transaction_signature,
        self.amount,
        self.status,
        self.tg_user_id,
    )
