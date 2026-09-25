import os
import logging
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

PROJECT_TYPE, USER_NAME, USER_PHONE = range(3)
ADMIN_MESSAGE = range(1)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bahador Film Bot is running live with complete CV, portfolio photo IDs and new marketing features!"

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

# منوی اصلی بهینه‌شده با دسترسی سریع به درخواست مشاوره، هدیه رایگان و پکیج‌ها در بالاترین سطح
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("💬 درخواست مشاوره رایگان", callback_data="start_order"), InlineKeyboardButton("🎁 هدیه رایگان (چک‌لیست)", callback_data="lead_magnet")],
        [InlineKeyboardButton("🎬 نمونه کارها و رزومه کامل", callback_data="portfolio"), InlineKeyboardButton("⚙️ فرآیند کار ما", callback_data="workflow")],
        [InlineKeyboardButton("📦 پکیج‌های خدمات", callback_data="packages"), InlineKeyboardButton("👤 درباره مدیرعامل", callback_data="about")],
        [InlineKeyboardButton("💳 کارت ویزیت دیجیتال", callback_data="digital_card"), InlineKeyboardButton("💬 ارسال پیام به مدیریت", callback_data="contact_admin")],
        [InlineKeyboardButton("📰 مصاحبه‌ها و رسانه", callback_data="interviews"), InlineKeyboardButton("🔔 خبرنامه آموزشی", callback_data="newsletter_join")],
        [InlineKeyboardButton("❓ پرسش‌های متداول (FAQ)", callback_data="faq")]
    ]
    return InlineKeyboardMarkup(keyboard)

