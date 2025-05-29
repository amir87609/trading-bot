
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import random
from datetime import datetime

TOKEN = "8080679821:AAE1ULTurmkGteGSqkCorgINLRniQEJ_OOM"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

user_data = {}
daily_signals_limit = 10

def get_market_status():
    return random.choice(["✅ السوق جيد للتداول", "⚠️ السوق متذبذب، كن حذرًا!"])

def get_trade_signal():
    return random.choice(["📉 بيع (Sell)", "📈 شراء (Buy)"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = datetime.now()

    if user_id not in user_data or user_data[user_id]["date"] != now.date():
        user_data[user_id] = {
            "date": now.date(),
            "signals_used": 0,
            "wins": 0,
            "losses": 0,
            "amount": 5
        }

    keyboard = [
        [InlineKeyboardButton("📊 تحليل الآن", callback_data="analyze")],
        [InlineKeyboardButton("💸 تداول الآن", callback_data="trade_options")],
        [InlineKeyboardButton("📈 النتائج", callback_data="results")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🔥 Welcome to the bot 🔥🫡",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    now = datetime.now()

    if user_id not in user_data or user_data[user_id]["date"] != now.date():
        user_data[user_id] = {
            "date": now.date(),
            "signals_used": 0,
            "wins": 0,
            "losses": 0,
            "amount": 5
        }

    data = query.data

    if data == "analyze":
        await query.edit_message_text(text=get_market_status())

    elif data == "trade_options":
        amounts = [5, 10, 25, 40]
        buttons = [[InlineKeyboardButton(f"${amt}", callback_data=f"set_amount_{amt}")] for amt in amounts]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(text="💰 اختر قيمة التداول", reply_markup=reply_markup)

    elif data.startswith("set_amount_"):
        amount = int(data.split("_")[-1])
        user_data[user_id]["amount"] = amount
        if user_data[user_id]["signals_used"] >= daily_signals_limit:
            await query.edit_message_text(text="You've reached the maximum. Come back tomorrow. 🔻")
        else:
            signal = get_trade_signal()
            user_data[user_id]["signals_used"] += 1
            buttons = [
                [InlineKeyboardButton("✅ تم الربح", callback_data="win"),
                 InlineKeyboardButton("❌ خسارة", callback_data="lose")]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(
                text=f"🔔 إشارة اليوم: {signal}\n💵 المبلغ: ${amount}",
                reply_markup=reply_markup
            )

    elif data == "win":
        user_data[user_id]["wins"] += 1
        await query.edit_message_text(text="🎉 مبروك ياوحشش! تم تسجيل الصفقة كربح ✅")

    elif data == "lose":
        user_data[user_id]["losses"] += 1
        await query.edit_message_text(text="😢 تم تسجيل الصفقة كخسارة ❌")

    elif data == "results":
        wins = user_data[user_id]["wins"]
        losses = user_data[user_id]["losses"]
        await query.edit_message_text(
            text=f"📊 نتائج اليوم:\n✅ عدد الربح: {wins}\n❌ عدد الخسارة: {losses}"
        )

    elif data == "help":
        help_msg = (
            "👋 هذا البوت يعطيك إشارات بيع/شراء يومية بناءً على تحليل السوق باستخدام مؤشرات محترفة.\n"
            "1. اضغط 'تحليل الآن' لرؤية حالة السوق.\n"
            "2. اضغط 'تداول الآن' وحدد المبلغ للحصول على إشارة.\n"
            "3. سجل نتيجة الصفقة (ربح أو خسارة).\n"
            "4. لا يمكنك تجاوز 10 إشارات يوميًا.\n\n🚀 بالتوفيق!"
        )
        await query.edit_message_text(text=help_msg)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()
