import json
import os
import random
import time
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ====== توکن ربات (همون توکن خودت) ======
TOKEN = "8873887420:AAHINF0T2CDM_rs41XYyYSORAONvYFJETn8"

# ====== تنظیمات بازی ======
DATA_FILE = "data.json"
COOLDOWN_MINUTES = 5
POINT_RANGE = (1, 50)
TRIGGER_WORDS = ["ابول", "ابولی"]

# ====== توابع ذخیره و بارگذاری ======
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ====== دستور استارت ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 سلام! من ربات ابول‌پوینت هستم.\n"
        "تو گروه عضو شو و «ابول» یا «ابولی» بفرست تا شانس‌ت رو امتحان کنی!\n"
        "هر ۵ دقیقه یک بار می‌تونی امتیاز بگیری. 🎲"
    )

# ====== پردازش پیام‌ها ======
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or update.message.chat.type not in ["group", "supergroup"]:
        return

    user_id = str(update.message.from_user.id)
    username = update.message.from_user.username or "کاربر"
    text = update.message.text.strip()

    if text.lower() not in [w.lower() for w in TRIGGER_WORDS]:
        return

    data = load_data()

    if user_id not in data:
        data[user_id] = {"points": 0, "last_claim": None}

    user_data = data[user_id]
    now = datetime.now()

    if user_data["last_claim"]:
        last_time = datetime.fromisoformat(user_data["last_claim"])
        diff = now - last_time
        if diff.total_seconds() < COOLDOWN_MINUTES * 60:
            remaining = int((COOLDOWN_MINUTES * 60) - diff.total_seconds())
            minutes = remaining // 60
            seconds = remaining % 60
            await update.message.reply_text(
                f"⏳ {username} عزیز، هنوز {minutes} دقیقه و {seconds} ثانیه مونده تا بتونی دوباره امتیاز بگیری! 🕒"
            )
            return

    point = random.randint(POINT_RANGE[0], POINT_RANGE[1])
    user_data["points"] += point
    user_data["last_claim"] = now.isoformat()

    save_data(data)

    await update.message.reply_text(
        f"🔥 ابول ابول !\n\n"
        f"🎯 شما عدد شانسی **{point}** ابول‌پوینت گرفتید!\n"
        f"💰 کل ابول‌پوینت‌های شما: **{user_data['points']}**\n\n"
        f"⭐ دوباره ۵ دقیقه دیگه می‌تونی تلاش کنی!"
    )

# ====== دستور امتیاز ======
async def my_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    data = load_data()
    if user_id in data:
        points = data[user_id]["points"]
        await update.message.reply_text(f"💎 کل ابول‌پوینت‌های شما: **{points}**")
    else:
        await update.message.reply_text("⛔ هنوز هیچ امتیازی نداری. اولین «ابول» رو بفرست!")

# ====== اجرای اصلی ======
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("points", my_points))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # روش اجرا روی Railway (وب‌هوک)
    port = int(os.environ.get("PORT", 8443))
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TOKEN,
        webhook_url=f"https://{os.environ.get('RAILWAY_STATIC_URL')}/{TOKEN}"
    )
    # اگه خواستی روی سیستم خودت تست کنی، دو خط بالا رو کامنت کن و خط پایین رو فعال کن:
    # app.run_polling()

if __name__ == "__main__":
    main()
