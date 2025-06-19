import logging
import os
from datetime import datetime, timedelta
from telegram import Bot
from telegram.ext import ApplicationBuilder, ContextTypes
import asyncio

# بيانات القنوات والتوكن
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PUBLIC_CHANNEL_ID = os.environ.get("PUBLIC_CHANNEL_ID")
PRIVATE_CHANNEL_ID = os.environ.get("PRIVATE_CHANNEL_ID")

# إعدادات السجل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# توصيات اليوم (مثال ثابت – بتربط لاحقًا بفلاتر)
recommendations = [
    {"ticker": "XYZ", "entry": 2.35},
    {"ticker": "ABC", "entry": 1.70},
    {"ticker": "DEF", "entry": 4.20}
]

# حساب الأهداف والوقف بناءً على نقطة الدخول
def get_targets(entry):
    return {
        "t1": round(entry * 1.08, 2),
        "t2": round(entry * 1.15, 2),
        "t3": round(entry * 1.25, 2),
        "t4": round(entry * 1.40, 2),
        "sl": round(entry * 0.91, 2)
    }

# إرسال التوصيات
async def send_recommendations(bot):
    for rec in recommendations:
        prices = get_targets(rec["entry"])
        msg = (
            f"{rec['ticker']}\n"
            f"دخول {rec['entry']}\n"
            f"الأهداف: {prices['t1']} - {prices['t2']} - {prices['t3']} - {prices['t4']}\n"
            f"وقف الخسارة: {prices['sl']}"
        )
        await bot.send_message(chat_id=PRIVATE_CHANNEL_ID, text=msg)
        await asyncio.sleep(1)

# إرسال ملخص النتايج في آخر اليوم
async def send_results(bot):
    results = [
        "XYZ دخول 2.35 حقق 3.00 - النسبة 40% 💰",
        "ABC دخول 1.70 لم تحقق دخول",
        "DEF دخول 4.20 ضربت الوقف ❌ - النسبة -9%"
    ]
    final = "\n".join(results)
    await bot.send_message(chat_id=PUBLIC_CHANNEL_ID, text=f"نتائج اليوم:\n{final}")
    await bot.send_message(chat_id=PRIVATE_CHANNEL_ID, text=f"نتائج اليوم:\n{final}")

# المشغل
async def main():
    bot = Bot(token=BOT_TOKEN)
    now = datetime.now().strftime("%H:%M")
    if now.startswith("11:0"):  # البري ماركت الساعة 11 صباحًا
        await send_recommendations(bot)
    elif now.startswith("22:5"):  # نهاية اليوم
        await send_results(bot)

if __name__ == "__main__":
    asyncio.run(main())