# دستور استارت کوتاه و حرفه‌ای با قابلیت رهگیری منابع ورود (UTM Tracking)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    stats_data["total_visits"] += 1
    stats_data["unique_users"].add(user.id)
    
    # ردیابی منابع ورود (مثلا ?start=story یا ?start=bio)
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

    # --- بخش جدید: فرآیند ۴ مرحله‌ای کار ---
    elif data == "workflow":
        keyboard = [
            [InlineKeyboardButton("💬 درخواست مشاوره رایگان", callback_data="start_order")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = (
            "⚙️ **فرآیند تولید پروژه در مؤسسه بهادر فیلم (۴ مرحله شفاف):**\n\n"
            "۱️⃣ **مشاوره اولیه:** بررسی ایده، نیازسنجی، تعیین اهداف و مخاطب اثر.\n"
            "۲️⃣ **پیش‌تولید:** نگارش فیلم‌نامه، استوری‌برد، انتخاب عوامل، لوکیشن و برنامه‌ریزی.\n"
            "۳️⃣ **تولید:** تصویربرداری حرفه‌ای با تجهیزات مدرن و کادر مجرب.\n"
            "۴️⃣ **تحویل و پس‌تولید:** تدوین دقیق با پریمیر، اصلاح رنگ، صداگذاری و تحویل باکیفیت.\n\n"
            "با این مسیر شفاف، با خیال راحت به پروژه خود جان ببخشید."
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    # --- بخش جدید: پکیج‌های خدمات به‌جای تعرفه خام ---
    elif data == "packages":
        keyboard = [
            [InlineKeyboardButton("💬 انتخاب پکیج و درخواست مشاوره", callback_data="start_order")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = (
            "📦 **پکیج‌های پیشنهادی خدمات:**\n\n"
            "🔹 **پکیج پایه (مناسب کسب‌وکارها):** تولید تیزر معرفی کوتاه، کیفیت استاندارد، مناسب شبکه‌های اجتماعی.\n"
            "🔸 **پکیج حرفه‌ای (پیشنهاد ویژه ⭐):** ساخت مستند سازمانی یا تیزر کامل، فیلم‌برداری تخصصی، اصلاح رنگ و صداگذاری حرفه‌ای.\n"
            "🔹 **پکیج ویژه (فاخر):** تولید سریال، مستندهای بلند تلویزیونی یا پروژه‌های بزرگ سازمانی از صفر تا صد.\n\n"
            "کدام پکیج مد نظر شماست؟ برای شروع کافی است درخواست مشاوره ثبت کنید."
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    # --- بخش جدید: هدیه رایگان (Lead Magnet) ---
    elif data == "lead_magnet":
        keyboard = [
            [InlineKeyboardButton("💬 درخواست مشاوره رایگان", callback_data="start_order")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = (
            "🎁 **هدیه رایگان شما:**\n"
            "«چک‌لیست طلایی آماده‌سازی و سفارش فیلم و تیزر سازمانی»\n\n"
            "این چک‌لیست به شما کمک می‌کند پیش از شروع هر پروژه تولیدی، هزینه‌ها، اهداف و پیام خود را بهینه‌سازی کنید.\n\n"
            "📄 برای مشاهده و دانلود فایل راهنما، به وب‌سایت رسمی ما مراجعه کنید:\n"
            "🌐 alibahador.ir\n\n"
            "⏰ ساعات پاسخگویی واحد مشاوره: شنبه تا چهارشنبه ۹ الی ۱۷."
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown", disable_web_page_preview=True)
        try:
            await query.message.delete()
        except Exception:
            pass

    # --- بخش جدید: خبرنامه آموزشی ماهانه ---
    elif data == "newsletter_join":
        keyboard = [
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = (
            "🔔 **خبرنامه آموزشی و هنری بهادر فیلم**\n\n"
            "با عضویت در این خبرنامه، ماهی ۱ الی ۲ بار نکات ارزشمند تولید فیلم، پشت‌صحنه‌ها و اخبار کارهای جدید مستقیماً برای شما ارسال می‌شود (بدون تبلیغات آزاردهنده).\n\n"
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
            [InlineKeyboardButton("🌐 وب‌سایت رسمی", url="https://alibahador.ir"), InlineKeyboardButton("📸 اینستاگرام", url="https://instagram.com")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        text = (
            "🎬 **بخش نمونه کارها و رزومه جامع علی بهادر:**\n\n"
            "لطفاً حوزه مورد نظر خود را برای مشاهده فهرست کامل آثار همراه با جزئیات و تصاویر انتخاب کنید:"
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass
    
    # --- الف - بخش سریال‌های تلویزیونی، سینمایی و داستانی کوتاه ---
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

    # --- ب - بخش مستند و مستند داستانی ---
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

    # --- پروژه‌های ملی نفت و گاز و کتاب مرجع ---
    elif data == "port_gas":
        keyboard = [
            [InlineKeyboardButton("📚 کتاب مرجع «گاز؛ انرژی پاک...»", callback_data="work_gas_book")],
            [InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = (
            "⛽ **پروژه‌های ملی نفت و گاز و تألیفات:**\n\n"
            "• مجموعه مستند پژوهشی-تاریخی «گاز انرژی پاک با نیم قرن تلاش» در ۶۳ برنامه ۶۰ دقیقه‌ای (مجموعاً ۳۷۰۰ دقیقه).\n"
            "• **کتاب مرجع «گاز انرژی پاک با نیم قرن تلاش»:** ۱۰۱۸ صفحه، چاپ و انتشار در سال ۱۳۹۵. رونمایی رسمی در مراسم پنجاهمین سالگرد تأسیس شرکت ملی گاز ایران با حضور ریاست محترم جمهوری اسلامی ایران.\n"
            "• پوشش تصویری همایش‌ها و پروژه‌ها: افتتاح گازرسانی روستاهای کرمانشاه با حضور وزیر نفت و مدیرعامل شرکت ملی گاز (۱۳۹۹)، پوشش ویدیوکنفرانس پروژه‌ها با ریاست جمهوری، تولید آرم‌استیشن‌های خبری، مستند دیسپچینگ ملی گاز، مستند ایمن‌سازی ایستگاه‌های TBS/DRS، مستند هات‌تپ و آموزش خوردگی خطوط لوله.\n\n"
            "👇 برای مشاهده تصویر کتاب مرجع کلیک کنید:"
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    # --- انیمیشن‌ها ---
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

    # --- جوایز ---
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

    # ================= نمایش آثار و تصاویر با شناسه‌های دقیق و اصلاح‌شده =================
    
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
            await query.message.reply_photo(photo="AgACAgQAAxkBAANuarTyOwkGmkfs6tcNodNBGzujgCwAAkMQaxslQqhRRxnzoph9E4EBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
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

    elif data == "work_resaneh":
        kb = [[InlineKeyboardButton("🔙 بازگشت به مستندها", callback_data="port_docs")]]
        caption = "📽️ **مجموعه مستند «روایتی از رسانه» (۱۴۰۳-۱۴۰۴)**\nبررسی ویژگی‌های مدیریت رسانه در دوران آقایان محمد هاشمی، شهید علی لاریجانی و عزت‌الله ضرغامی."
        try:
            await query.message.reply_photo(photo="AgACAgQAAxkBAANsarTx9X_9z_IFk7DvWGmtVGkGB0AAAkIQaxslQqhRUjAa4c-6XLwBAAMCAAN5AAM9BA", caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
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

    # ================= بخش مصاحبه‌ها و سایر منوها =================

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
            "عنوان: «سینمای مستند به مدیرانی جسور نیاز دارد» (گفتگو با نژلا پیکانیان).\n\n"
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
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به بخش مصاحبه‌ها", callback_data="interviews")]]
        caption_text = (
            "📰 **مصاحبه با هفته‌نامه صدا و سیما (مرداد ۱۴۰۵):**\n"
            "عنوان: «تصویر مقاومت در آیینه رسانه؛ نیم قرن تلاش برای هنر و وطن» (گفتگو با عبدالرحمن شلیبیان)."
        )
        await query.message.reply_text(caption_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "about":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        await query.message.reply_text(
            "👤 **درباره علی بهادر و مؤسسه هنری بهادر فیلم:**\n\n"
            "• **تحصیلات:** کارشناسی ارشد ادبیات نمایشی و لیسانس کارگردانی از دانشکده صداوسیما.\n"
            "• **سوابق اجرایی:** مدیر گروه حماسه و دفاع شبکه یک سیما، سرپرست واحد دوبلاژ شبکه یک، شروع فعالیت حرفه‌ای از زمستان ۱۳۶۰ در واحد خبر همدان به مدت ۶ سال پیش از ورود به دانشکده صداوسیما.\n"
            "• **مدیرعامل:** مؤسسه هنری و سینمایی بهادر فیلم.",
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
            [InlineKeyboardButton("📸 اینستاگرام مؤسسه", url="https://instagram.com")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        await query.message.reply_text(
            "💳 **کارت ویزیت دیجیتال مؤسسه هنری بهادر فیلم:**\n\n"
            "▫️ مدیرعامل: علی بهادر\n"
            "▫️ تخصص: کارگردانی، تهیه‌کنندگی و نویسندگی\n"
            "▫️ وب‌سایت رسمی: alibahador.ir",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "services":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        await query.message.reply_text(
            "📋 **خدمات و تعرفه‌ها:**\n\n"
            "۱. ساخت سریال‌های داستانی و تلویزیونی فاخر\n"
            "۲. تولید مستندهای تلویزیونی، صنعتی و تاریخی\n"
            "۳. ساخت تیزرهای تبلیغاتی و آگهی‌های بازرگانی\n"
            "۴. تولید انیمیشن‌های آموزشی و طنز",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        try:
            await query.message.delete()
        except Exception:
            pass

    elif data == "faq":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        await query.message.reply_text(
            "❓ **پرسش‌های متداول (FAQ):**\n\n"
            "• **چگونه درخواست مشاوره ثبت کنیم؟** از طریق دکمه «درخواست مشاوره رایگان» در منوی اصلی.\n"
            "• **چگونه با مدیریت ارتباط بگیریم؟** از طریق دکمه «ارسال پیام به مدیریت».",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        try:
            await query.message.delete()
        except Exception:
            pass

# --- جریان مکالمه ثبت سفارش / درخواست مشاوره با مقاومت روانی پایین‌تر ---
async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📺 سریال و فیلم داستانی", callback_data="p_series")],
        [InlineKeyboardButton("📽️ ساخت مستند", callback_data="p_documentary")],
        [InlineKeyboardButton("🎬 تیزر تبلیغاتی", callback_data="p_teaser")],
        [InlineKeyboardButton("🎨 انیمیشن", callback_data="p_anim")],
        [InlineKeyboardButton("❌ انصراف", callback_data="back_to_menu")]
    ]
    await query.message.reply_text(
        "💬 **فرم درخواست مشاوره رایگان (مرحله ۱ از ۳):**\n\nلطفاً نوع پروژه مورد نظر خود را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    try:
        await query.message.delete()
    except Exception:
        pass
    return PROJECT_TYPE

async def receive_project_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    mapping = {
        "p_series": "سریال یا فیلم داستانی",
        "p_documentary": "مستند",
        "p_teaser": "تیزر تبلیغاتی",
        "p_anim": "انیمیشن"
    }
    
    if query.data == "back_to_menu":
        await start(update, context)
        return ConversationHandler.END
        
    context.user_data['project_type'] = mapping.get(query.data, "نامشخص")
    
    await query.message.reply_text("✍️ **مرحله ۲ از ۳:**\n\nلطفاً **نام و نام خانوادگی** خود را ارسال کنید:")
    try:
        await query.message.delete()
    except Exception:
        pass
    return USER_NAME

async def receive_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['user_name'] = update.message.text
    await update.message.reply_text(
        "📞 **مرحله ۳ از ۳:**\n\nلطفاً **شماره تماس** خود را ارسال کنید تا همکاران ما در ساعات اداری (۹ الی ۱۷) با شما تماس بگیرند:"
    )
    return USER_PHONE

async def receive_user_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['user_phone'] = update.message.text
    stats_data["orders_count"] += 1
    
    p_type = context.user_data.get('project_type')
    u_name = context.user_data.get('user_name')
    u_phone = context.user_data.get('user_phone')
    
    summary = (
        "✅ **درخواست مشاوره شما با موفقیت ثبت شد!**\n\n"
        f"▫️ نوع پروژه: {p_type}\n"
        f"▫️ نام: {u_name}\n"
        f"▫️ شماره تماس: {u_phone}\n\n"
        "کارشناسان مؤسسه هنری بهادر فیلم به زودی با شما تماس خواهند گرفت."
    )
    
    await update.message.reply_text(summary, parse_mode="Markdown")
    
    # ارسال اطلاع‌رسانی فوری به ادمین
    try:
        admin_notification = (
            f"🔔 **درخواست مشاوره جدید ثبت شد!**\n\n"
            f"👤 نام: {u_name}\n"
            f"📞 تلفن: {u_phone}\n"
            f"🎬 پروژه: {p_type}\n"
            f"🆔 شناسه کاربر: {update.effective_user.id}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_notification, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"خطا در ارسال پیام به ادمین: {e}")

    # بازگشت به منوی اصلی پس از ثبت
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
    await update.message.reply_text("برای بازگشت به منوی اصلی روی دکمه زیر کلیک کنید:", reply_markup=InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END

async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عملیات لغو شد.")
    return ConversationHandler.END

# مدیریت پیام مستقیم به مدیریت
async def contact_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("❌ انصراف", callback_data="back_to_menu")]]
    await query.message.reply_text(
        "💬 **ارسال پیام مستقیم به مدیریت:**\n\nلطفاً پیام، نظر یا پیشنهاد خود را بفرستید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    try:
        await query.message.delete()
    except Exception:
        pass
    return ADMIN_MESSAGE

async def receive_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    user = update.effective_user
    stats_data["messages_count"] += 1

    forward_text = (
        f"📩 **پیام جدید از مخاطب ربات:**\n\n"
        f"👤 نام: {user.full_name} (@{user.username if user.username else 'ندارد'})\n"
        f"🆔 شناسه: {user.id}\n\n"
        f"متن پیام:\n{user_msg}"
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=forward_text, parse_mode="Markdown")
        await update.message.reply_text("✅ پیام شما با موفقیت به مدیریت ارسال شد. به زودی بررسی خواهد شد.")
    except Exception as e:
        logger.error(f"خطا در ارسال پیام ادمین: {e}")
        await update.message.reply_text("❌ متأسفانه در ارسال پیام خطایی رخ داد. لطفاً بعداً تلاش کنید.")
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
    await update.message.reply_text("از ارتباط شما سپاسگزاریم.", reply_markup=InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END

def main():
    app_builder = ApplicationBuilder().token(TOKEN).build()

    # هندلر گفتگو برای ثبت سفارش / مشاوره
    order_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_order, pattern="^start_order$")],
        states={
            PROJECT_TYPE: [CallbackQueryHandler(receive_project_type, pattern="^p_")],
            USER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_name)],
            USER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel_order)]
    )

    # هندلر گفتگو برای ارسال پیام به ادمین
    admin_msg_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(contact_admin_start, pattern="^contact_admin$")],
        states={
            ADMIN_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_admin_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel_order)]
    )

    app_builder.add_handler(CommandHandler("start", start))
    app_builder.add_handler(CommandHandler("stats", stats_command))
    app_builder.add_handler(order_handler)
    app_builder.add_handler(admin_msg_handler)
    app_builder.add_handler(CallbackQueryHandler(button_handler))

    # اجرای سرور Flask در یک ترد جداگانه برای رندر / هاستینگ
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    logger.info("ربات بهادر فیلم با موفقیت اجرا شد و آماده به‌کار است...")
    app_builder.run_polling()

if __name__ == '__main__':
    main()
