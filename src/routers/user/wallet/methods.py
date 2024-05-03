from json import load
import aiohttp
import asyncio
from src.utils.env_vars import get_env_var
from src.models import DbSession, User, Transaction
from sqlalchemy import Update
import time


def get_admin_settings():
  setting_path = "data/state_data/admin_settings.json"
  with open(setting_path) as setting_file:
    settings = load(setting_file)
    setting_file.close()
  return settings


TX_API_URL = get_env_var("TX_API_URL")


def balance_card(tg_user_id) -> str:
  balance = get_wallet_balance(tg_user_id)
  return f"""
🪙 **$DUKO**
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-
💳 Balance: ```{balance}/$DUKO```
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-
"""


# get pending tx
# check it status if it confirmed update the amount
# allow him to withdrawal


def get_wallet_balance(tg_user_id):
  with DbSession() as session:
    total_amount = (session.query(
        User.duko_balance).where(User.tg_user_id == tg_user_id).first())

    balance = 0
    if total_amount:
      balance = total_amount[0]

    return balance


def get_pending_tx(tg_user_id):
  with DbSession() as session:
    row = (session.query(Transaction.amount).where(
        Transaction.tg_user_id == tg_user_id,
        Transaction.status == "pending",
    ).first())
    return row


def update_tx_status(tg_user_id, tx_signature, tx_amount, status="pending"):
  with DbSession() as session:
    if status == "pending":
      new_tx = Transaction(tg_user_id=tg_user_id,
                           transaction_signature=None,
                           amount=tx_amount,
                           status=status)
      session.add(new_tx)
    elif status == "completed":
      amount_update = (Update(User).values(duko_balance=User.duko_balance -
                                           tx_amount).where(
                                               User.tg_user_id == tg_user_id))
      session.execute(amount_update)
      tx_status_update = (Update(Transaction).values(
          status=status, transaction_signature=tx_signature).where(
              Transaction.tg_user_id == tg_user_id))
      session.execute(tx_status_update)
    else:
      tx_status_update = (Update(Transaction).values(
          status=status, transaction_signature=tx_signature).where(
              Transaction.tg_user_id == tg_user_id))
      session.execute(tx_status_update)
    session.commit()


async def transfer_token(tg_user_id, amount, sol_address, logging_msg):
  SETTINGS = get_admin_settings()
  send_from = SETTINGS["wallet_address"]
  tx_data = {
      "from": send_from,
      "to": sol_address,
      "amount": amount,
      "token": "DUKO",
  }

  tx_signature = None
  prev_msg = await logging_msg.reply(
      text="⌛ Processing the transaction,pleas wait...")

  # pending
  update_tx_status(tg_user_id, tx_signature, amount)
  prev_msg = await prev_msg.edit_text(
      text="⏳ Processing the transaction,pleas wait....")
  async with aiohttp.ClientSession(base_url=TX_API_URL) as session:
    async with session.post(url="/tx-api/transfer", json=tx_data) as tx_res:
      if tx_res.status == 200:
        tx_signature = (await tx_res.json())["data"]["signature"]
        # compeleted
        update_tx_status(tg_user_id, tx_signature, amount, "completed")
        await prev_msg.edit_text(text="✅ Transaction successfully completed.")
      else:
        # failed
        update_tx_status(tg_user_id, tx_signature, amount, "failed")
        await prev_msg.edit_text(
            text="❌ Transaction Failed: please try againg later")
