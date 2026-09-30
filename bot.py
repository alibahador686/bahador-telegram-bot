import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from datetime import datetime
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)

# سرور HTTP ساده برای سازگاری با هاستینگ‌ها
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        pass

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# توکن ربات شما
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8627933053:AAHAo1QSfWDpAUPr_LfJjVSwadzQKX0fJEA")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "198728977"))

# شناسه‌های فایل عکس‌های مختص بهادر فیلم
PHOTO_IDS = {
    "logo": "AgACAgQAAxkBAANoarTxcvaLVFFDuPSMVCLQ6XXcCEgAAj8QaxslQqhRHyuGPLEPCTYBAAMCAAN5AAM9BA",
    "work_1": "AgACAgQAAxkBAANZarTpN4VZ_zuBvY8qfr8XmbNw7pkAAjQQaxslQqhRXfvpAAFEs83zAQADAgADeQADPQQ",
    "work_2": "AgACAgQAAxkBAANearTvmlgwxRnFLGAlGWxU8rkT-1AAAjgQaxslQqhR53FaIRSpKHYBAAMCAAN5AAM9BA",
    "work_3": "AgACAgQAAxkBAANgarTwM3C7YugVl34Zx5zmdfqblxEAAjoQaxslQqhRjoQOS53pRBEBAAMCAAN5AAM9BA",
    "work_4": "AgACAgQAAxkBAANiarTwitFl3GizqfXA940Rm6KoAywAAjsQaxslQqhRLcDSK7px4JIBAAMCAAN5AAM9BA",
    "work_5": "AgACAgQAAxkBAANkarTw6xfxZ84odXO_PlgJBVLWvY8AAjwQaxslQqhR3hmwjUYRM0wBAAMCAAN5AAM9BA",
    "work_6": "AgACAgQAAxkBAANmarTxHy9f8plmCbwBwH-n-0U3eUcAAj4QaxslQqhR79dvxxWcmpIBAAMCAAN5AAM9BA",
    "work_7": "AgACAgQAAxkBAANoarTxcvaLVFFDuPSMVCLQ6XXcCEgAAj8QaxslQqhRHyuGPLEPCTYBAAMCAAN5AAM9BA",
    "work_8": "AgACAgQAAxkBAANqarTxuueYW1gjMcHlaCaDZJXtJ1EAAkEQaxslQqhR-aYKXskUhHIBAAMCAAN5AAM9BA",
    "work_9": "AgACAgQAAxkBAANsarTx9X_9z_IFk7DvWGmtVGkGB0AAAkIQaxslQqhRUjAa4c-6XLwBAAMCAAN5AAM9BA",
    "work_10": "AgACAgQAAxkBAANuarTyOwkGmkfs6tcNodNBGzujgCwAAkMQaxslQqhRRxnzoph9E4EBAAMCAAN5AAM9BA",
    "work_11": "AgACAgQAAxkBAANwarTyYMpvBUdAvWgxpNDsokdZzAkAAkQQaxslQqhR0jS6MO2oIdQBAAMCAAN5AAM9BA",
    "work_12": "AgACAgQAAxkBAANyarTyuYCz-nKqjilkshH7l-IZl_8AAkUQaxslQqhR_zB2Ple2rxMBAAMCAAN5AAM9BA",
    "work_13": "AgACAgQAAxkBAAN0arTz_Q5l6uW9hJ3uQ1wAARXGq78AAkYQaxslQqhR6m1k_3_5-1wBAAMCAAN5AAM9BA",
    "work_14": "AgACAgQAAxkBAAN2arT0a6YpX7aK5f8v8x5Y1AABAAH8AAkcAaxslQqhR8p9kZ9l_3AEBAAMCAAN5AAM9BA",
    "award_15": "AgACAgQAAxkBAAOBarT63lwTbK1i98T2La7qVD3q4gEAAlQQaxslQqhRbvL3WI2R2JkBAAMCAAN5AAM9BA",
    "award_16": "AgACAgQAAxkBAAODarT69lI0d1-rQQs-AwTKjAO7WQsAAlUQaxslQqhRpgYVe0-1E6QBAAMCAAN5AAM9BA",
    "award_17": "AgACAgQAAxkBAAOFarT7AAH5vKOpDySxkrpJFz3UX-5eAAJWEGsbJUKoUTD95jq44Ny8AQADAgADeQADPQQ",
    "award_18": "AgACAgQAAxkBAAOHarT7Ecmh4vTKQmVMRKyi95ijsXYAAlcQaxslQqhR703ya5-kizwBAAMCAAN5AAM9BA",
    "award_19": "AgACAgQAAxkBAAOJarT7JWk3v6x2f7W4V6_1a8q3b68AAloQaxslQqhR9p1kZ9l_3AEBAAMCAAN5AAM9BA",
    "award_20": "AgACAgQAAxkBAAOLarT7O91v6x2f7W4V6_1a8q3b69AAlsQaxslQqhR5p1kZ9l_3AEBAAMCAAN5AAM9BA"
}

