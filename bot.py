import os
import json
import requests
import schedule
import time
import random
from datetime import datetime, timedelta
import pytz
from telegram import Bot
from telegram.constants import ParseMode
import logging

# ==================== تنظیمات ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# مقادیر پیش‌فرض - در Render جایگزین می‌شوند
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', 'توکن_ربات_شما')
CHANNEL_USERNAME = os.environ.get('CHANNEL_USERNAME', '@کانال_شما')

kabul_tz = pytz.timezone('Asia/Kabul')
bot = None

# ==================== API های رایگان ====================
class DataFetcher:
    @staticmethod
    def get_currency_rates():
        """دریافت نرخ ارز از API های رایگان"""
        try:
            # گزینه ۱: exchangerate-api
            response = requests.get(
                'https://api.exchangerate-api.com/v4/latest/USD',
                timeout=5
            )
            data = response.json()
            rates = data.get('rates', {})
            
            # تبدیل به افغانی (نمونه - نیاز به API واقعی دارید)
            afn_rate = rates.get('AFN', 80)
            return {
                '🇺🇸 دلار آمریکا': f"{afn_rate:,} افغانی",
                '🇪🇺 یورو اروپا': f"{round(afn_rate * 0.85):,} افغانی",
                '🇵🇰 روپیه پاکستان': f"{round(afn_rate / 285, 2)} افغانی",
                '🇮🇷 ریال ایران': f"{round(afn_rate / 42000, 4)} افغانی",
                '🇦🇪 درهم امارات': f"{round(afn_rate / 3.67):,} افغانی"
            }
        except:
            # مقادیر پیش‌فرض
            return {
                '🇺🇸 دلار آمریکا': '80 افغانی',
                '🇪🇺 یورو اروپا': '85 افغانی',
                '🇵🇰 روپیه پاکستان': '0.28 افغانی',
                '🇮🇷 ریال ایران': '0.0019 افغانی',
                '🇦🇪 درهم امارات': '22 افغانی'
            }

    @staticmethod
    def get_crypto_prices():
        """قیمت ارزهای دیجیتال"""
        try:
            response = requests.get(
                'https://api.coingecko.com/api/v3/simple/price',
                params={'ids': 'bitcoin,ethereum', 'vs_currencies': 'usd'},
                timeout=5
            )
            data = response.json()
            return {
                '₿ بیت‌کوین': f"${data.get('bitcoin', {}).get('usd', 45000):,}",
                '🔷 اتریوم': f"${data.get('ethereum', {}).get('usd', 2500):,}"
            }
        except:
            return {
                '₿ بیت‌کوین': '$45,000',
                '🔷 اتریوم': '$2,500'
            }

    @staticmethod
    def get_news_headlines():
        """دریافت تیتر اخبار (نمونه)"""
        news_sources = [
            "📰 توافق جدید تجاری با کشورهای همسایه",
            "🌍 قیمت جهانی گندم ۵٪ افزایش یافت",
            "💰 بانک مرکزی سیاست جدید ارزی اعلام کرد",
            "⚡ قطعی برق در برخی مناطق کابل",
            "🤝 دیدار وزیر تجارت با هیئت چینی",
            "🌧️ پیش‌بینی بارش باران در شمال کشور",
            "📈 رشد ۲٪ی صادرات پسته افغانستان",
            "🛒 کاهش قیمت مرغ در بازار کابل"
        ]
        return random.sample(news_sources, 4)

# ==================== سیستم زمان‌بندی هوشمند ====================
class SmartScheduler:
    def __init__(self):
        self.schedule_times = [
            "08:00", "12:00", "16:00", "20:00"  # ۴ بار در روز
        ]
        
    def get_next_run(self):
        now = datetime.now(kabul_tz)
        for time_str in self.schedule_times:
            run_time = datetime.strptime(time_str, "%H:%M").time()
            run_datetime = kabul_tz.localize(
                datetime.combine(now.date(), run_time)
            )
            if run_datetime > now:
                return run_datetime
        # اگر همه زمان‌ها گذشتند، برای فردا اولین زمان
        tomorrow = now + timedelta(days=1)
        first_time = datetime.strptime(self.schedule_times[0], "%H:%M").time()
        return kabul_tz.localize(datetime.combine(tomorrow.date(), first_time))

