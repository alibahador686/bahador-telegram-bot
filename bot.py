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

# توکن ربات (خوانده شده از متغیرهای محیطی رندر با پشتیبانی از مقدار پیش‌فرض ایمن)
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
        [InlineKeyboardButton("🎬 نمونه کارها", callback_data="portfolio"), InlineKeyboardButton("👤 درباره مؤسسه", callback_data="about")],
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
        "🎬 **مؤسسه هنری بهادر فیلم خوش آمدید!**\n\n"
        "مدیریت: علی بهادر – کارگردان و تهیه‌کننده با بیش از سه دهه تجربه در صداوسیما\n\n"
        "🎬 ساخت مستند، تیزر، آگهی و تولید محتوای اینستاگرام\n\n"
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
        f"📊 **آمار ربات مؤسسه بهادر فیلم:**\n\n"
        f"🔹 کل بازدیدها: {stats_data['total_visits']}\n"
        f"🔹 کاربران یکتا: {len(stats_data['unique_users'])}\n"
        f"🔹 سفارش‌های ثبت شده: {stats_data['orders_count']}\n"
        f"🔹 پیام‌های دریافتی مدیریت: {stats_data['messages_count']}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# مدیریت کلیک دکمه‌ها
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
            [InlineKeyboardButton("🌐 مشاهده نمونه کارها در سایت", url="https://alibahador.ir")],
            [InlineKeyboardButton("📸 مشاهده صفحه اینستاگرام", url="https://instagram.com")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]
        ]
        await query.message.edit_text(
            "🎬 **بخش نمونه کارها و تیزرها:**\n\n"
            "برای مشاهده کامل مستندها، تیزرها و پروژه‌های تلویزیونی می‌توانید به وب‌سایت رسمی یا صفحه اینستاگرام مؤسسه مراجعه کنید:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    elif data == "about":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        await query.message.edit_text(
            "👤 **درباره علی بهادر و مؤسسه هنری بهادر فیلم:**\n\n"
            "کارگردان، تهیه‌کننده و فیلم‌نامه‌نویس با سابقه فعالیت در گروه حماسه و دفاع شبکه یک سیما، مدیریت واحد دوبلاژ و ساخت آثار ماندگاری چون *بهترین تابستان من*، *عشق سال‌های جنگ* و *شب هزار و یکم*.",
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
            "▫️ حوزه فعالیت: کارگردانی، تهیه‌کنندگی، ساخت مستند و تیزرهای تبلیغاتی\n"
            "▫️ وب‌سایت: alibahador.ir",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    elif data == "services":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        await query.message.edit_text(
            "📋 **خدمات و تعرفه‌ها:**\n\n"
            "۱. ساخت مستندهای صنعتی و تلویزیونی\n"
            "۲. تولید تیزرهای تبلیغاتی و آگهی‌های بازرگانی\n"
            "۳. تولید محتوای تخصصی اینستاگرام و یوتیوب\n\n"
            "برای استعلام تعرفه دقیق، از بخش «ثبت سفارش» اقدام فرمایید.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    elif data == "faq":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_menu")]]
        await query.message.edit_text(
            "❓ **پرسش‌های متداول (FAQ):**\n\n"
            "• **چگونه پروژه ثبت کنیم؟** از طریق دکمه ثبت سفارش در منو.\n"
            "• **زمان تحویل پروژه‌ها چقدر است؟** بسته به نوع پروژه (مستند یا تیزر) متغیر است.\n"
            "• **چگونه با مدیریت ارتباط بگیریم؟** از طریق دکمه ارسال پیام به مدیریت.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

# فرآیند ثبت سفارش مرحله به مرحله
async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🎬 مستند", callback_data="p_documentary")],
        [InlineKeyboardButton("📺 تیزر تبلیغاتی", callback_data="p_teaser")],
        [InlineKeyboardButton("📱 تولید محتوای اینستاگرام", callback_data="p_insta")],
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
        "p_documentary": "مستند",
        "p_teaser": "تیزر تبلیغاتی",
        "p_insta": "تولید محتوای اینستاگرام"
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
    # اجرای وب‌سایت فلاسک در یک ترد جداگانه
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

    # ساخت اپلیکیشن تلگرام
    application = ApplicationBuilder().token(TOKEN).build()

    # هندلر مکالمه ثبت سفارش
    order_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_order, pattern="^start_order$")],
        states={
            PROJECT_TYPE: [CallbackQueryHandler(receive_project_type)],
            USER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_name)],
            USER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_phone)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # هندلر ارسال پیام به مدیریت
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

    print("Bot is running with interactive features!")
    application.run_polling()

if __name__ == '__main__':
    main()
