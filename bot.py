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

# توکن ربات (خوانده شده از متغیرهای محیطی رندر)
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8627933053:AAG1-UaJK5DkKpa330nvd3WmBepC8psEVg0")

# متغیرهای ذخیره آمار ساده
stats_data = {
    "total_visits": 0,
    "unique_users": set(),
    "orders_count": 0,
    "messages_count": 0
}

# مراحل ثبت سفارش مکالمه‌ای
PROJECT_TYPE, USER_NAME, USER_PHONE = range(3)
# مراحل ارسال پیام به مدیریت
ADMIN_MESSAGE = range(1)

# راه‌اندازی سرور فلاسک برای پایداری روی رندر (Web Service)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bahador Film Bot is running live!"

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

# منوی اصلی ربات
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🎬 نمونه کارها و رزومه", callback_data="portfolio"), InlineKeyboardButton("👤 درباره مدیرعامل", callback_data="about")],
        [InlineKeyboardButton("💳 کارت ویزیت دیجیتال", callback_data="digital_card"), InlineKeyboardButton("💬 ارسال پیام به مدیریت", callback_data="contact_admin")],
        [InlineKeyboardButton("📋 خدمات و تعرفه", callback_data="services"), InlineKeyboardButton("📝 ثبت سفارش", callback_data="start_order")],
        [InlineKeyboardButton("❓ پرسش‌های متداول (FAQ)", callback_data="faq")]
    ]
    return InlineKeyboardMarkup(keyboard)

