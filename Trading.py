
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

import random

# إعداد السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# الحد الأقصى للإشارات اليومية
MAX_SIGNALS_PER_DAY = 10

# بيانات المستخدمين
user_data = {}

# إشارات عشوائية تجريبية
signals = ["Buy", "Sell", "No clear signal"]

# لوحة تحكم البداية
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("Start Trading", callback_data="start_trading")],
        [InlineKeyboardButton("Market Status", callback_data="market_status")],
        [InlineKeyboardButton("Help", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

# لوحة خيارات المبالغ
def get_amount_menu():
    keyboard = [
        [InlineKeyboardButton("$5", callback_data="amount_5")],
        [InlineKeyboardButton("$10", callback_data="amount_10")],
        [InlineKeyboardButton("$25", callback_data="amount_25")],
        [InlineKeyboardButton("$40", callback_data="amount_40")]
    ]
    return InlineKeyboardMarkup(keyboard)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {"signals_today": 0, "wins": 0, "losses": 0}
    await update.message.reply_text("Welcome to the bot 🔥🫡", reply_markup=get_main_menu())

# تحكم بردود الضغط على الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "start_trading":
        await query.edit_message_text("Choose your amount:", reply_markup=get_amount_menu())

    elif query.data.startswith("amount_"):
        if user_data[user_id]["signals_today"] >= MAX_SIGNALS_PER_DAY:
            await query.edit_message_text("You've reached the maximum. Come back tomorrow. 🔻")
        else:
            signal = random.choice(signals)
            user_data[user_id]["signals_today"] += 1
            context.user_data["last_signal"] = signal
            await query.edit_message_text(f"Market Signal: {signal}", reply_markup=get_result_buttons())

    elif query.data == "market_status":
        status = random.choice(["Good", "Volatile"])
        await query.edit_message_text(f"Market Status: {status}")

    elif query.data == "help":
        await query.edit_message_text("To start, click on 'Start Trading'. Choose amount, get signal.")

    elif query.data == "win":
        user_data[user_id]["wins"] += 1
        await query.edit_message_text("Well done! ✅ Total Wins: {}".format(user_data[user_id]["wins"]))

    elif query.data == "lose":
        user_data[user_id]["losses"] += 1
        await query.edit_message_text("Don't worry! ❌ Total Losses: {}".format(user_data[user_id]["losses"]))

# أزرار ربح / خسارة
def get_result_buttons():
    keyboard = [
        [InlineKeyboardButton("✅ I won", callback_data="win"),
         InlineKeyboardButton("❌ I lost", callback_data="lose")]
    ]
    return InlineKeyboardMarkup(keyboard)

# تشغيل البوت
def main():
    import os
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
