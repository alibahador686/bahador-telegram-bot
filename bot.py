import os
import logging
import random
import datetime
from flask import Flask, jsonify
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler
)

# تنظیمات لاگینگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN", "8627933053:AAGhQyyblUP237We1QRMMwTBY7IW45SK79Y")
ADMIN_CHAT_ID = 198728977

stats_data = {
    "total_visits": 0,
    "unique_users": set(),
    "orders_count": 0,
    "messages_count": 0
}

# مراحل کانورسیشن ثبت سفارش و پیام مدیریت
PACKAGE_CHOICE, USER_NAME, USER_PHONE = range(3)
ADMIN_MESSAGE = range(1)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bahador Film Bot is running live with two-column layout and fixed stats!"

@app.route('/stats')
def stats():
    return jsonify({
        "status": "active",
        "total_visits": stats_data["total_visits"],
        "unique_users_count": len(stats_data["unique_users"]),
        "total_orders": stats_data["orders_count"],
        "total_admin_messages": stats_data["messages_count"]
    })

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# منوی اصلی دو ستونی (طبق درخواست شما)
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("ثبت سفارش و درخواست مشاوره", callback_data="start_order")],
        [InlineKeyboardButton("هدیه رایگان فایل راهنما", callback_data="lead_magnet")],
        [
            InlineKeyboardButton("پکیج های خدمات", callback_data="packages"),
            InlineKeyboardButton("نمونه کارها و رزومه کامل", callback_data="portfolio")
        ],
        [
            InlineKeyboardButton("فرآیند کار ما", callback_data="workflow"),
            InlineKeyboardButton("درباره مدیر عامل", callback_data="about")
        ],
        [
            InlineKeyboardButton("کارت ویزیت دیجیتال", callback_data="digital_card"),
            InlineKeyboardButton("ارسال پیام به مدیریت", callback_data="contact_admin")
        ],
        [
            InlineKeyboardButton("مصاحبه ها و رسانه", callback_data="interviews"),
            InlineKeyboardButton("خبرنامه آموزشی", callback_data="newsletter_join")
        ],
        [InlineKeyboardButton("پرسشهای متداول (FAQ)", callback_data="faq")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    stats_data["total_visits"] += 1
    stats_data["unique_users"].add(user.id)
    args = context.args
    if args:
        source = args[0]
        logger.info(f"کاربر جدید از منبع ورودی {source} وارد ربات شد. کاربر ID: {user.id}")
    
    welcome_text = (
        "**به مؤسسه هنری بهادر فیلم خوش آمدید**\n\n"
        "سازنده سریال، مستندهای فاخر تلویزیونی، تیزر و انیمیشن\n\n"
        "**مدیریت: علی بهادر (کارگردان و تهیه‌کننده)**\n\n"
        "چه پروژه‌ای در ذهن دارید؟ از منوی زیر انتخاب کنید:"
    )
    if update.callback_query:
        await update.callback_query.message.reply_text(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")
        await update.callback_query.answer()
    else:
        await update.message.reply_text(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "**📊 آمار بازدید و تعاملات ربات مؤسسه بهادر فیلم**\n\n"
        f"• کل بازدیدها: {stats_data['total_visits']}\n"
        f"• کاربران یکتا: {len(stats_data['unique_users'])}\n"
        f"• مشاوره ها و سفارشهای ثبت شده: {stats_data['orders_count']}\n"
        f"• پیامهای دریافتی مدیریت: {stats_data['messages_count']}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# --- جریان تعاملی ثبت سفارش و پکیج ها ---
async def start_order_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("پکیج پایه مناسب کسب و کارها", callback_data="pkg_base")],
        [InlineKeyboardButton("پکیج حرفه ای مستند و تیزر", callback_data="pkg_pro")],
        [InlineKeyboardButton("پکیج ویژه / فاخر سریال و پروژه های بزرگ", callback_data="pkg_vip")],
        [InlineKeyboardButton("مشاوره عمومی / پروژه دلخواه", callback_data="pkg_custom")],
        [InlineKeyboardButton("بازگشت به منوی اصلی", callback_data="back_to_menu")]
    ]
    text = (
        "**انتخاب پکیج خدمات و ثبت سفارش**\n\n"
        "🎁 **هدیه ویژه:** در صورت ثبت سفارش و انجام کار تا پایان سال ۱۴۰۵، یک کلیپ ۱ دقیقه‌ای رایگان به سفارش‌دهنده تحویل خواهد شد.\n\n"
        "لطفاً پکیج یا نوع درخواست خود را از میان گزینه‌های زیر انتخاب کنید:"
    )
    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    try:
        await query.message.delete()
    except Exception:
        pass
    return PACKAGE_CHOICE

async def receive_package_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    pkg_names = {
        "pkg_base": "پکیج پایه مناسب کسب و کارها",
        "pkg_pro": "پکیج حرفه‌ای مستند و تیزر ویژه",
        "pkg_vip": "پکیج ویژه / فاخر (سریال) و پروژه‌های بزرگ",
        "pkg_custom": "مشاوره عمومی / پروژه دلخواه"
    }
    context.user_data['selected_package'] = pkg_names.get(data, "پکیج سفارشی")
    keyboard = [[InlineKeyboardButton("انصراف و بازگشت", callback_data="back_to_menu")]]
    text = (
        f"پکیج انتخابی شما: **{context.user_data['selected_package']}**\n\n"
        "لطفاً **نام و نام خانوادگی** خود را ارسال کنید:"
    )
    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    try:
        await query.message.delete()
    except Exception:
        pass
    return USER_NAME

async def receive_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.text
    context.user_data['user_name'] = user_name
    keyboard = [[InlineKeyboardButton("انصراف و بازگشت", callback_data="back_to_menu")]]
    text = (
        f"متشکرم **{user_name}** عزیز.\n\n"
        "لطفاً **شماره تماس خود** (مثلاً ۰۹۲۱...) را ارسال کنید تا کارشناسان ما با شما تماس بگیرند:"
    )
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return USER_PHONE

async def receive_user_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    phone = update.message.text
    name = context.user_data.get('user_name', 'نامشخص')
    package = context.user_data.get('selected_package', 'مشاوره عمومی')
    stats_data["orders_count"] += 1
    timestamp = datetime.datetime.now().strftime("%y%m%d%H%M")
    rand_num = random.randint(100, 999)
    tracking_code = f"AB-ORD-{timestamp}-{rand_num}"
    
    admin_notification = (
        "**سفارش / درخواست مشاوره جدید ثبت شد**\n\n"
        f"• **پکیج:** {package}\n"
        f"• **نام:** {name}\n"
        f"• **شماره تماس:** {phone}\n"
        f"• **یوزرنیم تلگرام:** @{user.username or 'ندارد'} (ID: {user.id})\n"
        f"• **کد پیگیری:** `{tracking_code}`"
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_notification, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error sending order to admin: {e}")
        
    success_text = (
        "☑ **سفارش شما با موفقیت ثبت شد.**\n\n"
        "در اسرع وقت با شما تماس گرفته خواهد شد.\n\n"
        "• ساعات پاسخگویی: ۹ صبح تا ۲۰\n"
        "🎁 **هدیه ویژه:** در صورت انجام کار تا پایان سال ۱۴۰۵، یک کلیپ ۱ دقیقه‌ای رایگان به سفارش شما تعلق خواهد گرفت.\n\n"
        f"📌 **کد پیگیری سفارش شما:** `{tracking_code}`\n\n"
        "از اعتماد شما سپاسگزاریم."
    )
    keyboard = [[InlineKeyboardButton("بازگشت به منوی اصلی", callback_data="back_to_menu")]]
    await update.message.reply_text(success_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return ConversationHandler.END

# --- هندلر ارسال پیام مستقیم به مدیریت ---
async def contact_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("انصراف و بازگشت", callback_data="back_to_menu")]]
    text = (
        "**ارسال پیام مستقیم به مدیریت**\n\n"
        "لطفاً پیام، نظر یا درخواست خود را همینجا ارسال کنید تا در اسرع وقت به دست مدیریت برسد و کد پیگیری دریافت کنید."
    )
    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    try:
        await query.message.delete()
    except Exception:
        pass
    return ADMIN_MESSAGE

async def receive_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_text = update.message.text
    stats_data["messages_count"] += 1
    timestamp = datetime.datetime.now().strftime("%y%m%d%H%M")
    rand_num = random.randint(100, 999)
    tracking_code = f"AB-MSG-{timestamp}-{rand_num}"
    
    admin_notification = (
        "**پیام جدید به مدیریت**\n\n"
        f"• **فرستنده:** {user.first_name} {user.last_name or ''}\n"
        f"• **یوزرنیم:** @{user.username or 'ندارد'} (ID: {user.id})\n"
        f"• **کد پیگیری:** `{tracking_code}`\n\n"
        f"**متن پیام:**\n{user_text}"
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_notification, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error sending message to admin chat: {e}")
        
    success_response = (
        "☑ **پیام شما با موفقیت ثبت شد و به مدیریت ارسال گردید.**\n\n"
        "در اسرع وقت پاسخ داده خواهد شد.\n"
        f"📌 **کد پیگیری شما:** `{tracking_code}`"
    )
    keyboard = [[InlineKeyboardButton("بازگشت به منوی اصلی", callback_data="back_to_menu")]]
    await update.message.reply_text(success_response, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return ConversationHandler.END

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "back_to_menu":
        await query.message.reply_text(
            "**مؤسسه هنری بهادر فیلم**\n\nاز منوی زیر انتخاب کنید:",
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "workflow":
        keyboard = [
            [InlineKeyboardButton("ثبت سفارش و درخواست مشاوره", callback_data="start_order")],
            [InlineKeyboardButton("بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = (
            "**فرآیند تولید پروژه در مؤسسه بهادر فیلم (۴ مرحله شفاف):**\n\n"
            "۱. **مشاوره اولیه:** بررسی ایده، نیازسنجی، تعیین اهداف و مخاطب اثر.\n"
            "۲. **پیش‌تولید:** نگارش فیلم‌نامه، استوری‌برد، انتخاب عوامل، لوکیشن و برنامه‌ریزی.\n"
            "۳. **تولید:** تصویربرداری حرفه‌ای با تجهیزات مدرن و کادر مجرب.\n"
            "۴. **تحویل و پس‌تولید:** تدوین دقیق با پریمیر، اصلاح رنگ، صداگذاری و تحویل باکیفیت.\n\n"
            "🎁 **هدیه ویژه:** همراه با یک کلیپ ۱ دقیقه‌ای رایگان برای هر سفارش تا پایان سال ۱۴۰۵."
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "packages":
        keyboard = [
            [InlineKeyboardButton("انتخاب پکیج و ثبت سفارش", callback_data="start_order")],
            [InlineKeyboardButton("بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = (
            "☑ **پکیج های پیشنهادی خدمات:**\n\n"
            "• **پکیج پایه:** مناسب کسب‌وکارها، تولید تیزر معرفی کوتاه، کیفیت استاندارد مناسب شبکه‌های اجتماعی.\n"
            "• **پکیج حرفه‌ای (پیشنهاد ویژه):** ساخت مستند سازمانی یا تیزر کامل، فیلم‌برداری تخصصی، اصلاح رنگ و صداگذاری حرفه‌ای.\n"
            "• **پکیج ویژه (فاخر):** تولید سریال مستندهای بلند تلویزیونی یا پروژه‌های بزرگ سازمانی از صفر تا صد.\n\n"
            "🎁 **هدیه ویژه:** در صورت ثبت سفارش و انجام کار تا پایان سال ۱۴۰۵، یک کلیپ ۱ دقیقه‌ای رایگان تحویل داده خواهد شد.\n\n"
            "برای ثبت سفارش روی دکمه زیر کلیک کنید:"
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "lead_magnet":
        keyboard = [
            [InlineKeyboardButton("وبسایت رسمی", url="https://alibahador.ir")],
            [InlineKeyboardButton("ثبت سفارش و درخواست مشاوره", callback_data="start_order")],
            [InlineKeyboardButton("بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = (
            "**هدیه رایگان شما:**\n\n"
            "**«چک‌لیست طلایی آماده‌سازی و سفارش فیلم و تیزر سازمانی»**\n\n"
            "• **گام اول: تعیین هدف و مخاطب** (چرا و برای چه کسی؟)\n"
            "• **گام دوم: تعیین بودجه و زمان‌بندی** (هزینه‌ها و ددلاین)\n"
            "• **گام سوم: پیام اصلی و ساختار محتوایی** (چه می‌خواهیم بگوییم؟)\n\n"
            "🎁 **هدیه ویژه:** در صورت ثبت سفارش پروژه تا پایان سال ۱۴۰۵، یک کلیپ ۱ دقیقه‌ای رایگان هدیه بگیرید.\n\n"
            "• **گام چهارم: هماهنگی با تیم تولید و مشاوره** (تلفن: ۰۹۲۱۵۶۸۰۱۱۴ - alibahador.ir)"
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown", disable_web_page_preview=True)
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "newsletter_join":
        keyboard = [[InlineKeyboardButton("بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        text = (
            "**خبرنامه آموزشی و هنری بهادر فیلم**\n\n"
            "با عضویت در این خبرنامه، نکات ارزشمند تولید فیلم و پشت‌صحنه‌ها برای شما ارسال می‌شود.\n\n"
            "☑ **شما با موفقیت در لیست مخاطبان ویژه قرار گرفتید.**"
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "faq":
        keyboard = [
            [InlineKeyboardButton("ثبت سفارش و مشاوره", callback_data="start_order")],
            [InlineKeyboardButton("بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = (
            "**پرسش‌های متداول (FAQ):**\n\n"
            "**۱. چگونه می‌توانم سفارش خود را ثبت کنم؟**\n"
            "از طریق دکمه «ثبت سفارش و درخواست مشاوره» در منوی اصلی.\n\n"
            "**۲. هدیه ویژه سفارش‌ها چیست؟**\n"
            "یک کلیپ ۱ دقیقه‌ای رایگان برای سفارش‌های ثبت‌شده تا پایان سال ۱۴۰۵."
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "portfolio":
        keyboard = [
            [InlineKeyboardButton("سریال‌ها و فیلم‌های داستانی", callback_data="port_series")],
            [InlineKeyboardButton("مستندها و مستند داستانی", callback_data="port_docs")],
            [InlineKeyboardButton("پروژه‌های ملی نفت و گاز و کتاب مرجع", callback_data="port_gas")],
            [InlineKeyboardButton("انیمیشن‌های آموزشی و طنز", callback_data="port_anim")],
            [InlineKeyboardButton("جوایز و لوح‌های سپاس", callback_data="port_awards")],
            [InlineKeyboardButton("وبسایت رسمی", url="https://alibahador.ir")],
            [InlineKeyboardButton("بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = "**بخش نمونه کارها و رزومه جامع علی بهادر**\n\nحوزه مورد نظر خود را انتخاب کنید:"
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "port_series":
        keyboard = [
            [InlineKeyboardButton("بهترین تابستان من", callback_data="work_tabestan"), InlineKeyboardButton("عشق سال‌های جنگ", callback_data="work_eshgh")],
            [InlineKeyboardButton("شب هزار و یکم", callback_data="work_shab"), InlineKeyboardButton("قدم زدن در بهشت", callback_data="work_ghadam")],
            [InlineKeyboardButton("ارثیه پرماجرا", callback_data="work_ershieh"), InlineKeyboardButton("شاهزاده و گدا", callback_data="work_shahzadeh")],
            [InlineKeyboardButton("مشتری‌مداری", callback_data="work_moshtari"), InlineKeyboardButton("برکت", callback_data="work_barakat")],
            [InlineKeyboardButton("بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = (
            "**فهرست سریال‌های تلویزیونی و سینمایی:**\n\n"
            "۱. سریال «بهترین تابستان من» (۱۳۷۲)\n"
            "۲. سریال «عشق سال‌های جنگ» (۱۳۷۹)\n"
            "۳. سریال «شب هزار و یکم» (۱۳۸۸)\n"
            "۴. تله‌فیلم «قدم زدن در بهشت» (۱۳۹۱)\n"
            "۵. فیلم «ارثیه پرماجرا» و «شاهزاده و گدا» (۱۳۹۳)\n"
            "۶. مینی‌سریال «برکت» (۱۳۹۷) و سریال «مشتری‌مداری» (۱۴۰۰)\n\n"
            "برای مشاهده جزئیات و تصاویر هر اثر روی دکمه مربوطه کلیک کنید:"
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "port_docs":
        keyboard = [
            [InlineKeyboardButton("مستند زندگی و سایر آثار", callback_data="work_zendegi")],
            [InlineKeyboardButton("مستندهای برون‌مرزی (نوروز)", callback_data="work_nowruz")],
            [InlineKeyboardButton("مجموعه مستند روایتی از رسانه", callback_data="work_resaneh")],
            [InlineKeyboardButton("بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = "**بخش مستندها و مستند داستانی:**\n\nلطفاً بخش مورد نظر را انتخاب کنید:"
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "port_gas":
        keyboard = [
            [InlineKeyboardButton("کتاب مرجع گاز؛ انرژی پاک...", callback_data="work_gas_book")],
            [InlineKeyboardButton("بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = "**پروژه‌های ملی نفت و گاز و کتاب مرجع (۱۰۱۸ صفحه)**\n\nبرای مشاهده تصویر کتاب کلیک کنید:"
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "port_anim":
        keyboard = [
            [InlineKeyboardButton("انیمیشن اسرافی و انصافی", callback_data="work_esrafi")],
            [InlineKeyboardButton("بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = "**انیمیشن‌های آموزشی و طنز (اسرافی و انصافی)**\n\nبرای مشاهده پوستر کلیک کنید:"
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "port_awards":
        keyboard = [
            [InlineKeyboardButton("لوح تقدیر جشنواره رشد و دفاع مقدس", callback_data="award_roshd")],
            [InlineKeyboardButton("تندیس‌ها و لوح‌های تقدیر ویژه", callback_data="award_tandis")],
            [InlineKeyboardButton("بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = "**افتخارات، جوایز و لوح‌های سپاس:**\n\nانتخاب کنید:"
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    # نمایش عکس‌ها با پشتیبانی متن جایگزین در صورت بروز خطا
    elif data == "work_tabestan":
        kb = [[InlineKeyboardButton("بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "**(۱۳۷۲) بهترین تابستان من**\nکارگردانی سریال طنز دفاع مقدس در ۸ قسمت."
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAANZarTpN4VZ_zuBvY8qfr8XmbNw7pkAAjQQaxsIQqhRXfvpAAFEs83zAQADAgADEQADPQQ", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "work_eshgh":
        kb = [[InlineKeyboardButton("بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "**(۱۳۷۹) عشق سال‌های جنگ**\nکارگردانی و تهیه‌کنندگی مشترک."
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAAIBXGq1RFFgqvcgd_P55t87XY74WIPKAALSEGsbJUKoUZfj1JAQyVznAQADAgADEQADPQQ", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "work_shab":
        kb = [[InlineKeyboardButton("بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "**(۱۳۸۸) شب هزار و یکم**\nکارگردانی سریال ۲۳ قسمتی شبکه اول سیما."
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAAPBarUluUVD4nM87cFP8BgXuq5-U_oAAngQaxsIQqhRh6dUdcL50N0BAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "work_ghadam":
        kb = [[InlineKeyboardButton("بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "**(۱۳۹۱) قدم زدن در بهشت**\nکارگردانی تله‌فیلم با ساختار سینمایی."
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAAO9arUlhU6N9Z12yrlgket0xeRDKQUAAnYQaxsIQqhRldr720T2dboBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "work_ershieh":
        kb = [[InlineKeyboardButton("بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "**(۱۳۹۳) ارثیه پرماجرا**\nتهیه‌کنندگی فیلم سینمایی ویدیویی طنز اجتماعی."
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAANkarTw6xfxZ84odXO_PlgJBVLWvY8AAjwQaxsIQqhR3hmwjUYRMOWBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "work_shahzadeh":
        kb = [[InlineKeyboardButton("بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "**(۱۳۹۳) شاهزاده و گدا**\nتهیه‌کنندگی فیلم سینمایی ویدیویی."
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAANmarTxHy9f8plmCbwBwH-n-0U3eUcAAj4QaxslQqhR79dvxxWcmpIBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "work_moshtari":
        kb = [[InlineKeyboardButton("بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "**(۱۴۰۰) مشتری‌مداری**\nسریال آموزشی ۳۰ قسمتی."
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAANqarTxuueYW1gjMcHlaCaDZJXtJ1EAAkEQaxslQqhR-aYKXskUhHIBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "work_barakat":
        kb = [[InlineKeyboardButton("بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "**(۱۳۹۷) برکت**\nتهیه‌کنندگی و کارگردانی مینی‌سریال ۴ قسمتی."
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAANuarTyOwkGmkfs6tcNodNBGzujgCwAAkMQaxslQqhRRxnzoph9E4EBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "work_zendegi":
        kb = [[InlineKeyboardButton("بازگشت به مستندها", callback_data="port_docs")]]
        caption = "**مستند زندگی**\nبرنده سه جایزه معتبر جشنواره‌ای."
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAAPgarUK-ilwHxyH6dpdF6lUk7u_mbwAAnoQaxslQqhRW40w4rUt2MsBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "work_nowruz":
        kb = [[InlineKeyboardButton("بازگشت به مستندها", callback_data="port_docs")]]
        caption = "**مستندهای برون‌مرزی نوروز در آسیای میانه**"
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAANvarTysXz-nKqjilkshH7l-IZI_8AAkUQaxslQqhR_zB2Ple2rxMBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "work_resaneh":
        kb = [[InlineKeyboardButton("بازگشت به مستندها", callback_data="port_docs")]]
        text = "**(۱۴۰۳ - ۱۴۰۴) مجموعه مستند روایتی از رسانه**\nبررسی مدیریت رسانه در دوران مختلف."
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "work_gas_book":
        kb = [[InlineKeyboardButton("بازگشت به پروژه‌های گاز", callback_data="port_gas")]]
        caption = "**کتاب مرجع گاز؛ انرژی پاک با نیم قرن تلاش (۱۰۱۸ صفحه)**"
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAANsarTx9X_9z_IFk7DvWGmtVGkGBOAAAkIQaxsIQqhRUjAa4c-6XLWBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "work_esrafi":
        kb = [[InlineKeyboardButton("بازگشت به انیمیشن‌ها", callback_data="port_anim")]]
        caption = "**انیمیشن آموزشی اسرافی و انصافی**"
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAAOXarT7ccFh9OXiCdDZEU8Ke77rJ3gAAI8QaxslQqhRdziJ4NbzhYQBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "award_roshd":
        kb = [[InlineKeyboardButton("بازگشت به جوایز", callback_data="port_awards")]]
        caption = "**لوح تقدیر جشنواره بین‌المللی فیلم رشد و جشنواره دفاع مقدس**"
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAAOBarT63lwTbK1i98T2La7qVD3q4gEAAIQQaxsIQqhRbvL3WI2R2JKBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "award_tandis":
        kb = [[InlineKeyboardButton("بازگشت به جوایز", callback_data="port_awards")]]
        caption = "**تندیس‌ها، لوح‌های سپاس و تقدیر ویژه مدیران ارشد**"
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAAODarT69110d1-rQQs-AwTKjAO7WQSAAIUQaxslQqhRpgYVe0-1E6QBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "interviews":
        keyboard = [
            [InlineKeyboardButton("مصاحبه روزنامه اطلاعات (۲۰ مرداد ۱۴۰۵)", callback_data="view_ettelaat_img")],
            [InlineKeyboardButton("مصاحبه هفته‌نامه صدا و سیما (مرداد ۱۴۰۵)", callback_data="view_sedavasima_img")],
            [InlineKeyboardButton("بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = "**بخش مصاحبه‌ها و پوشش رسانه‌ای**\n\nانتخاب کنید:"
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "view_ettelaat_img":
        keyboard = [[InlineKeyboardButton("بازگشت به بخش مصاحبه‌ها", callback_data="interviews")]]
        caption_text = (
            "**(۲۰ مرداد ۱۴۰۵) مصاحبه با روزنامه اطلاعات**\n\n"
            "عنوان: سینمای مستند به مدیرانی جسور نیاز دارد\n\n"
            "[مشاهده آنلاین در سایت اطلاعات](https://www.ettelaat.com/news/161537/%D8%B3%DB%8C%D9%86%D9%85%D8%A7%DB%8C-%D9%85%D8%B3%D8%AA%D9%86%D8%AF-%D8%A8%D9%87-%D9%85%D8%AF%DB%8C%D8%B1%D8%A7%D9%86%DB%8C-%D8%AC%D8%B3%D9%88%D8%B1-%D9%86%DB%8C%D8%A7%D8%B2-%D8%AF%D8%A7%D8%B1%D8%AF)"
        )
        try:
            await query.message.reply_photo(
                photo="https://www.ettelaat.com/files/fa/news/1405/5/20/161537_485.jpg",
                caption=caption_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        except Exception:
            await query.message.reply_text(caption_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "view_sedavasima_img":
        keyboard = [
            [InlineKeyboardButton("مشاهده آنلاین در سایت", url="https://iribonline.ir/portal/newsview/125403")],
            [InlineKeyboardButton("بازگشت به بخش مصاحبه‌ها", callback_data="interviews")]
        ]
        caption_text = (
            "☑ **گفت‌وگو با ۲ چهره باسابقه رسانه ملی با تجربه زیسته دفاع مقدس**\n\n"
            "**تصویر مقاومت در آیینه رسانه**\n\n"
            "علی بهادر: **روایت یک عمر تصویرگری حماسه**"
        )
        await query.message.reply_text(caption_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown", disable_web_page_preview=True)
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "about":
        keyboard = [[InlineKeyboardButton("بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        about_text = (
            "☑ **درباره مدیرعامل:**\n\n"
            "علی بهادر، کارگردان، تهیه‌کننده و نویسنده با بیش از چهار دهه سابقه فعالیت در صداوسیما، فارغ‌التحصیل کارشناسی کارگردانی و کارشناسی ارشد ادبیات نمایشی."
        )
        await query.message.reply_text(about_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
            
    elif data == "digital_card":
        keyboard = [
            [InlineKeyboardButton("وبسایت رسمی", url="https://alibahador.ir")],
            [InlineKeyboardButton("بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = (
            "**کارت ویزیت دیجیتال مؤسسه بهادر فیلم**\n\n"
            "• مدیرعامل: علی بهادر\n"
            "• شماره تماس مستقیم: ۰۹۲۱۵۶۸۰۱۱۴\n"
            "• وبسایت: alibahador.ir"
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats_command))
    
    order_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_order_process, pattern="^start_order$")],
        states={
            PACKAGE_CHOICE: [CallbackQueryHandler(receive_package_choice, pattern="^pkg_")],
            USER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_name)],
            USER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_phone)]
        },
        fallbacks=[CallbackQueryHandler(button_handler, pattern="^back_to_menu$")]
    )
    
    contact_admin_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(contact_admin_start, pattern="^contact_admin$")],
        states={
            ADMIN_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_admin_message)]
        },
        fallbacks=[CallbackCodeHandler if 'CallbackCodeHandler' in globals() else CallbackQueryHandler(button_handler, pattern="^back_to_menu$")]
    )
    
    application.add_handler(order_conv_handler)
    application.add_handler(contact_admin_handler)
    application.add_handler(CallbackQueryHandler(button_handler))
    
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    logger.info("Bot is running with two-column layout, active stats command, and gift message up to 1405...")
    application.run_polling()

if __name__ == '__main__':
    main()
