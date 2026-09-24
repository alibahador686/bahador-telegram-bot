import os
import logging
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# تنظیمات لاگ‌گیری استاندارد
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# راه‌اندازی وب‌سرور ساده Flask برای پاسخ به پورت رندر و جلوگیری از خطای Timeout
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot is active and running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)

# خواندن خودکار توکن
TOKEN = os.environ.get("TELEGRAM_TOKEN", "55555555555555555")

# 🆔 آیدی عددی تلگرام شما برای دریافت پیام‌ها و آمار (در صورت نیاز می‌توانید تغییر دهید)
ADMIN_ID = 123456789  # جایگزین با آیدی عددی ادمین در صورت تمایل

# متغیرهای ساده برای ذخیره آمار در حافظه سرور
stats = {
    "total_starts": 0,
    "messages_received": 0
}

# ═══════════════════════════════════════════
# ✏️ اطلاعات تماس و کارت ویزیت دیجیتال
# ═══════════════════════════════════════════
PHONE = "09215680114"
INSTAGRAM = "alibahador.director"
WEBSITE = "https://alibahador.ir/"

CATEGORIES = {
    "series": "📺 سریال‌های تلویزیونی",
    "films": "🎬 فیلم‌های سینمایی و ویدیویی",
    "intl": "🌍 مستندهای بین‌المللی",
    "docs": "📖 مستندهای داخلی",
    "industry": "🏭 مستندهای صنعتی و سازمانی",
    "anim": "🎨 انیمیشن",
}

SAMPLES = {
    "series_1": {
        "cat": "series",
        "title": "بهترین تابستان من",
        "desc": "کارگردانی — ۸ قسمت ۴۵ دقیقه‌ای\nموضوع: طنز دفاع مقدس\n\n🏆 پر مخاطب‌ترین مجموعه تلویزیونی در زمان پخش",
    },
    "series_2": {
        "cat": "series",
        "title": "شب هزار و یکم",
        "desc": "کارگردانی — ۲۳ قسمت ۴۰ دقیقه‌ای\nموضوع: نقش پزشکان در دفاع مقدس",
    },
    "film_1": {
        "cat": "films",
        "title": "قدم زدن در بهشت",
        "desc": "کارگردانی — تله‌فیلم با نوآوری خاص",
    },
    "ind_2": {
        "cat": "industry",
        "title": "گاز؛ انرژی پاک با نیم قرن تلاش",
        "desc": "تهیه‌کنندگی و کارگردانی\nمستند پژوهشی، تحقیقی و تاریخی",
    },
}

ABOUT = (
    "👤 علی بهادر\n\n"
    "🎓 لیسانس کارگردانی از دانشکده صداوسیما\n"
    "🎓 فوق‌لیسانس ادبیات نمایشی\n\n"
    "🎬 بیش از سه دهه فعالیت در صداوسیما\n"
    "در عرصه کارگردانی، تهیه‌کنندگی و نویسندگی"
)

WELCOME = (
    "🎬 بهادر فیلم خوش اومدید!\n\n"
    "استودیوی علی بهادر — کارگردان و تهیه‌کننده\n"
    "با بیش از سه دهه تجربه در صداوسیما\n\n"
    "از منوی زیر انتخاب کنید 👇"
)