stats_data = {"total_visits": 0, "unique_users": set(), "orders_count": 0, "messages_count": 0}
PROJECT_TYPE, USER_NAME, USER_PHONE = range(3)
ADMIN_MESSAGE = range(1)

def get_rotational_photo():
    all_keys = list(PHOTO_IDS.keys())
    day_of_year = datetime.now().timetuple().tm_yday
    return PHOTO_IDS.get(all_keys[day_of_year % len(all_keys)], PHOTO_IDS["logo"])

def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 ثبت سفارش و درخواست مشاوره", callback_data="start_order")],
        [InlineKeyboardButton("📺 نمونه کارها و رزومه تصویری", callback_data="portfolio")],
        [InlineKeyboardButton("ℹ️ درباره مدیرعامل و موسسه", callback_data="about")],
        [InlineKeyboardButton("💳 کارت ویزیت دیجیتال", callback_data="digital_card")],
        [InlineKeyboardButton("✉ ارسال پیام به مدیریت", callback_data="contact_admin")],
        [InlineKeyboardButton("📋 خدمات و تعرفه‌ها", callback_data="services")],
        [InlineKeyboardButton("📰 مصاحبه‌ها و رسانه", callback_data="interviews")],
        [InlineKeyboardButton("❓ پرسش‌های متداول (FAQ)", callback_data="faq")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    stats_data["total_visits"] += 1
    stats_data["unique_users"].add(user.id)
    
    welcome_text = (
        f"سلام {user.first_name} عزیز! 🎬\n\n"
        "**به ربات رسمی موسسه هنری بهادر فیلم خوش آمدید**\n\n"
        "به مدیریت **علی بهادر** - کارگردان، تهیه‌کننده و نویسنده (دارای کارشناسی ارشد ادبیات نمایشی و لیسانس کارگردانی با بیش از چهار دهه تجربه حرفه‌ای در ساخت سریال، مستندهای فاخر تلویزیونی، تیزر، آگهی و انیمیشن).\n\n"
        "لطفاً بخش مورد نظر خود را از منوی زیر انتخاب کنید:"
    )
    
    header_photo = get_rotational_photo()
    
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=header_photo,
            caption=welcome_text,
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
    elif update.message:
        await update.message.reply_photo(
            photo=header_photo,
            caption=welcome_text,
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "back_to_menu":
        welcome_text = "🎬 به منوی اصلی موسسه هنری بهادر فیلم خوش آمدید.\nلطفاً بخش مورد نظر را انتخاب کنید:"
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=get_rotational_photo(),
            caption=welcome_text,
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
    elif data == "portfolio":
        keyboard = [
            [InlineKeyboardButton("📺 سریال‌ها و فیلم‌های داستانی", callback_data="port_series")],
            [InlineKeyboardButton("🎥 مستندهای تلویزیونی و بین‌المللی", callback_data="port_docs")],
            [InlineKeyboardButton("⛽ پروژه ملی و کتاب مرجع گاز", callback_data="port_gas")],
            [InlineKeyboardButton("🎨 انیمیشن‌های آموزشی و طنز", callback_data="port_anim")],
            [InlineKeyboardButton("🏆 جوایز و لوح‌های سپاس", callback_data="port_awards")],
            [InlineKeyboardButton("🌐 وب‌سایت رسمی", url="https://alibahador.ir"), InlineKeyboardButton("📸 اینستاگرام", url="https://instagram.com")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = "📁 **بخش نمونه‌کارها و رزومه تصویری علی بهادر**\n\nلطفاً حوزه مورد نظر خود را برای مشاهده آثار همراه با پوستر و تصویر انتخاب کنید:"
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif data == "port_series":
        keyboard = [
            [InlineKeyboardButton("(۱۳۷۲) بهترین تابستان من", callback_data="work_tabestan")],
            [InlineKeyboardButton("(۱۳۸۰-۱۳۷۹) عشق سال‌های جنگ", callback_data="work_eshgh")],
            [InlineKeyboardButton("(۱۳۸۸) شب هزار و یکم", callback_data="work_shab")],
            [InlineKeyboardButton("(۱۳۹۱) قدم زدن در بهشت", callback_data="work_ghadam")],
            [InlineKeyboardButton("(۱۳۹۳) ارثیه پرماجرا", callback_data="work_ershieh")],
            [InlineKeyboardButton("(۱۳۹۳) شاهزاده و گدا", callback_data="work_shahzadeh")],
            [InlineKeyboardButton("(۱۴۰۱) مشتری‌مداری", callback_data="work_moshtari")],
            [InlineKeyboardButton("(۱۳۹۷) برکت", callback_data="work_barakat")],
            [InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = "📺 **سریال‌های تلویزیونی و فیلم‌های داستانی:**\nلطفاً اثر مورد نظر خود را انتخاب کنید:"
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif data == "port_docs":
        keyboard = [
            [InlineKeyboardButton("مستند «زندگی»", callback_data="work_zendegi")],
            [InlineKeyboardButton("(۲۰۱۵) مستند کنگره جهانی گاز پاریس", callback_data="work_paris")],
            [InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = "🎥 **مستندهای تلویزیونی و بین‌المللی:**\nلطفاً مستند مورد نظر خود را انتخاب کنید:"
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif data == "port_gas":
        keyboard = [
            [InlineKeyboardButton("کتاب مرجع گاز؛ انرژی پاک با نیم قرن تلاش", callback_data="work_gas_book")],
            [InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = "⛽ **پروژه‌های ملی نفت و گاز و کتاب مرجع:**\nلطفاً گزینه مورد نظر را انتخاب کنید:"
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif data == "port_anim":
        keyboard = [
            [InlineKeyboardButton("انیمیشن آموزشی «اسرافی و انصافی»", callback_data="work_esrafi")],
            [InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = "🎨 **انیمیشن‌های آموزشی و طنز:**\nلطفاً گزینه مورد نظر را انتخاب کنید:"
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif data == "port_awards":
        keyboard = [
            [InlineKeyboardButton("لوح تقدیر جشنواره رشد و دفاع مقدس", callback_data="award_roshd")],
            [InlineKeyboardButton("لوح‌ها و تندیس‌های تقدیر ویژه", callback_data="award_tandis")],
            [InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = "🏆 **افتخارات، جوایز و لوح‌های سپاس:**\nلطفاً گزینه مورد نظر را انتخاب کنید:"
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif data == "work_tabestan":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_1"], caption="⭐ **بهترین تابستان من**\n\nکارگردانی سریال طنز دفاع مقدس.", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try: await query.message.delete()
        except: pass
    elif data == "work_eshgh":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_3"], caption="❤️ **عشق سال‌های جنگ**", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try: await query.message.delete()
        except: pass
    elif data == "work_shab":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_13"], caption="🌙 **شب هزار و یکم**", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try: await query.message.delete()
        except: pass
    elif data == "work_ghadam":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_4"], caption="🌿 **قدم زدن در بهشت**", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try: await query.message.delete()
        except: pass
    elif data == "work_ershieh":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_5"], caption="💼 **ارثیه پرماجرا**", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try: await query.message.delete()
        except: pass
    elif data == "work_shahzadeh":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_6"], caption="👑 **شاهزاده و گدا**", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try: await query.message.delete()
        except: pass
    elif data == "work_moshtari":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_8"], caption="🤝 **مشتری‌‌مداری**", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try: await query.message.delete()
        except: pass
    elif data == "work_barakat":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_12"], caption="🌾 **برکت**", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try: await query.message.delete()
        except: pass
    elif data == "work_gas_book":
        kb = [[InlineKeyboardButton("🔙 بازگشت به پروژه گاز", callback_data="port_gas")]]
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_11"], caption="📖 **کتاب مرجع گاز**", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try: await query.message.delete()
        except: pass
    elif data == "work_paris":
        kb = [[InlineKeyboardButton("🔙 بازگشت به مستندها", callback_data="port_docs")]]
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_14"], caption="🌍 **مستند پاریس**", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try: await query.message.delete()
        except: pass
    elif data == "work_zendegi":
        kb = [[InlineKeyboardButton("🔙 بازگشت به مستندها", callback_data="port_docs")]]
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_2"], caption="🏆 **مستند «زندگی»**", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try: await query.message.delete()
        except: pass
    elif data == "work_esrafi":
        kb = [[InlineKeyboardButton("🔙 بازگشت به انیمیشن‌ها", callback_data="port_anim")]]
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["work_7"], caption="💡 **اسرافی و انصافی**", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try: await query.message.delete()
        except: pass
    elif data == "award_roshd":
        kb = [[InlineKeyboardButton("🔙 بازگشت به جوایز", callback_data="port_awards")]]
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["award_15"], caption="🎖 **لوح تقدیر جشنواره رشد**", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try: await query.message.delete()
        except: pass
    elif data == "award_tandis":
        kb = [[InlineKeyboardButton("🔙 بازگشت به جوایز", callback_data="port_awards")]]
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=PHOTO_IDS["award_16"], caption="🏆 **تندیس‌ها**", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try: await query.message.delete()
        except: pass
            
    elif data == "interviews":
        keyboard = [
            [InlineKeyboardButton("مصاحبه روزنامه اطلاعات (۲۰ مرداد ۱۴۰۵)", callback_data="view_ettelaat_img")],
            [InlineKeyboardButton("مصاحبه هفته‌نامه صدا و سیما (مرداد ۱۴۰۵)", callback_data="view_sedavasima_img")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = "📰 **بخش مصاحبه‌ها و پوشش رسانه‌ای:**"
        try: await query.message.delete()
        except: pass
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif data == "view_ettelaat_img":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به بخش مصاحبه‌ها", callback_data="interviews")]]
        await query.message.reply_text("📰 **مصاحبه با روزنامه اطلاعات (۲۰ مرداد ۱۴۰۵):**\n[مشاهده آنلاین](https://www.ettelaat.com/news/161537/%D8%B3%DB%8C%D9%86%D9%85%D8%A7%DB%8C-%D9%85%D8%B3%D8%AA%D9%86%D8%AF-%D8%A8%D9%87-%D9%85%D8%AF%DB%8C%D8%B1%D8%A7%D9%86%DB%8C-%D8%AC%D8%B3%D9%88%D8%B1-%D9%86%DB%8C%D8%A7%D8%B2-%D8%AF%D8%A7%D8%B1%D8%AF)", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try: await query.message.delete()
        except: pass
    elif data == "view_sedavasima_img":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به بخش مصاحبه‌ها", callback_data="interviews")]]
        try: await query.message.delete()
        except: pass
        await query.message.reply_text("📰 **مصاحبه با هفته‌نامه صدا و سیما (مرداد ۱۴۰۵)**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif data == "about":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        about_text = (
            "ℹ️ **درباره علی بهادر و مؤسسه هنری بهادر فیلم**\n\n"
            "• **تحصیلات:** کارشناسی ارشد ادبیات نمایشی و لیسانس کارگردانی\n"
            "• **مدیرعامل:** مؤسسه فرهنگی و هنری بهادر فیلم\n"
            "• **سوابق:** ساخت سریال‌های تلویزیونی (بهترین تابستان من، عشق سال‌های جنگ، شب هزار و یکم) و مستندهای ملی."
        )
        try: await query.message.delete()
        except: pass
        await query.message.reply_text(about_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif data == "digital_card":
        keyboard = [
            [InlineKeyboardButton("🌐 وب‌‌سایت رسمی", url="https://alibahador.ir")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        try: await query.message.delete()
        except: pass
        await query.message.reply_text("💳 **کارت ویزیت دیجیتال مؤسسه هنری بهادر فیلم**\n👤 مدیرعامل: علی بهادر", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif data == "services":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        try: await query.message.delete()
        except: pass
        await query.message.reply_text("📋 **خدمات مؤسسه:**\n۱. ساخت سریال\n۲. مستند\n۳. تیزر و انیمیشن", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif data == "faq":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        try: await query.message.delete()
        except: pass
        await query.message.reply_text("❓ **پرسش‌های متداول:**\nثبت سفارش از طریق منوی اصلی انجام می‌شود.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("سریال و فیلم داستانی", callback_data="p_series")],
        [InlineKeyboardButton("ساخت مستند", callback_data="p_documentary")],
        [InlineKeyboardButton("تیزر تبلیغاتی", callback_data="p_teaser")],
        [InlineKeyboardButton("انیمیشن", callback_data="p_anim")],
        [InlineKeyboardButton("انصراف", callback_data="back_to_menu")]
    ]
    try: await query.message.delete()
    except: pass
    await query.message.reply_text("🛒 نوع پروژه مورد نظر خود را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return PROJECT_TYPE

async def receive_project_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mapping = {"p_series": "سریال", "p_documentary": "مستند", "p_teaser": "تیزر", "p_anim": "انیمیشن"}
    context.user_data['project_type'] = mapping.get(query.data, "نامشخص")
    try: await query.message.delete()
    except: pass
    await query.message.reply_text("🛒 لطفاً **نام و نام خانوادگی خود را ارسال کنید:**", parse_mode="Markdown")
    return USER_NAME

async def receive_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['user_name'] = update.message.text
    await update.message.reply_text("🛒 لطفاً **شماره تماس خود را ارسال کنید:**", parse_mode="Markdown")
    return USER_PHONE

async def receive_user_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u_phone = update.message.text
    p_type = context.user_data.get('project_type')
    u_name = context.user_data.get('user_name')
    
    stats_data["orders_count"] += 1
    
    try:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"🚨 **سفارش جدید!**\n🔹 پروژه: {p_type}\n👤 نام: {u_name}\n📞 تلفن: {u_phone}",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
    await update.message.reply_text("✅ سفارش شما ثبت شد و به مدیریت ارسال گردید.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return ConversationHandler.END

async def contact_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("انصراف", callback_data="back_to_menu")]]
    try: await query.message.delete()
    except: pass
    await query.message.reply_text("✉️ پیام خود را برای مدیریت بنویسید:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return ADMIN_MESSAGE

async def receive_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats_data["messages_count"] += 1
    user_msg = update.message.text
    user = update.effective_user
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"✉️ پیام از {user.full_name}:\n\n{user_msg}", parse_mode="Markdown")
    except: pass
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
    await update.message.reply_text("✅ پیام ارسال شد.", reply_markup=InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عملیات لغو شد.", reply_markup=get_main_menu())
    return ConversationHandler.END

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    order_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_order, pattern="^start_order$")],
        states={
            PROJECT_TYPE: [CallbackQueryHandler(receive_project_type)],
            USER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_name)],
            USER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    contact_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(contact_admin_start, pattern="^contact_admin$")],
        states={
            ADMIN_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_admin_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(order_conv)
    application.add_handler(contact_conv)
    application.add_handler(CallbackQueryHandler(button_handler))
    
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
