import os
import logging
import random
import datetime
from flask import Flask, jsonify
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler

# تنظیمات لاگینگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN", "8627933053:AAG1-UaJK5DkKpa330nvd3WmBepC8psEVg0")
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
    return "Bahador Film Bot is running live with fully fixed interactive workflow and portfolio!"

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

# منوی اصلی کامل و جامع
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("💬 ثبت سفارش و درخواست مشاوره", callback_data="start_order")],
        [InlineKeyboardButton("🎁 هدیه رایگان (فایل راهنما)", callback_data="lead_magnet"), InlineKeyboardButton("📦 پکیج‌های خدمات", callback_data="packages")],
        [InlineKeyboardButton("🎬 نمونه کارها و رزومه کامل", callback_data="portfolio"), InlineKeyboardButton("⚙️ فرآیند کار ما", callback_data="workflow")],
        [InlineKeyboardButton("👤 درباره مدیرعامل", callback_data="about"), InlineKeyboardButton("💳 کارت ویزیت دیجیتال", callback_data="digital_card")],
        [InlineKeyboardButton("💬 ارسال پیام به مدیریت", callback_data="contact_admin"), InlineKeyboardButton("📰 مصاحبه‌ها و رسانه", callback_data="interviews")],
        [InlineKeyboardButton("🔔 خبرنامه آموزشی", callback_data="newsletter_join"), InlineKeyboardButton("❓ پرسش‌های متداول (FAQ)", callback_data="faq")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    stats_data["total_visits"] += 1
    stats_data["unique_users"].add(user.id)
    
    args = context.args
    if args:
        source = args[0]
        logger.info(f"کاربر جدید از منبع ورودی '{source}' وارد ربات شد. کاربر ID: {user.id}")

    welcome_text = (
        "🎬 **به مؤسسه هنری بهادر فیلم خوش آمدید!**\n\n"
        "سازنده سریال، مستندهای فاخر تلویزیونی، تیزر و انیمیشن.\n"
        "مدیریت: علی بهادر (کارگردان و تهیه‌کننده)\n\n"
        "👇 چه پروژه‌ای در ذهن دارید؟ از منوی زیر انتخاب کنید:"
    )
    
    if update.callback_query:
        await update.callback_query.message.reply_text(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")
        await update.callback_query.answer()
    else:
        await update.message.reply_text(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"📊 **آمار بازدید و تعاملات ربات مؤسسه بهادر فیلم:**\n\n"
        f"🔹 کل بازدیدها: {stats_data['total_visits']}\n"
        f"🔹 کاربران یکتا: {len(stats_data['unique_users'])}\n"
        f"🔹 مشاوره‌ها و سفارش‌های ثبت‌شده: {stats_data['orders_count']}\n"
        f"🔹 پیام‌های دریافتی مدیریت: {stats_data['messages_count']}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# --- جریان تعاملی ثبت سفارش و پکیج‌ها (ConversationHandler) ---
async def start_order_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔹 پکیج پایه (مناسب کسب‌وکارها)", callback_data="pkg_base")],
        [InlineKeyboardButton("🔸 پکیج حرفه‌ای (مستند و تیزر ⭐)", callback_data="pkg_pro")],
        [InlineKeyboardButton("🔹 پکیج ویژه / فاخر (سریال و پروژه‌های بزرگ)", callback_data="pkg_vip")],
        [InlineKeyboardButton("💬 مشاوره عمومی / پروژه دلخواه", callback_data="pkg_custom")],
        [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
    ]
    text = (
        "📦 **انتخاب پکیج خدمات و ثبت سفارش:**\n\n"
        "🎁 **هدیه ویژه:** در صورت سفارش هر پروژه، یک کلیپ ۱ دقیقه‌ای رایگان به سفارش‌دهنده تحویل خواهد شد.\n\n"
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
        "pkg_base": "پکیج پایه (مناسب کسب‌وکارها)",
        "pkg_pro": "پکیج حرفه‌ای (مستند و تیزر ویژه)",
        "pkg_vip": "پکیج ویژه / فاخر (سریال و پروژه‌های بزرگ)",
        "pkg_custom": "مشاوره عمومی / پروژه دلخواه"
    }
    
    context.user_data['selected_package'] = pkg_names.get(data, "پکیج سفارشی")
    
    keyboard = [[InlineKeyboardButton("🔙 انصراف و بازگشت", callback_data="back_to_menu")]]
    text = (
        f"✅ پکیج انتخابی شما: **{context.user_data['selected_package']}**\n\n"
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
    
    keyboard = [[InlineKeyboardButton("🔙 انصراف و بازگشت", callback_data="back_to_menu")]]
    text = (
        f"متشکرم **{user_name} عزیز**.\n\n"
        "لطفاً **شماره تماس** خود (مثلاً 0912...) را ارسال کنید تا کارشناسان ما با شما تماس بگیرند:"
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
        "🛒 **سفارش / درخواست مشاوره جدید ثبت شد!**\n\n"
        f"📦 **پکیج:** {package}\n"
        f"👤 **نام:** {name}\n"
        f"📞 **شماره تماس:** `{phone}`\n"
        f"یوزرنیم تلگرام: @{user.username or 'ندارد'} (ID: `{user.id}`)\n"
        f"🔖 **کد پیگیری:** `{tracking_code}`"
    )
    
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_notification, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error sending order to admin: {e}")
        
    success_text = (
        "✅ **پیام شما ثبت شد. در اسرع وقت با شما تماس گرفته خواهد شد.**\n"
        "⏰ ساعات پاسخگویی: ۹ صبح تا ساعت ۲۰\n\n"
        f"🎁 **یادآوری هدیه ویژه:** یک کلیپ ۱ دقیقه‌ای رایگان به سفارش شما تعلق خواهد گرفت.\n"
        f"🔖 **کد پیگیری سفارش:** `{tracking_code}`\n\n"
        "از اعتماد شما سپاسگزاریم. 🌹"
    )
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
    await update.message.reply_text(success_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return ConversationHandler.END

# --- هندلر ارسال پیام مستقیم به مدیریت ---
async def contact_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
    text = (
        "💬 **ارسال پیام مستقیم به مدیریت:**\n\n"
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
        "📩 **پیام جدید به مدیریت**\n\n"
        f"👤 **فرستنده:** {user.first_name} {user.last_name or ''}\n"
        f"یوزرنیم: @{user.username or 'ندارد'} (ID: `{user.id}`)\n"
        f"🔖 **کد پیگیری:** `{tracking_code}`\n\n"
        f"💬 **متن پیام:**\n{user_text}"
    )
    
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_notification, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error sending message to admin chat: {e}")

    success_response = (
        "✅ **پیام شما ثبت شد. در اسرع وقت با شما تماس گرفته خواهد شد.**\n"
        "⏰ ساعات پاسخگویی: ۹ صبح تا ساعت ۲۰\n\n"
        f"🔖 **کد پیگیری شما:** `{tracking_code}`\n"
        "از حسن توجه و ارتباط شما سپاسگزاریم. 🌹"
    )
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
    await update.message.reply_text(success_response, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return ConversationHandler.END

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_to_menu":
        await query.message.reply_text(
            "🎬 **مؤسسه هنری بهادر فیلم**\n\n👇 از منوی زیر انتخاب کنید:",
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "workflow":
        keyboard = [
            [InlineKeyboardButton("💬 ثبت سفارش و درخواست مشاوره", callback_data="start_order")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = (
            "⚙️ **فرآیند تولید پروژه در مؤسسه بهادر فیلم (۴ مرحله شفاف):**\n\n"
            "۱️⃣ **مشاوره اولیه:** بررسی ایده، نیازسنجی، تعیین اهداف و مخاطب اثر.\n"
            "۲️⃣ **پیش‌تولید:** نگارش فیلم‌نامه، استوری‌برد، انتخاب عوامل، لوکیشن و برنامه‌ریزی.\n"
            "۳️⃣ **تولید:** تصویربرداری حرفه‌ای با تجهیزات مدرن و کادر مجرب.\n"
            "۴️⃣ **تحویل و پس‌تولید:** تدوین دقیق با پریمیر، اصلاح رنگ، صداگذاری و تحویل باکیفیت.\n\n"
            "🎁 **هدیه ویژه:** همراه با یک کلیپ ۱ دقیقه‌ای رایگان برای هر سفارش!"
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "packages":
        keyboard = [
            [InlineKeyboardButton("💬 انتخاب پکیج و ثبت سفارش", callback_data="start_order")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = (
            "📦 **پکیج‌های پیشنهادی خدمات:**\n\n"
            "🔹 **پکیج پایه (مناسب کسب‌وکارها):** تولید تیزر معرفی کوتاه، کیفیت استاندارد، مناسب شبکه‌های اجتماعی.\n"
            "🔸 **پکیج حرفه‌ای (پیشنهاد ویژه ⭐):** ساخت مستند سازمانی یا تیزر کامل، فیلم‌برداری تخصصی، اصلاح رنگ و صداگذاری حرفه‌ای.\n"
            "🔹 **پکیج ویژه (فاخر):** تولید سریال، مستندهای بلند تلویزیونی یا پروژه‌های بزرگ سازمانی از صفر تا صد.\n\n"
            "🎁 **هدیه ویژه:** در صورت سفارش هر پروژه، یک کلیپ ۱ دقیقه‌ای رایگان به سفارش‌دهنده تحویل خواهد شد.\n\n"
            "برای ثبت سفارش روی دکمه زیر کلیک کنید."
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    # --- هدیه رایگان (فایل راهنما) شامل هدیه کلیپ ۱ دقیقه‌ای ---
    elif data == "lead_magnet":
        keyboard = [
            [InlineKeyboardButton("🌐 وب‌سایت رسمی", url="https://alibahador.ir")],
            [InlineKeyboardButton("💬 ثبت سفارش و درخواست مشاوره", callback_data="start_order")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = (
            "🎁 **هدیه رایگان شما:**\n"
            "**«چک‌لیست طلایی آماده‌سازی و سفارش فیلم و تیزر سازمانی»**\n\n"
            "مقدمه کوتاه:\n"
            "اهمیت ساخت ویدیو و تیزر در معرفی برند، محصول یا سازمان و نقش کلیدی پیش‌تولید در کاهش هزینه‌ها و افزایش اثربخشی.\n\n"
            "📌 **گام اول: تعیین هدف و مخاطب (چرا و برای چه کسی؟)**\n"
            "• مشخص کردن هدف اصلی پروژه (فروش، آگاهی از برند، آموزشی، مستند سازمانی و...)\n"
            "• شناخت دقیق مخاطب هدف و لحن مناسب برای ارتباط با آن‌ها.\n\n"
            "📌 **گام دوم: تعیین بودجه و زمان‌بندی (هزینه‌ها و ددلاین)**\n"
            "• برآورد اولیه بودجه متناسب با اهداف پروژه.\n"
            "• مشخص کردن بازه زمانی تحویل و تاریخ‌های کلیدی رویدادها یا انتشار.\n\n"
            "📌 **گام سوم: پیام اصلی و ساختار محتوایی (چه می‌خواهیم بگوییم؟)**\n"
            "• خلاصه کردن پیام کلیدی در یک جمله طلایی.\n"
            "• تعیین نوع محتوا (مستند، تیزر داستانی، موشن‌گرافیک، گزارش عملکرد و...)\n\n"
            "🎁 **هدیه ویژه همراه با فایل:** در صورت ثبت سفارش هر پروژه، یک کلیپ ۱ دقیقه‌ای رایگان به سفارش‌دهنده تحویل خواهد شد.\n\n"
            "📌 **گام چهارم: هماهنگی با تیم تولید و مشاوره**\n"
            "راه‌های ارتباطی با واحد مشاوره و ثبت سفارش از طریق ربات تلگرام، وب‌سایت رسمی (alibahador.ir) و تماس مستقیم با شماره `+989121711063`.\n\n"
            "⏰ ساعات پاسخگویی واحد مشاوره: شنبه تا چهارشنبه، ساعت ۹ الی ۱۷."
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown", disable_web_page_preview=True)
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "newsletter_join":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        text = (
            "🔔 **خبرنامه آموزشی و هنری بهادر فیلم**\n\n"
            "با عضویت در این خبرنامه، ماهی ۱ الی ۲ بار نکات ارزشمند تولید فیلم، پشت‌صحنه‌ها و اخبار کارهای جدید مستقیماً برای شما ارسال می‌شود.\n\n"
            "شما با موفقیت در لیست مخاطبان ویژه قرار گرفتید! ✅"
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "portfolio":
        keyboard = [
            [InlineKeyboardButton("📺 سریال‌ها و فیلم‌های داستانی", callback_data="port_series")],
            [InlineKeyboardButton("📽️ مستندها و مستند داستانی", callback_data="port_docs")],
            [InlineKeyboardButton("⛽ پروژه‌های ملی نفت و گاز و کتاب مرجع", callback_data="port_gas")],
            [InlineKeyboardButton("🎨 انیمیشن‌های آموزشی و طنز", callback_data="port_anim")],
            [InlineKeyboardButton("🏆 جوایز و لوح‌های سپاس", callback_data="port_awards")],
            [InlineKeyboardButton("🌐 وب‌سایت رسمی", url="https://alibahador.ir")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = "🎬 **بخش نمونه کارها و رزومه جامع علی بهادر:**\n\nحوزه مورد نظر خود را انتخاب کنید:"
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
    
    elif data == "port_series":
        keyboard = [
            [InlineKeyboardButton("📺 بهترین تابستان من (۱۳۷۲)", callback_data="work_tabestan")],
            [InlineKeyboardButton("📺 عشق سال‌های جنگ (۱۳۷۹)", callback_data="work_eshgh")],
            [InlineKeyboardButton("📺 شب هزار و یکم (۱۳۸۸)", callback_data="work_shab")],
            [InlineKeyboardButton("🎬 قدم زدن در بهشت (۱۳۹۱)", callback_data="work_ghadam")],
            [InlineKeyboardButton("🎬 ارثیه پرماجرا (۱۳۹۳)", callback_data="work_ershieh")],
            [InlineKeyboardButton("🎬 شاهزاده و گدا (۱۳۹۳)", callback_data="work_shahzadeh")],
            [InlineKeyboardButton("🎬 مشتری‌مداری (۱۴۰۰)", callback_data="work_moshtari")],
            [InlineKeyboardButton("🎬 برکت (۱۳۹۷)", callback_data="work_barakat")],
            [InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = (
            "📺 **فهرست کامل الف - بخش سریال های تلویزیونی ، سینمایی و داستانی کوتاه:**\n\n"
            "۱- تهیه‌کنندگی فیلم سینمایی‌ویدیویی «ارثیه پرماجرا» (۱۳۹۳) - کارگردان: رسول محمدی، نویسنده: سینا سعید وزیری، موضوع طنز اجتماعی (پخش در شبکه خانگی).\n"
            "۲- تهیه‌کنندگی فیلم سینمایی‌ویدیویی «شاهزاده و گدا» (۱۳۹۳) - کارگردان: رسول محمدی، نویسنده: قربان محمدپور - رهام تربیت، با موضوع طنز اجتماعی.\n"
            "۳- کارگردانی فیلم سینمایی-تلویزیونی (تله‌فیلم) «قدم زدن در بهشت» (از بهمن ۱۳۹۱ تا ۱۳۹۳) - با نوگرایی خاص، پخش از شبکه‌های ۱، ۲، ۳، نمایش و مرکز همدان.\n"
            "۴- کارگردانی سریال تلویزیونی «شب هزار و یکم» (پاییز ۱۳۸۸) - ۲۳ قسمت ۴۰ دقیقه‌ای با موضوع نقش پزشکان در دفاع مقدس (پخش از شبکه اول سیما) با بازی دانیال حکیمی، علیرضا خمسه، مهشید افشارزاده، یوسف مرادیان و...\n"
            "۵- کارگردانی سریال تلویزیونی «عشق سالهای جنگ» (۱۳۷۹) - ۱۳ قسمت ۴۵ دقیقه‌ای با موضوع دفاع مقدس (پخش از شبکه سوم سیما - تهیه‌کنندگی مشترک) با بازی فرهاد جم، جعفر دهقان، اندیشه فولادوند، پرستو صالحی و...\n"
            "۶- کارگردانی سریال تلویزیونی «بهترین تابستان من» (۱۳۷۲) - طنز دفاع مقدس در ۸ قسمت ۴۵ دقیقه‌ای، پرمخاطب‌ترین مجموعه تلویزیونی زمان پخش، بازپخش متعدد.\n"
            "۷- کارگردانی فیلم داستانی کوتاه «آن شب» (۱۳۶۹) با موضوع دفاع مقدس.\n"
            "۸- کارگردانی فیلم داستانی کوتاه «گردنبند» (۱۳۶۹) با موضوع دفاع مقدس.\n"
            "۹- تهیه‌کنندگی و کارگردانی مینی‌سریال «برکت» در چهار قسمت ۴۵ دقیقه‌ای (تولید ۱۳۹۷).\n"
            "۱۰- تهیه‌کنندگی و کارگردانی سریال آموزشی «مشتری‌مداری» در ۳۰ قسمت با هدف جلب رضایت مردم در حوزه‌های کسب‌وکار و خدمات پستی (تولید ۱۴۰۰).\n\n"
            "👇 برای مشاهده تصاویر آثار کلیک کنید:"
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "port_docs":
        keyboard = [
            [InlineKeyboardButton("📽️ مستند «زندگی» و آثار دیگر", callback_data="work_zendegi")],
            [InlineKeyboardButton("📽️ مستندهای برون‌مرزی (نوروز و آسیای میانه)", callback_data="work_nowruz")],
            [InlineKeyboardButton("📽️ مجموعه مستند «روایتی از رسانه»", callback_data="work_resaneh")],
            [InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = (
            "📽️ **فهرست کامل ب - بخش مستند و مستند داستانی:**\n\n"
            "• فیلم «زندگی» (نویسندگی و کارگردانی) - برنده سه جایزه از جشنواره فیلم دفاع مقدس، بیست‌ودومین جشنواره بین‌المللی فیلم‌های آموزشی و تربیتی رشد، و دومین جشنواره فیلم کوتاه همدان.\n"
            "• فیلم «گل‌های مثل هم» (نویسندگی و کارگردانی) - شرکت در بخش مسابقه جشنواره فیلم دفاع مقدس.\n"
            "• مجموعه مستند «ولی نعمتان انقلاب» در ۱۵ قسمت ۳۰ دقیقه‌ای.\n"
            "• مجموعه مستند «زنبورداری در ایران» (تهیه‌کنندگی و کارگردانی) - برنده جایزه ویژه جشنواره سوره.\n"
            "• مجموعه ۱۵ قسمتی «همدلی» با موضوع جوانان و دفاع مقدس.\n"
            "• مجموعه مستند «جهاد در جهاد» در ۷ قسمت ۳۰ دقیقه‌ای.\n"
            "• مجموعه‌های برون‌مرزی تاجیکستان و آسیای میانه: «بدخشان بام جهان»، «نوروز در تاجیکستان»، «نوروز در ازبکستان» (برنده دو جایزه بهترین تهیه‌کنندگی و تدوین از جشنواره دفاتر خارج از کشور), «نوروز در قزاقستان»، «نوروز در ترکمنستان»، «میهمانی خدا در تاجیکستان»، «ایران‌شناسان در تاجیکستان و ازبکستان»، «میر سید علی همدانی» و «بوی جوی مولیان آید همی».\n"
            "• مجموعه‌های تلویزیونی و معارفی: «دعای جوشن کبیر» (۱۳ قسمت), «قدسیان خاک» (۷ قسمت شبکه یک), «نخلهای صبور» (۳۰ قسمت شبکه تهران), «شن‌های شاهد» (تهیه مشترک ۱۳ قسمت), «عطر میعاد» (۷ قسمت حج), «حج اکبر» (شبکه العالم), «بچه‌های مسجد» (شبکه ۵), «نسیم کوثر» (۲۶ قسمت).\n"
            "• مستندهای پژوهشی و تاریخی: «نیم قرن تلاش و تجربه» (تاریخ ۵۰ ساله گاز - ۱۳۹۴), «گام‌های بزرگ همدلی» (۱۳۹۵), «روایت خدمت» (۱۴۰۲), مجموعه ۱۰ قسمتی «تلاش بی‌پایان» (اورال صنعت گاز - ۱۴۰۴), و مجموعه مستند تحقیقی-پژوهشی ۱۸ قسمتی **«روایتی از رسانه»** (بررسی مدیریت رسانه در دوران آقایان محمد هاشمی، شهید علی لاریجانی و عزت‌الله ضرغامی در سال‌های ۱۴۰۳–۱۴۰۴).\n\n"
            "👇 برای مشاهده مستندهای شاخص کلیک کنید:"
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "port_gas":
        keyboard = [
            [InlineKeyboardButton("📚 کتاب مرجع «گاز؛ انرژی پاک...»", callback_data="work_gas_book")],
            [InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = (
            "⛽ **پروژه‌های ملی نفت و گاز و تألیفات:**\n\n"
            "• مجموعه مستند پژوهشی-تاریخی «گاز انرژی پاک با نیم قرن تلاش» در ۶۳ برنامه ۶۰ دقیقه‌ای (مجموعاً ۳۷۰۰ دقیقه).\n"
            "• **کتاب مرجع «گاز انرژی پاک با نیم قرن تلاش»:** ۱۰۱۸ صفحه، چاپ و انتشار در سال ۱۳۹۵. رونمایی رسمی در مراسم پنجاهمین سالگرد تأسیس شرکت ملی گاز ایران با حضور ریاست محترم جمهوری اسلامی ایران.\n"
            "• پوشش تصویری همایش‌ها و پروژه‌ها: افتتاح گازرسانی روستاهای کرمانشاه با حضور وزیر نفت و مدیرعامل شرکت ملی گاز (۱۳۹۹), پوشش ویدیوکنفرانس پروژه‌ها با ریاست جمهوری، تولید آرم‌استیشن‌های خبری، مستند دیسپچینگ ملی گاز، مستند ایمن‌سازی ایستگاه‌های TBS/DRS، مستند هات‌تپ و آموزش خوردگی خطوط لوله.\n\n"
            "👇 برای مشاهده تصویر کتاب مرجع کلیک کنید:"
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "port_anim":
        keyboard = [
            [InlineKeyboardButton("🎨 انیمیشن طنز «اسرافی و انصافی»", callback_data="work_esrafi")],
            [InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = (
            "🎨 **انیمیشن‌های آموزشی و طنز:**\n\n"
            "• مجموعه انیمیشن طنز-موزیکال «اسرافی و انصافی» (فصل اول تولید ۱۳۹۷-۱۳۹۸، فصل دوم تولید ۱۳۹۸، فصل سوم تولید ۱۳۹۹-۱۴۰۰) با موضوع ایمنی گاز شهری و مشاوره کاراکتر حکیمانه «انصافی» به خانواده اسرافی.\n"
            "• تولید دو قسمت انیمیشن آموزشی برای مدیریت راه‌ها و حمل‌ونقل جاده‌ای استان همدان (۱۳۹۹).\n\n"
            "👇 برای مشاهده پوستر انیمیشن کلیک کنید:"
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "port_awards":
        keyboard = [
            [InlineKeyboardButton("🏆 لوح تقدیر جشنواره رشد و دفاع مقدس", callback_data="award_roshd")],
            [InlineKeyboardButton("🏆 لوح‌ها و تندیس‌های تقدیر ویژه", callback_data="award_tandis")],
            [InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = "🏆 **افتخارات، جوایز و لوح‌های سپاس:**\n\nلطفاً گزینه مورد نظر را انتخاب کنید:"
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "work_tabestan":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "📺 **بهترین تابستان من (۱۳۷۲)**\nکارگردانی سریال طنز دفاع مقدس در ۸ قسمت ۴۵ دقیقه‌ای؛ پرمخاطب‌ترین مجموعه تلویزیونی زمان پخش."
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAANZarTpN4VZ_zuBvY8qfr8XmbNw7pkAAjQQaxslQqhRXfvpAAFEs83zAQADAgADeQADPQQ", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "work_eshgh":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "📺 **عشق سال‌های جنگ (۱۳۷۹)**\nکارگردانی و تهیه‌کنندگی مشترک در ۱۳ قسمت ۴۵ دقیقه‌ای با موضوع دفاع مقدس."
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAAIBXGq1RFFgqvcgd_P55t87XY74WlPkAALSEGsbJUKoUZfj1JAQyVznAQADAgADeQADPQQ", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "work_shab":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "📺 **شب هزار و یکم (۱۳۸۸)**\nکارگردانی سریال ۲۳ قسمتی با موضوع نقش پزشکان در دفاع مقدس، محصول شبکه اول سیما."
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAAPBarUIuUVD4nM87cFP8BgXuq5-U_oAAngQaxslQqhRh6dUdcL50N0BAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "work_ghadam":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "🎬 **قدم زدن در بهشت (۱۳۹۱)**\nکارگردانی تله‌فیلم با نوگرایی خاص و ساختار سینمایی."
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAAO9arUIhU6N9Z12yrIgket0xeRDKQUAAnYQaxslQqhRIdr720T2dboBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "work_ershieh":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "🎬 **ارثیه پرماجرا (۱۳۹۳)**\nتهیه‌کنندگی فیلم سینمایی-ویدیویی با موضوع طنز اجتماعی (پخش در شبکه خانگی)."
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAANkarTw6xfxZ84odXO_PlgJBVLWvY8AAjwQaxslQqhR3hmwjUYRM0wBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "work_shahzadeh":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "🎬 **شاهزاده و گدا (۱۳۹۳)**\nتهیه‌کنندگی فیلم سینمایی-ویدیویی طنز اجتماعی."
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAANmarTxHy9f8plmCbwBwH-n-0U3eUcAAj4QaxslQqhR79dvxxWcmpIBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "work_moshtari":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "🎬 **مشتری‌مداری (۱۴۰۰)**\nسریال آموزشی ۳۰ قسمتی با هدف جلب رضایت مردم در کسب‌وکار."
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAANqarTxuueYW1gjMcHlaCaDZJXtJ1EAAkEQaxslQqhR-aYKXskUhHIBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "work_barakat":
        kb = [[InlineKeyboardButton("🔙 بازگشت به سریال‌ها", callback_data="port_series")]]
        caption = "🎬 **برکت (۱۳۹۷)**\nتهیه‌کنندگی و کارگردانی مینی‌سریال ۴ قسمتی."
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAANuarTyOwkGmkfs6tcNodNBGzujgCwAAkMQaxslQqhRRxnzoph9E4EBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_node="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "work_zendegi":
        kb = [[InlineKeyboardButton("🔙 بازگشت به مستندها", callback_data="port_docs")]]
        caption = "📽️ **مستند «زندگی»**\nبرنده سه جایزه از جشنواره فیلم دفاع مقدس، جشنواره رشد و جشنواره همدان."
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAAPgarUK-iIwHxyH6dpdF6lUk7u_mbwAAnoQaxslQqhRW40w4rUt2MsBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "work_nowruz":
        kb = [[InlineKeyboardButton("🔙 بازگشت به مستندها", callback_data="port_docs")]]
        caption = "📽️ **مستندهای برون‌مرزی (نوروز در آسیای میانه)**\nتصویربرداری و کارگردانی آیین‌های نوروزی در تاجیکستان، ازبکستان و..."
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAANvarTysXz-nKqjilkshH7l-IZl_8AAkUQaxslQqhR_zB2Ple2rxMBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    # --- اصلاح شده دقیق: نمایش مستند «روایتی از رسانه» به صورت متنی (بدون عکس اشتباه کتاب گاز) ---
    elif data == "work_resaneh":
        kb = [[InlineKeyboardButton("🔙 بازگشت به مستندها", callback_data="port_docs")]]
        text = (
            "📽️ **مجموعه مستند «روایتی از رسانه» (۱۴۰۳-۱۴۰۴):**\n\n"
            "• مجموعه مستند تحقیقی-پژوهشی ۱۸ قسمتی پیرامون بررسی ویژگی‌های مدیریت رسانه در دوران آقایان محمد هاشمی، شهید علی لاریجانی و عزت‌الله ضرغامی."
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "work_gas_book":
        kb = [[InlineKeyboardButton("🔙 بازگشت به پروژه‌های گاز", callback_data="port_gas")]]
        caption = "📚 **کتاب مرجع «گاز؛ انرژی پاک با نیم قرن تلاش»**\n۱۰۱۸ صفحه، تاریخ شفاهی ۵۰ ساله شرکت ملی گاز ایران."
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAANsarTx9X_9z_IFk7DvWGmtVGkGB0AAAkIQaxslQqhRUjAa4c-6XLwBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "work_esrafi":
        kb = [[InlineKeyboardButton("🔙 بازگشت به انیمیشن‌ها", callback_data="port_anim")]]
        caption = "🎨 **انیمیشن آموزشی «اسرافی و انصافی»**\nمجموعه انیمیشن‌های طنز با محوریت ایمنی گاز شهری."
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAAOXarT7ccFh9OXiCdDZEU8Ke77rJ3gAAl8QaxslQqhRdziJ4NbzhYQBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "award_roshd":
        kb = [[InlineKeyboardButton("🔙 بازگشت به جوایز", callback_data="port_awards")]]
        caption = "🏆 **لوح تقدیر جشنواره بین‌المللی فیلم رشد و جشنواره دفاع مقدس**"
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAAOBarT63lwTbK1i98T2La7qVD3q4gEAAlQQaxslQqhRbvL3WI2R2JkBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "award_tandis":
        kb = [[InlineKeyboardButton("🔙 بازگشت به جوایز", callback_data="port_awards")]]
        caption = "🏆 **تندیس‌ها و لوح‌های سپاس و تقدیر ویژه مدیران ارشد**"
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAAODarT69lI0d1-rQQs-AwTKjAO7WQsAAlUQaxslQqhRpgYVe0-1E6QBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "interviews":
        keyboard = [
            [InlineKeyboardButton("📰 مصاحبه روزنامه اطلاعات (۲۰ مرداد ۱۴۰۵)", callback_data="view_ettelaat_img")],
            [InlineKeyboardButton("📰 مصاحبه هفته‌نامه صدا و سیما (مرداد ۱۴۰۵)", callback_data="view_sedavasima_img")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = (
            "📰 **بخش مصاحبه‌ها و پوشش رسانه‌ای:**\n\n"
            "برای مشاهده تصاویر و جزئیات مصاحبه‌های علی بهادر روی گزینه‌های زیر کلیک کنید:"
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "view_ettelaat_img":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به بخش مصاحبه‌ها", callback_data="interviews")]]
        caption_text = (
            "📰 **مصاحبه با روزنامه اطلاعات (۲۰ مرداد ۱۴۰۵):**\n"
            "عنوان: «سینمای مستند به مدیرانی جسور نیاز دارد» (گفتگو با علی بهادر)\n\n"
            "🔗 [مشاهده آنلاین در سایت اطلاعات](https://www.ettelaat.com/news/161537/%D8%B3%DB%8C%D9%86%D9%85%D8%A7%DB%8C-%D9%85%D8%B3%D8%AA%D9%86%D8%AF-%D8%A8%D9%87-%D9%85%D8%AF%DB%8C%D8%B1%D8%A7%D9%86%DB%8C-%D8%AC%D8%B3%D9%88%D8%B1-%D9%86%DB%8C%D8%A7%D8%B2-%D8%AF%D8%A7%D8%B1%D8%AF)"
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
            [InlineKeyboardButton("🔗 مشاهده آنلاین در سایت", url="https://iribonline.ir/portal/newsview/125403")],
            [InlineKeyboardButton("🔙 بازگشت به بخش مصاحبه‌ها", callback_data="interviews")]
        ]
        caption_text = (
            "📰 **گفت‌وگو با ۲ چهره باسابقه رسانه ملی با تجربه زیسته دفاع مقدس**\n"
            "**«تصویر مقاومت در آیینه رسانه»**\n"
            "**علی بهادر:** روایت یک عمر تصویرگری حماسه\n\n"
            "🔗 [مشاهده آنلاین در سایت](https://iribonline.ir/portal/newsview/125403)"
        )
        await query.message.reply_text(caption_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown", disable_web_page_preview=True)
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "about":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        about_text = (
            "👤 **درباره مدیرعامل:**\n\n"
            "علی بهادر، کارگردان، تهیه‌کننده و نویسنده با بیش از چهار دهه سابقه فعالیت در صدا و سیما و فارغ‌التحصیل کارشناسی کارگردانی از دانشکده صدا و سیما و کارشناسی ارشد ادبیات نمایشی. "
            "در طول این سال‌ها در حوزه‌های سریال‌سازی، تله‌فیلم، مستند و پروژه‌های فرهنگی و صنعتی، هم در داخل کشور و هم در چند کشور منطقه، فعالیت کرده است."
        )
        await query.message.reply_text(about_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "digital_card":
        keyboard = [
            [InlineKeyboardButton("🌐 وب‌سایت رسمی", url="https://alibahador.ir")],
            [InlineKeyboardButton("📸 اینستاگرام مؤسسه", url="https://instagram.com")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = (
            "💳 **کارت ویزیت دیجیتال مؤسسه بهادر فیلم:**\n\n"
            "مدیرعامل: علی بهادر\n"
            "شماره تماس مستقیم: `+989121711063`\n"
            "وب‌سایت: alibahador.ir"
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
    
    # کانورسیشن هندلر ثبت سفارش و پکیج‌ها (با الگوهای دقیق pkg_)
    order_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_order_process, pattern="^start_order$")],
        states={
            PACKAGE_CHOICE: [CallbackQueryHandler(receive_package_choice, pattern="^pkg_")],
            USER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_name)],
            USER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_phone)]
        },
        fallbacks=[CallbackQueryHandler(button_handler, pattern="^back_to_menu$")]
    )
    
    # کانورسیشن هندلر ارسال پیام مستقیم به مدیریت
    contact_admin_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(contact_admin_start, pattern="^contact_admin$")],
        states={
            ADMIN_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_admin_message)]
        },
        fallbacks=[CallbackQueryHandler(button_handler, pattern="^back_to_menu$")]
    )
    
    application.add_handler(order_conv_handler)
    application.add_handler(contact_admin_handler)
    application.add_handler(CallbackQueryHandler(button_handler))

    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    logger.info("Bot is starting polling with fully verified workflows, stats, and bug fixes...")
    application.run_polling()

if __name__ == '__main__':
    main()
