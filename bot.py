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
    return "Bahador Film Bot is running live with complete guide content and fixed admin messaging!"

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

# منوی اصلی بهینه‌شده (شامل دکمه ثبت سفارش و مشاوره در صدر منو)
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
        f"📊 **آمار ربات مؤسسه هنری بهادر فیلم:**\n\n"
        f"🔹 کل بازدیدها: {stats_data['total_visits']}\n"
        f"🔹 کاربران یکتا: {len(stats_data['unique_users'])}\n"
        f"🔹 مشاوره‌ها/سفارش‌های ثبت شده: {stats_data['orders_count']}\n"
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
        "لطفاً پکیج یا نوع درخواست خود را انتخاب کنید:"
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
            [InlineKeyboardButton("📺 سریال‌ها و آثار نمایشی", callback_data="port_series")],
            [InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = (
            "📺 **فهرست سریال‌ها و فیلم‌های داستانی:**\n\n"
            "۱- ارثیه پرماجرا (۱۳۹۳)\n"
            "۲- شاهزاده و گدا (۱۳۹۳)\n"
            "۳- قدم زدن در بهشت (۱۳۹۱)\n"
            "۴- شب هزار و یکم (۱۳۸۸ - شبکه اول سیما)\n"
            "۵- عشق سال‌های جنگ (۱۳۷۹ - شبکه سوم سیما)\n"
            "۶- بهترین تابستان من (۱۳۷۲ - پرمخاطب‌ترین مجموعه)\n"
            "۷- برکت (۱۳۹۷)\n"
            "۸- مشتری‌مداری (۱۴۰۰)\n"
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "port_docs":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]]
        text = "📽️ مستند «زندگی»، مستندهای برون‌مرزی نوروز در آسیای میانه، مجموعه «روایتی از رسانه» و ده‌ها اثر مستند فاخر دیگر."
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "port_gas":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]]
        text = "⛽ مجموعه مستند پژوهشی «گاز انرژی پاک با نیم قرن تلاش» و کتاب مرجع ۱۰۱۸ صفحه‌ای چاپ ۱۳۹۵."
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "port_anim":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]]
        text = "🎨 انیمیشن طنز و آموزشی «اسرافی و انصافی» با محوریت ایمنی گاز شهری."
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "port_awards":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]]
        text = "🏆 جوایز جشنواره بین‌المللی فیلم رشد، جشنواره دفاع مقدس و لوح‌های تقدیر مدیران ارشد."
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "interviews":
        keyboard = [
            [InlineKeyboardButton("📰 روزنامه اطلاعات (۲۰ مرداد ۱۴۰۵)", url="https://www.ettelaat.com/news/161537/%D8%B3%DB%8C%D9%86%D9%85%D8%A7%DB%8C-%D9%85%D8%B3%D8%AA%D9%86%D8%AF-%D8%A8%D9%87-%D9%85%D8%AF%DB%8C%D8%B1%D8%A7%D9%86%DB%8C-%D8%AC%D8%B3%D9%88%D8%B1-%D9%86%DB%8C%D8%A7%D8%B2-%D8%AF%D8%A7%D8%B1%D8%AF")],
            [InlineKeyboardButton("📰 هفته‌نامه صدا و سیما", url="https://iribonline.ir/portal/newsview/125403")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = "📰 **مصاحبه‌ها و پوشش رسانه‌ای علی بهادر:**"
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "about":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        await query.message.reply_text(
            "👤 **درباره علی بهادر:**\n\n"
            "• کارشناسی ارشد ادبیات نمایشی و کارگردانی از دانشکده صداوسیما.\n"
            "• مدیر گروه حماسه و دفاع شبکه یک سیما، سرپرست واحد دوبلاژ شبکه یک.\n"
            "• مدیرعامل مؤسسه هنری و سینمایی بهادر فیلم.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "digital_card":
        keyboard = [
            [InlineKeyboardButton("🌐 وب‌سایت رسمی", url="https://alibahador.ir")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = "💳 **کارت ویزیت دیجیتال:**\nمدیرعامل: علی بهادر\nشماره تماس: `+989121711063`\nوب‌سایت: alibahador.ir"
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # کانورسیشن هندلر ثبت سفارش و پکیج‌ها
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

    logger.info("Bot is starting polling with updated order workflow...")
    application.run_polling()

if __name__ == '__main__':
    main()
