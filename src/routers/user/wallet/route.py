from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from aiogram.filters import Command, StateFilter
from aiogram.enums import ParseMode

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.utils.auth_middleware import AuthMiddleware
from src.routers.bot_route_list import BOT_ROUTES
from .methods import *

wallet_router = Router(name="User Wallet Router")


class WithdrawalForm(StatesGroup):
  sol_address = State()
  amount = State()
  confirm = State()


wallet_router.message.middleware(AuthMiddleware())


@wallet_router.message(Command("wallet"))
async def handle_wallet_cmd(message: Message):
  prev_msg = await message.reply(text="🔃 processing... ")

  tg_user_id = message.chat.id
  await prev_msg.edit_text(
      text=balance_card(tg_user_id),
      reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
          InlineKeyboardButton(
              text="📤 Withdraw",
              callback_data="user_wallet:withdraw",
          )
      ]]),
      parse_mode=ParseMode.MARKDOWN_V2,
  )


# user_wallet:withdraw
@wallet_router.callback_query(F.data == "user_wallet:withdraw")
async def ask_withdrawal_amount(query: CallbackQuery, state: FSMContext):
  tg_user_id = query.message.chat.id

  pending_tx = get_pending_tx(tg_user_id)
  if pending_tx:
    await query.answer(
        text=
        "⚠️ The previous withdrawal request is still being processed. Please wait for the transaction to complete, or try again later.",
        show_alert=True)
    return

  await query.message.edit_text("""
1️⃣ your solana address to receive the $tokens?
""")

  await state.set_state(WithdrawalForm.sol_address)


@wallet_router.message(
    StateFilter(WithdrawalForm.sol_address),
    F.text.len() > 31,  # sol is b/n 32-44
    F.text.len() < 45,
)
async def sol_address(message: Message, state: FSMContext):
  SETTINGS = get_admin_settings()
  sol_address = message.text.strip()

  min_w = SETTINGS["minimal_withdrawal"]
  await state.set_data({"sol_address": sol_address})

  await message.reply(f"""
2️⃣ Enter the amount you want to withdraw:

>> minimal withdrawal amount is {min_w}
""")

  await state.set_state(WithdrawalForm.amount)


@wallet_router.message(WithdrawalForm.amount, F.text.not_in(BOT_ROUTES))
async def get_withdrawal_amount(message: Message, state: FSMContext):
  SETTINGS = get_admin_settings()
  prev_msg = await message.reply(text="🔃 processing... ")

  tg_user_id = message.chat.id
  total_amount = get_wallet_balance(tg_user_id)
  amount = message.text

  if not amount.isdigit():
    await prev_msg.edit_text(
        text="⚠️ Please enter the withdrawal amount using digits only")
    return

  amount = float(amount)
  if amount > total_amount:
    await prev_msg.edit_text(
        text=
        "⚠️ you have no enough funds to withdraw that amount. Please enter a valid withdrawal amount."
    )
    return

  min_w_amount = SETTINGS["minimal_withdrawal"]
  if amount < min_w_amount:
    await prev_msg.edit_text(
        text=
        f"⚠️ The minimum withdrawal amount is {min_w_amount}. Please enter a higher withdrawal amount."
    )
    return

  await prev_msg.delete()
  await message.reply(
      text=f"""
You're about to withdraw:

💲 Amount: {amount}/$DUKO

3️⃣ Confirm your withdrawal:
""",
      reply_markup=ReplyKeyboardMarkup(
          keyboard=[[
              KeyboardButton(text="❌ Cancel"),
              KeyboardButton(text="✅ Confirm")
          ], [KeyboardButton(text="🔍 Browse Tasks")]],
          resize_keyboard=True,
      ),
  )
  await state.update_data({"withdrawal_amount": amount})
  await state.set_state(WithdrawalForm.confirm)


@wallet_router.message(WithdrawalForm.confirm, F.text == "✅ Confirm")
async def confirm_handler(message: Message, state: FSMContext):
  processing_msg = await message.reply(
      text="🔃 Processing your withdrawal request...",
      reply_markup=ReplyKeyboardRemove(),
  )
  tg_user_id = message.chat.id
  session_data = await state.get_data()

  await processing_msg.delete()
  await transfer_token(tg_user_id, session_data["withdrawal_amount"],
                       session_data["sol_address"], message)
  await state.clear()


@wallet_router.message(WithdrawalForm.confirm, F.text == "❌ Cancel")
async def cancel_handler(message: Message, state: FSMContext):
  await message.reply(text="""
Your withdrawal request has been canceled.

To go back to your wallet, click /wallet.
""",
                      reply_markup=ReplyKeyboardMarkup(
                          keyboard=[[KeyboardButton(text="🔍 Browse Tasks")]],
                          resize_keyboard=True))
  await state.clear()


@wallet_router.message(StateFilter(WithdrawalForm.sol_address),
                      F.text.not_in(BOT_ROUTES))
async def incorrect_sol_address(message: Message):
  await message.reply(text="⚠️ Please enter the correct Solana address!")
