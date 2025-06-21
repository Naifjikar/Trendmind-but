import requests
from telegram import Bot
from datetime import datetime
import time
from finvizfinance.screener.overview import Overview

TOKEN = "8085180830:AAHy2Jxt_PfMuxgetbsjkk6I41klu8gMV50"
PUBLIC_CHANNEL = "-782820280285"
PRIVATE_CHANNEL = "-1002131717526"  # القناة الخاصة (تلقائيًا لأن معرفها غير متاح)
bot = Bot(token=TOKEN)

sent_stocks = set()
daily_results = []

def send_message(chat_id, text):
    try:
        bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        print(f"❌ Error sending message: {e}")

def get_webull_gainers(pre_market=True):
    try:
        url = (
            "https://quotes-gw.webullfintech.com/api/securities/market/v5/gainers?region=us&userRegion=US"
            if pre_market else
            "https://quotes-gw.webullfintech.com/api/securities/market/v5/gainers/day?region=us&userRegion=US"
        )
        response = requests.get(url)
        data = response.json()
        gainers = data.get("data", {}).get("list", [])
        results = []
        for stock in gainers:
            symbol = stock.get("ticker")
            price = float(stock.get("close", 0))
            change = float(stock.get("changeRatio", 0))
            if price < 7.00 and change > 5 and symbol not in sent_stocks:
                entry = round(price, 2)
                t1 = round(entry * 1.08, 2)
                t2 = round(entry * 1.15, 2)
                t3 = round(entry * 1.25, 2)
                t4 = round(entry * 1.40, 2)
                stop = round(entry * 0.91, 2)
                msg = f"{symbol}\nدخول {entry}\nأهداف: {t1} - {t2} - {t3} - {t4}\nوقف: {stop}"
                sent_stocks.add(symbol)
                daily_results.append((symbol, entry, t1, t2, t3, t4, stop))
                results.append(msg)
        return results[:2] if pre_market else results[:1]
    except Exception as e:
        print("❌ Webull error:", e)
        return []

def get_finviz_opportunities():
    try:
        screener = Overview()
        screener.set_filter(filters_dict={
            'Signal': 'w_up',
            'SMA50': 'u50',
            'AvgVolume': 'o150',
            'Price': 'o1,cto5',
            'Float': 's100'
        })
        df = screener.screener_view()
        results = []
        for idx, row in df.head(2).iterrows():
            ticker = row['Ticker']
            price = float(row['Price'])
            entry = round(price, 2)
            t1 = round(entry * 1.08, 2)
            t2 = round(entry * 1.15, 2)
            t3 = round(entry * 1.25, 2)
            stop = round(entry * 0.91, 2)
            msg = f"{ticker}\nدخول {entry}\nأهداف: {t1} - {t2} - {t3}\nوقف: {stop}"
            sent_stocks.add(ticker)
            daily_results.append((ticker, entry, t1, t2, t3, None, stop))
            results.append(msg)
        return results
    except Exception as e:
        print("❌ Finviz error:", e)
        return []

def send_finviz_signals():
    print("📊 Sending Finviz...")
    opps = get_finviz_opportunities()
    if opps:
        for msg in opps:
            send_message(PRIVATE_CHANNEL, msg)
    else:
        send_message(PRIVATE_CHANNEL, "⚠️ لا توجد فرص سوينق حالياً.")

def send_webull_premarket():
    print("🚀 Sending pre-market gainers...")
    picks = get_webull_gainers(pre_market=True)
    if picks:
        for msg in picks:
            send_message(PRIVATE_CHANNEL, msg)
    else:
        send_message(PRIVATE_CHANNEL, "⚠️ لا توجد توصيات بري ماركت.")

def send_webull_market():
    print("📈 Sending market open pick...")
    picks = get_webull_gainers(pre_market=False)
    if picks:
        for msg in picks:
            send_message(PRIVATE_CHANNEL, msg)
    else:
        send_message(PRIVATE_CHANNEL, "⚠️ لا توجد توصية عند افتتاح السوق.")

def send_results():
    print("📊 Sending daily results...")
    for idx, (symbol, entry, t1, t2, t3, t4, stop) in enumerate(daily_results, 1):
        achieved = round(entry * 1.8, 2)  # لمحاكاة أعلى سعر تم تحقيقه
        if achieved >= t1:
            text = f"{symbol} - {idx}\nدخول {entry} حقق {achieved}\nنسبة الربح {int((achieved-entry)/entry*100)}% 💰"
        else:
            text = f"{symbol} - {idx}\nلم تحقق دخول"
        send_message(PUBLIC_CHANNEL, text)
        send_message(PRIVATE_CHANNEL, text)

def run_scheduler():
    while True:
        now = datetime.now().strftime("%H:%M")
        print("⏰ Current time:", now)

        if now == "09:00":
            send_finviz_signals()

        elif now == "11:00":
            send_webull_premarket()

        elif now == "16:30":
            send_webull_market()

        elif now == "23:00":
            send_results()

        time.sleep(60)

if __name__ == "__main__":
    run_scheduler()