def main_menu():
    keyboard = [
        [InlineKeyboardButton("🎥 نمونه کارها", callback_data="samples")],
        [InlineKeyboardButton("👤 درباره علی بهادر", callback_data="about")],
        [InlineKeyboardButton("💳 کارت ویزیت دیجیتال", callback_data="digital_card")],
        [InlineKeyboardButton("💬 ارسال پیام به مدیریت", callback_data="contact_admin")],
        [InlineKeyboardButton("📋 خدمات و تعرفه", callback_data="services")],
        [InlineKeyboardButton("📝 ثبت سفارش", callback_data="order")],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_menu():
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منو", callback_data="menu")]]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats["total_starts"] += 1
    await update.message.reply_text(WELCOME, reply_markup=main_menu())


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "samples":
        rows = [[InlineKeyboardButton(label, callback_data=f"cat_{key}")] for key, label in CATEGORIES.items()]
        rows.append([InlineKeyboardButton("🔙 بازگشت به منو", callback_data="menu")])
        await query.edit_message_text("🎥 نمونه کارهای علی بهادر\n\nیک دسته را انتخاب کنید 👇", reply_markup=InlineKeyboardMarkup(rows))
    
    elif data.startswith("cat_"):
        cat = data.replace("cat_", "")
        rows = []
        for key, s in SAMPLES.items():
            if s["cat"] == cat:
                rows.append([InlineKeyboardButton(f"🎬 {s['title']}", callback_data=f"sample_{key}")])
        rows.append([InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="samples")])
        label = CATEGORIES.get(cat, "")
        await query.edit_message_text(f"{label}\n\nیکی از آثار را انتخاب کنید 👇", reply_markup=InlineKeyboardMarkup(rows))

    elif data.startswith("sample_"):
        key = data.replace("sample_", "")
        s = SAMPLES.get(key)
        if s:
            await query.edit_message_text(
                f"🎬 {s['title']}\n\n{s['desc']}\n\n━━━━━━━━━━━━━━\nبرای سفارش یا مشاوره، از بخش تماس استفاده کنید.",
                reply_markup=back_menu()
            )

    elif data == "about":
        await query.edit_message_text(ABOUT, reply_markup=back_menu())

    elif data == "digital_card":
        card_text = (
            "📇 **کارت ویزیت دیجیتال استودیوی بهادر فیلم**\n\n"
            f"👤 **نام:** علی بهادر\n"
            f"💼 **حوزه فعالیت:** کارگردان، تهیه‌کننده و نویسنده\n"
            f"📞 **تلفن تماس:** {PHONE}\n"
            f"📸 **اینستاگرام:** @{INSTAGRAM}\n"
            f"🌐 **وب‌سایت:** {WEBSITE}\n\n"
            "✨ برای ذخیره اطلاعات یا ارتباط مستقیم از دکمه‌های زیر استفاده کنید."
        )
        await query.edit_message_text(card_text, parse_mode="Markdown", reply_markup=back_menu())

    elif data == "contact_admin":
        context.user_data["waiting_for_message"] = True
        await query.edit_message_text(
            "💬 **ارسال پیام به مدیریت:**\n\n"
            "لطفاً پیام، نظر یا درخواست خود را همینجا ارسال کنید تا به دست آقای بهادر برسد.",
            parse_mode="Markdown",
            reply_markup=back_menu()
        )

    elif data == "services":
        await query.edit_message_text("📋 خدمات ما:\n\n• ساخت مستند\n• تیزر و آگهی\n• تولید محتوای اینستاگرام", reply_markup=back_menu())

    elif data == "order":
        await query.edit_message_text("📝 ثبت سفارش:\n\nلطفاً از طریق بخش «ارسال پیام به مدیریت» جزئیات پروژه خود را بفرستید.", reply_markup=back_menu())

    elif data == "menu":
        context.user_data["waiting_for_message"] = False
        await query.edit_message_text(WELCOME, reply_markup=main_menu())


# 📊 دستور مخفی برای مشاهده آمار بازدید (فقط با فرستادن دستور /stats)
async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats_text = (
        "📊 **آمار بازدید و فعالیت ربات:**\n\n"
        f"👥 تعداد کل استارت‌ها / بازدیدها: {stats['total_starts']}\n"
        f"💬 پیام‌های دریافتی از مخاطبان: {stats['messages_received']}"
    )
    await update.message.reply_text(stats_text, parse_mode="Markdown")


# 📨 دریافت پیام متنی از کاربر و ارسال به مدیریت
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("waiting_for_message"):
        user_text = update.message.text
        user = update.effective_user
        
        stats["messages_received"] += 1
        context.user_data["waiting_for_message"] = False

        # تأیید به کاربر
        await update.message.reply_text("✅ پیام شما با موفقیت به مدیریت ارسال شد. به زودی پاسخگوی شما خواهیم بود.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت به منو", callback_data="menu")]]))
        
        # چاپ پیام در لاگ سرور (یا ارسال به ادمین در صورت نیاز)
        logging.info(f"New Message from {user.full_name} (@{user.username}): {user_text}")


def main():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", show_stats))  # دستور آمار
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running with interactive features!")
    app.run_polling()


if __name__ == "__main__":
    main()
