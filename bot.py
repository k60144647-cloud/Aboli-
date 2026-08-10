import json
import os
import random
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ====== توکن ربات (همون توکن خودت) ======
TOKEN = "8873887420:AAHINF0T2CDM_rs41XYyYSORAONvYFJETn8"

# ====== تنظیمات بازی ======
DATA_FILE = "data.json"
COOLDOWN_MINUTES = 5  # هر ۵ دقیقه یک بار
POINT_RANGE = (1, 50)  # محدوده امتیاز شانسی
TRIGGER_WORDS = ["ابول", "ابولی"]  # کلمات کلیدی

# ====== توابع مدیریت فایل داده ======
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
        "در گروه عضو شوید و کلمه «ابول» یا «ابولی» را بفرستید تا شانس خود را امتحان کنید!\n"
        "هر ۵ دقیقه یک بار می‌توانید امتیاز بگیرید. 🎲"
    )

# ====== پردازش پیام‌های گروه ======
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # فقط پیام‌های متنی در گروه را پردازش کن
    if not update.message or not update.message.text or update.message.chat.type not in ["group", "supergroup"]:
        return

    user_id = str(update.message.from_user.id)
    username = update.message.from_user.username or "کاربر"
    text = update.message.text.strip()

    # بررسی کلمات کلیدی (مقایسه غیرحساس به حروف بزرگ/کوچک)
    if text.lower() not in [w.lower() for w in TRIGGER_WORDS]:
        return

    # بارگذاری داده‌ها
    data = load_data()

    # مقداردهی اولیه برای کاربر جدید
    if user_id not in data:
        data[user_id] = {"points": 0, "last_claim": None}

    user_data = data[user_id]

    # بررسی زمان انقضای ۵ دقیقه
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

    # تولید امتیاز شانسی
    point = random.randint(POINT_RANGE[0], POINT_RANGE[1])
    user_data["points"] += point
    user_data["last_claim"] = now.isoformat()

    # ذخیره داده‌ها
    save_data(data)

    # ارسال پیام موفقیت
    await update.message.reply_text(
        f"🔥 ابول ابول !\n\n"
        f"🎯 شما عدد شانسی **{point}** ابول‌پوینت گرفتید!\n"
        f"💰 کل ابول‌پوینت‌های شما: **{user_data['points']}**\n\n"
        f"⭐ دوباره ۵ دقیقه دیگه می‌تونی تلاش کنی!"
    )

# ====== دستور امتیاز (اختیاری) ======
async def my_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    data = load_data()
    if user_id in data:
        points = data[user_id]["points"]
        await update.message.reply_text(f"💎 {update.message.from_user.username} عزیز، کل ابول‌پوینت‌های شما: **{points}**")
    else:
        await update.message.reply_text("⛔ شما هنوز هیچ امتیازی کسب نکردید. اولین «ابول» رو بفرست!")

# ====== راه‌اندازی اصلی (روش Polling ساده) ======
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("points", my_points))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # اجرا با روش Polling (بدون نیاز به دامنه و وب‌هوک)
    print("🤖 ربات ابول‌پوینت روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