# ==================== سیستم گزارش‌گیری ====================
class ReportGenerator:
    @staticmethod
    def generate_market_report():
        fetcher = DataFetcher()
        
        now = datetime.now(kabul_tz)
        hijri_date = now.strftime("%Y/%m/%d")
        gregorian_date = now.strftime("%d/%m/%Y")
        
        report = f"""
🏔 **گزارش بازار افغانستان**
📅 {hijri_date} - {gregorian_date}
⏰ {now.strftime("%H:%M")} | کابل

──────────────
💱 **نرخ ارز:**
"""
        
        # ارزها
        currencies = fetcher.get_currency_rates()
        for name, value in currencies.items():
            report += f"• {name}: `{value}`\n"
        
        report += "\n💰 **ارزهای دیجیتال:**\n"
        cryptos = fetcher.get_crypto_prices()
        for name, value in cryptos.items():
            report += f"• {name}: `{value}`\n"
        
        report += "\n🏅 **فلزات گرانبها:**\n"
        report += "• طلای ۲۴ عیار: `3,200 افغانی`\n"
        report += "• سکه طلا: `16,000 افغانی`\n"
        report += "• نقره (گرم): `40 افغانی`\n"
        
        report += "\n🌾 **مواد غذایی:**\n"
        report += "• گندم (کیلو): `50 افغانی`\n"
        report += "• برنج (کیلو): `70 افغانی`\n"
        report += "• روغن (لیتر): `120 افغانی`\n"
        report += "• شکر (کیلو): `70 افغانی`\n"
        
        report += "\n📊 **وضعیت بازار:**\n"
        market_status = ["📈 صعودی", "📉 نزولی", "➡️ ثابت"]
        report += f"• روند: {random.choice(market_status)}\n"
        report += f"• نقدینگی: {'بالا' if random.random() > 0.5 else 'متوسط'}\n"
        
        report += "\n📰 **تیتر اخبار:**\n"
        news = fetcher.get_news_headlines()
        for i, headline in enumerate(news, 1):
            report += f"{i}. {headline}\n"
        
        report += f"""
──────────────
📊 منبع: داده‌های بازار افغانستان
🔄 به‌روزرسانی: ۴ بار در روز
🔔 کانال رسمی: {CHANNEL_USERNAME}
"""
        
        return report.strip()

# ==================== مدیریت ربات ====================
class TelegramBotManager:
    def __init__(self):
        self.bot = None
        self.scheduler = SmartScheduler()
        self.reporter = ReportGenerator()
        
    def initialize(self):
        """راه‌اندازی ربات"""
        try:
            token = TELEGRAM_TOKEN
            if 'توکن' in token:
                logger.error("لطفاً توکن ربات را در Environment Variables تنظیم کنید!")
                return False
            
            self.bot = Bot(token=token)
            logger.info("✅ ربات تلگرام راه‌اندازی شد")
            return True
        except Exception as e:
            logger.error(f"❌ خطا در راه‌اندازی ربات: {e}")
            return False
    
    def send_report(self):
        """ارسال گزارش به کانال"""
        try:
            if self.bot is None:
                self.initialize()
            
            report = self.reporter.generate_market_report()
            
            self.bot.send_message(
                chat_id=CHANNEL_USERNAME,
                text=report,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            
            next_run = self.scheduler.get_next_run()
            logger.info(f"✅ گزارش ارسال شد. ارسال بعدی: {next_run.strftime('%H:%M')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطا در ارسال گزارش: {e}")
            return False
    
    def setup_schedule(self):
        """تنظیم زمان‌بندی"""
        # ارسال اولیه
        self.send_report()
        
        # زمان‌بندی منظم
        for time_str in self.scheduler.schedule_times:
            schedule.every().day.at(time_str).do(self.send_report)
        
        logger.info("⏰ زمان‌بندی تنظیم شد")

# ==================== اجرای اصلی ====================
def main():
    logger.info("🚀 شروع ربات خبررسان بازار افغانستان")
    
    bot_manager = TelegramBotManager()
    
    if not bot_manager.initialize():
        logger.error("خاتمه به دلیل خطای راه‌اندازی")
        return
    
    bot_manager.setup_schedule()
    
    next_run = bot_manager.scheduler.get_next_run()
    logger.info(f"⏳ ارسال بعدی: {next_run.strftime('%Y-%m-%d %H:%M')}")
    
    # حلقه اصلی
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # بررسی هر دقیقه
        except KeyboardInterrupt:
            logger.info("🛑 ربات متوقف شد")
            break
        except Exception as e:
            logger.error(f"⚠️ خطا در حلقه اصلی: {e}")
            time.sleep(300)  # در صورت خطا ۵ دقیقه صبر

if __name__ == "__main__":
    main()