# دستور شروع /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    stats_data["total_visits"] += 1
    stats_data["unique_users"].add(user.id)
    
    welcome_text = (
        "🎬 **به مؤسسه هنری بهادر فیلم خوش آمدید!**\n\n"
        "مدیریت: علی بهادر – کارگردان، تهیه‌کننده و نویسنده (دارای کارشناسی ارشد ادبیات نمایشی و لیسانس کارگردانی از دانشکده صداوسیما با بیش از چهار دهه تجربه حرفه‌ای)\n\n"
        "🎬 ساخت سریال، مستندهای فاخر تلویزیونی، تیزر، آگهی و انیمیشن\n\n"
        "👇 از منوی زیر انتخاب کنید:"
    )
    
    if update.callback_query:
        await update.callback_query.message.reply_text(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")
        await update.callback_query.answer()
    else:
        await update.message.reply_text(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")

# دستور نمایش آمار برای ادمین /stats
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"📊 **آمار ربات مؤسسه هنری بهادر فیلم:**\n\n"
        f"🔹 کل بازدیدها: {stats_data['total_visits']}\n"
        f"🔹 کاربران یکتا: {len(stats_data['unique_users'])}\n"
        f"🔹 سفارش‌های ثبت شده: {stats_data['orders_count']}\n"
        f"🔹 پیام‌های دریافتی مدیریت: {stats_data['messages_count']}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# مدیریت کلیک دکمه‌ها و بخش نمونه کارها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_to_menu":
        await query.message.edit_text(
            "🎬 **مؤسسه هنری بهادر فیلم**\n\n👇 از منوی زیر انتخاب کنید:",
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
    elif data == "portfolio":
        keyboard = [
            [InlineKeyboardButton("📺 سریال‌ها و فیلم‌های سینمایی/داستانی", callback_data="port_series")],
            [InlineKeyboardButton("📽️ مستندهای تلویزیونی و بین‌المللی", callback_data="port_docs")],
            [InlineKeyboardButton("⛽ پروژه ملی و کتاب مرجع گاز", callback_data="port_gas")],
            [InlineKeyboardButton("🎨 انیمیشن‌های طنز و موزیکال", callback_data="port_anim")],
            [InlineKeyboardButton("🌐 وب‌سایت رسمی", url="https://alibahador.ir"), InlineKeyboardButton("📸 اینستاگرام", url="https://instagram.com")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        await query.message.edit_text(
            "🎬 **بخش نمونه کارها و کارنامه هنری علی بهادر:**\n\n"
            "لطفاً حوزه مورد نظر خود را برای مشاهده فهرست کامل آثار انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    elif data == "port_series":
        keyboard = [
            [InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = (
            "📺 **سریال‌های تلویزیونی و فیلم‌های داستانی:**\n\n"
            "1️⃣ **سریال بهترین تابستان من (۱۳۷۲):** طنز دفاع مقدس در ۸ قسمت. پرمخاطب‌ترین مجموعه تلویزیونی زمان پخش، تکرار چندین باره از شبکه یک و جام‌جم.\n"
            "*(بازیگران: علی صادقی، علیرضا اسحاقی، سید جواد هاشمی، مهدی صباغی، فاطمه طاهری و...)*\n\n"
            "2️⃣ **سریال عشق سال‌های جنگ (۱۳۷۹):** موضوع دفاع مقدس در ۱۳ قسمت (کارگردانی و تهیه‌کنندگی مشترک).\n"
            "*(بازیگران: فرهاد جم، جعفر دهقان، اندیشه فولادوند، پرستو صالحی، مهدی صبائی، بهمن دان، مجید مشیری، محسن قاضی‌مراد و...)*\n\n"
            "3️⃣ **سریال شب هزار و یکم (۱۳۸۸):** نقش پزشکان در دفاع مقدس در ۲۳ قسمت (پخش از شبکه یک سیما).\n"
            "*(بازیگران: دانیال حکیمی، علیرضا خمسه، مهشید افشارزاده، یوسف مرادیان، فخرالدین صدیق شریف، آرام جعفری، سپیده گلچین و...)*\n\n"
            "4️⃣ **تله‌فیلم قدم زدن در بهشت (۱۳۹۱-۱۳۹۳):** با نوگرایی خاص، پخش از شبکه‌های ۱، ۲، ۳، نمایش و سیمای همدان.\n\n"
            "5️⃣ **فیلم‌های سینمایی ویدیویی:**\n"
            "• *ارثیه پرماجرا* (۹۳) - تهیه‌کننده\n"
            "• *شاهزاده و گدا* (۹۳) - تهیه‌کننده\n\n"
            "6️⃣ **مینی‌سریال برکت (۱۳۹۷)** و سریال آموزشی **مشتری‌مداری (۱۴۰۰)** در ۳۰ قسمت."
        )
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "port_docs":
        keyboard = [
            [InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = (
            "📽️ **مستندهای تلویزیونی و بین‌المللی:**\n\n"
            "• **مستند «زندگی»:** برنده سه جایزه از جشنواره فیلم دفاع مقدس، جشنواره رشد و جشنواره همدان.\n"
            "• **مجموعه مستند «روایتی از رسانه» (۱۴۰۳-۱۴۰۴):** بررسی مدیریت رسانه در دوران آقایان محمد هاشمی، شهید علی لاریجانی و عزت‌الله ضرغامی در ۱۸ قسمت.\n"
            "• **مستند «تلاش بی‌پایان» (۱۴۰۴):** ۱۰ قسمت درباره اورهال و تعمیرات اساسی صنعت گاز.\n"
            "• **مستند «روایت خدمت» (۱۴۰۲):** ۳ قسمت درباره سختی گازرسانی در نقاط صعب‌العبور.\n"
            "• **مستندهای برون‌مرزی تاجیکستان و ازبکستان:** *بدخشان بام جهان*، *نوروز در ازبکستان* (برنده دو جایزه بهترین تهیه‌کنندگی و تدوین)، *میهمانی خدا*، *میر سید علی همدانی* و...\n"
            "• **سایر آثار شاخص:** *قدسیان خاک*، *نخل‌های صبور*، *عطر میعاد* (حج)، *بچه‌های مسجد*، *نسیم کوثر* و..."
        )
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "port_gas":
        keyboard = [
            [InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = (
            "⛽ **پروژه‌های ملی نفت و گاز و کتاب مرجع:**\n\n"
            "📚 **کتاب مرجع «گاز؛ انرژی پاک با نیم قرن تلاش» (۱۳۹۵):**\n"
            "تدوین و نشر اثر پژوهشی ۱۰۰۰ صفحه‌ای (تاریخ ۵۰ ساله گاز در ایران) که در مراسم رسمی با حضور ریاست محترم جمهوری رونمایی شد.\n\n"
            "• **مجموعه مستند پژوهشی ۶۳ برنامه‌ای (۳۷۰۰ دقیقه):** گاز انرژی پاک با نیم قرن تلاش.\n"
            "• **مجموعه «گام‌های بزرگ همدلی»:** پوشش تصویری و مستندسازی گازرسانی به شهرها و روستاهای کشور (۱۳۹۵).\n"
            "• **پوشش تصویری همایش‌ها و افتتاح کلان:** ضبط با واحد سیار، ۱۲ دوربین پرتابل و کرین در همایش‌های سراسری با حضور وزیر نفت و مقامات عالی‌رتبه.\n"
            "• **مستندهای تخصصی:** *ایمن‌سازی جریان گاز*، *عملیات هات‌تپ*، *مستند خوردگی خطوط لوله* و..."
        )
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "port_anim":
        keyboard = [
            [InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="portfolio")]
        ]
        text = (
            "🎨 **انیمیشن‌های طنز، موزیکال و آموزشی:**\n\n"
            "• **مجموعه انیمیشن «اسرافی و انصافی»:**\n"
            "تهیه‌کنندگی و کارگردانی فصول ۱، ۲ و ۳ (تولید ۱۳۹۷ تا ۱۴۰۰) - انیمیشن طنز و موزیکال با شخصیت ماندگار «انصافی» در مقام مشاور دانا برای خانواده اسرافی در حوزه ایمنی گاز شهری.\n"
            "• **انیمیشن‌های آموزشی راهداری:**\n"
            "تولید دو قسمت انیمیشن آموزشی برای مدیریت راه‌های اداره کل راهداری استان همدان (۱۳۹۹)."
        )
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "about":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        await query.message.edit_text(
            "👤 **درباره علی بهادر و مؤسسه هنری بهادر فیلم:**\n\n"
            "• **تحصیلات:** کارشناسی ارشد ادبیات نمایشی و لیسانس کارگردانی از دانشکده صداوسیما.\n"
            "• **سوابق اجرایی:** مدیر گروه حماسه و دفاع شبکه یک سیما، مدیر واحد دوبلاژ شبکه یک، آغاز فعالیت حرفه‌ای از سال ۱۳۶۰ در واحد خبر همدان (بیش از چهار دهه تجربه).\n"
            "• **مدیرعامل:** مؤسسه هنری و سینمایی بهادر فیلم.\n"
            "سازنده آثار فاخر تلویزیونی، مستندهای ملی و بین‌المللی و مرجع تولیدات رسانه‌ای.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    elif data == "digital_card":
        keyboard = [
            [InlineKeyboardButton("🌐 وب‌سایت رسمی", url="https://alibahador.ir")],
            [InlineKeyboardButton("📸 اینستاگرام مؤسسه", url="https://instagram.com")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        await query.message.edit_text(
            "💳 **کارت ویزیت دیجیتال مؤسسه هنری بهادر فیلم:**\n\n"
            "▫️ مدیرعامل: علی بهادر\n"
            "▫️ تخصص: کارگردانی، تهیه‌کنندگی، نویسندگی و پژوهش رسانه\n"
            "▫️ وب‌سایت: alibahador.ir",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    elif data == "services":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        await query.message.edit_text(
            "📋 **خدمات و تعرفه‌ها:**\n\n"
            "۱. ساخت سریال‌های داستانی، تلویزیونی و فیلم‌های سینمایی\n"
            "۲. تولید مستندهای فاخر صنعتی، تاریخی و تلویزیونی\n"
            "۳. ساخت تیزرهای تبلیغاتی، صنعتی و آگهی‌های بازرگانی\n"
            "۴. تولید انیمیشن‌های موزیکال و آموزشی\n\n"
            "برای استعلام تعرفه دقیق، از بخش «ثبت سفارش» اقدام فرمایید.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    elif data == "faq":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        await query.message.edit_text(
            "❓ **پرسش‌های متداول (FAQ):**\n\n"
            "• **چگونه پروژه ثبت کنیم؟** از طریق دکمه ثبت سفارش در منو.\n"
            "• **زمان تحویل پروژه‌ها چقدر است؟** بسته به نوع پروژه و حجم کار متغیر است.\n"
            "• **چگونه با مدیریت ارتباط بگیریم؟** از طریق دکمه ارسال پیام به مدیریت.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

# فرآیند ثبت سفارش مرحله به مرحله
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
    await query.message.edit_text(
        "📝 **ثبت سفارش جدید - مرحله ۱ از ۳:**\n\nلطفاً نوع پروژه مورد نظر خود را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
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
    
    await query.message.edit_text(
        "✍️ **مرحله ۲ از ۳:**\n\nلطفاً **نام و نام خانوادگی** خود را ارسال کنید:"
    )
    return USER_NAME

async def receive_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['user_name'] = update.message.text
    await update.message.reply_text(
        "📞 **مرحله ۳ از ۳:**\n\nلطفاً **شماره تماس** خود را ارسال کنید تا همکاران ما با شما تماس بگیرند:"
    )
    return USER_PHONE

async def receive_user_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['user_phone'] = update.message.text
    stats_data["orders_count"] += 1
    
    p_type = context.user_data.get('project_type')
    u_name = context.user_data.get('user_name')
    u_phone = context.user_data.get('user_phone')
    
    summary = (
        "✅ **سفارش شما با موفقیت ثبت شد!**\n\n"
        f"▫️ نوع پروژه: {p_type}\n"
        f"▫️ نام: {u_name}\n"
        f"▫️ شماره تماس: {u_phone}\n\n"
        "کارشناسان مؤسسه هنری بهادر فیلم به زودی با شما تماس خواهند گرفت."
    )
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
    await update.message.reply_text(summary, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return ConversationHandler.END

# فرآیند ارسال پیام به مدیریت
async def contact_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("❌ انصراف", callback_data="back_to_menu")]]
    await query.message.edit_text(
        "💬 **ارسال پیام به مدیریت:**\n\nلطفاً پیام، نظر یا درخواست خود را بنویسید تا برای مدیریت ارسال شود:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ADMIN_MESSAGE

async def receive_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats_data["messages_count"] += 1
    user_msg = update.message.text
    user = update.effective_user
    
    logger.info(f"New message from {user.full_name} ({user.id}): {user_msg}")
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
    await update.message.reply_text(
        "✅ پیام شما با موفقیت به مدیریت مؤسسه هنری بهادر فیلم ارسال شد.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عملیات لغو شد.", reply_markup=get_main_menu())
    return ConversationHandler.END

def main():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

    application = ApplicationBuilder().token(TOKEN).build()

    order_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_order, pattern="^start_order$")],
        states={
            PROJECT_TYPE: [CallbackQueryHandler(receive_project_type)],
            USER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_name)],
            USER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_phone)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    admin_msg_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(contact_admin_start, pattern="^contact_admin$")],
        states={
            ADMIN_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_admin_message)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(order_handler)
    application.add_handler(admin_msg_handler)
    application.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running with four decades of experience!")
    application.run_polling()

if __name__ == '__main__':
    main()
