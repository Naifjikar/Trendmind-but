import requests
from telegram import Bot
from datetime import datetime
import time
from finvizfinance.screener.overview import Overview

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
            price = float(stock.get("close"))
            change = float(stock.get("changeRatio", 0))
            if price < 5.00 and change > 5:
                entry = round(price, 2)
                t1 = round(entry * 1.08, 2)
                t2 = round(entry * 1.15, 2)
                t3 = round(entry * 1.25, 2)
                t4 = round(entry * 1.40, 2)
                stop = round(entry * 0.91, 2)
                results.append(f"{symbol}\nدخول {entry}\nأهداف: {t1} - {t2} - {t3} - {t4}\nوقف: {stop}")
        return results[:4]
    except Exception as e:
        print("❌ Error Webull:", e)
        return []

def get_finviz_swing_opportunities():
    try:
        print("🔍 Fetching Finviz swing scan...")
        screener = Overview()
        screener.set_filter(filters_dict={
            'Signal': 'w_up',
            'SMA50': 'u50',
            'AvgVolume': 'o150',
            'Price': 'o1,cto5',
            'Float': 's100'
        })
        df = screener.screener_view()
        print(f"📊 Finviz returned {len(df)} rows")
        results = []
        for idx, row in df.head(2).iterrows():
            ticker = row['Ticker']
            price = float(row['Price'])
            entry = round(price, 2)
            t1 = round(entry * 1.08, 2)
            t2 = round(entry * 1.15, 2)
            t3 = round(entry * 1.25, 2)
            stop = round(entry * 0.91, 2)
            results.append(f"{ticker}\nدخول {entry}\nأهداف: {t1} - {t2} - {t3}\nوقف: {stop}")
        return results
    except Exception as e:
        print("❌ Error Finviz:", e)
        return []

def send_finviz_signals():
    print("📈 Sending Finviz swing opportunities...")
    opps = get_finviz_swing_opportunities()
    if opps:
        for msg in opps:
            bot.send_message(chat_id=PRIVATE_CHANNEL, text=msg)
        print("✅ Sent Finviz swing signals.")
    else:
        bot.send_message(chat_id=PRIVATE_CHANNEL, text="⚠️ لا توجد فرص سوينق حالياً.")
        print("❗ No Finviz opportunities.")

def send_webull_recommendations():
    print("🚀 Sending Webull gainers...")
    gainers = get_webull_top_gainers()
    if gainers:
        for rec in gainers:
            bot.send_message(chat_id=PRIVATE_CHANNEL, text=rec)
        print("✅ Sent Webull gainers.")
    else:
        bot.send_message(chat_id=PRIVATE_CHANNEL, text="⚠️ لا توجد فرص حالياً.")
        print("❗ No Webull gainers.")

def send_results():
    print("📊 Sending daily results...")
    results = [
        "XYZ - 1\nدخول 1.00 حقق 2.00\nنسبة الربح 100% 💰",
        "ABC - 2\nلم تحقق دخول",
        "DEF - 3\nضربت الوقف ❌ - النسبة -9%"
    ]
    for line in results:
        bot.send_message(chat_id=PUBLIC_CHANNEL, text=line)
    print("✅ Sent daily results.")

while True:
    current_time = datetime.now().strftime("%H:%M")
    print("⏳ الوقت الحالي:", current_time)

    if current_time == "09:00":
        send_finviz_signals()

    elif current_time == "11:00":
        send_webull_recommendations()

    elif current_time == "23:00":
        send_results()

    time.sleep(60)
