import ccxt
import pandas as pd
import time
import requests
import logging
from datetime import datetime

# --- 1. إعداد نظام التسجيل (Logger) ---
# الملف activity.log راح يكون "الصندوق الأسود" تاع البوت
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_activity.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# --- 2. إعدادات أسامة (التوكن والـ ID) ---
token = '8784561791:AAEjT-yUmiK4cxP1-xAncL8QxZ9sSTLFli8'
chat_id = '941661354'

def send_pro_analysis(msg):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        res = requests.post(url, json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})
        if res.status_code == 200:
            logging.info("✅ تم إرسال التنبيه لتليغرام بنجاح")
        else:
            logging.warning(f"⚠️ فشل إرسال التنبيه: {res.text}")
    except Exception as e:
        logging.error(f"❌ خطأ في الاتصال بتليغرام: {e}")

# --- 3. تهيئة الاتصال ببينانس ---
exchange = ccxt.binance()
symbols = ['SOL/USDT', 'AVAX/USDT', 'BTC/USDT', 'XRP/USDT']

logging.info("🚀 Bot Strategy Master v5.0 started successfully!")

while True:
    try:
        for symbol in symbols:
            logging.info(f"🔎 فحص عملة {symbol} مستمر...")
            
            bars = exchange.fetch_ohlcv(symbol, timeframe='15m', limit=100)
            df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            i = len(df) - 1
            curr_close = df['close'].iloc[i]

            # --- Logic: Liquidity Sweep (SFP) ---
            prev_low = df['low'].iloc[-25:-2].min()
            current_low = df['low'].iloc[i-1]
            sweep = current_low < prev_low and curr_close > prev_low

            # --- Logic: SK System (Fibonacci) ---
            hi, lo = df['high'].max(), df['low'].min()
            fib_618 = hi - (0.618 * (hi - lo))
            fib_786 = hi - (0.786 * (hi - lo))

            # --- Logic: Elliott (AO Momentum) ---
            mid = (df['high'] + df['low']) / 2
            ao = mid.rolling(5).mean() - mid.rolling(34).mean()

            # --- Logic: SMC (FVG) ---
            fvg = df['low'].iloc[i] > df['high'].iloc[i-2]

            # التحقق من الإشارة الذهبية
            if sweep and fvg:
                if fib_786 <= curr_close <= fib_618:
                    if ao.iloc[i] > ao.iloc[i-1]:
                        msg = f"🌟 *PRO SIGNAL: {symbol}*\n"
                        msg += f"━━━━━━━━━━━━━━━\n"
                        msg += f"💀 Liquidity Sweep: ✅\n"
                        msg += f"⚡ SMC FVG: ✅\n"
                        msg += f"📐 SK Zone: ✅\n"
                        msg += f"🌊 Elliott Wave 3: ✅\n\n"
                        msg += f"💰 Price: `{curr_close:.4f}`"
                        send_pro_analysis(msg)
                        logging.info(f"🎯 فرصة ذهبية مكتشفة في {symbol}")
                        time.sleep(600) # راحة لعدم تكرار التنبيه

        time.sleep(60) # فحص كل دقيقة

    except Exception as e:
        logging.error(f"🚨 خطأ غير متوقع في الحلقة الأساسية: {e}")
        time.sleep(30) # انتظار قبل إعادة المحاولة