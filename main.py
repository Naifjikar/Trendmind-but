import requests
from telegram import Bot
from datetime import datetime
import time

TOKEN = "8085180830:AAFJqSio_7BJ3n_1jbeHvYEZU5FmDJkT_Dw"
PUBLIC_CHANNEL = "-782820280285"
PRIVATE_CHANNEL = "@TrendMind0"
bot = Bot(token=TOKEN)

def get_webull_top_gainers():
    try:
        url = "https://quotes-gw.webullfintech.com/api/securities/market/v5/gainers?region=us&userRegion=US"
        response = requests.get(url)
        data = response.json()
        gainers = data.get("data", {}).get("list", [])
        results = []
        for stock in gainers:
            symbol = stock.get("ticker")
            name = stock.get("name")
            price = float(stock.get("close"))
            change = float(stock.get("changeRatio", 0))
            if price < 5.00 and change > 5:
                entry = round(price, 2)
                target1 = round(entry + (entry * 0.08), 2)
                target2 = round(entry + (entry * 0.15), 2)
                target3 = round(entry + (entry * 0.25), 2)
                target4 = round(entry + (entry * 0.40), 2)
                stop = round(entry - (entry * 0.09), 2)
                results.append(f"{symbol}\nدخول {entry}\nأهداف: {target1} - {target2} - {target3} - {target4}\nوقف: {stop}")
        return results[:4]
    except:
        return []

def send_recommendations():
    gainers = get_webull_top_gainers()
    if gainers:
        for rec in gainers:
            bot.send_message(chat_id=PRIVATE_CHANNEL, text=rec)
    else:
        bot.send_message(chat_id=PRIVATE_CHANNEL, text="لا توجد فرص مناسبة حالياً.")

def send_results():
    now = datetime.now().strftime("%Y-%m-%d")
    # هذه النتائج مؤقتة كمثال، يجب تعديلها حسب بيانات المتابعة الحقيقية
    results = [
        "XYZ - 1\nدخول 1.00 حقق 2.00\nنسبة الربح 100% 💰",
        "ABC - 2\nلم تحقق دخول",
        "DEF - 3\nضربت الوقف ❌ - النسبة -9%"
    ]
    for line in results:
        bot.send_message(chat_id=PUBLIC_CHANNEL, text=line)

while True:
    current_time = datetime.now().strftime("%H:%M")
    if current_time == "11:00":  # وقت إرسال توصيات البري ماركت
        send_recommendations()
    elif current_time == "23:00":  # وقت النتائج اليومية
        send_results()
    time.sleep(60)
