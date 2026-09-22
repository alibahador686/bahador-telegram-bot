from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8627933053:AAFXegsURLKgkoQNI4Ov_gf7vT7kTA2V7tU"   # 👈 توکن ربات خودتان را اینجا قرار دهید

# ═══════════════════════════════════════════
# ✏️ اطلاعات تماس
# ═══════════════════════════════════════════
PHONE = "09215680114"             # 👈 شماره تماس واقعی
INSTAGRAM = "alibahador.director"   # ✅ اینستاگرام
WEBSITE = "https://alibahador.ir/"
# ═══════════════════════════════════════════
# 🎥 دسته‌بندی نمونه کارها
# ═══════════════════════════════════════════
CATEGORIES = {
    "series": "📺 سریال‌های تلویزیونی",
    "films": "🎬 فیلم‌های سینمایی و ویدیویی",
    "intl": "🌍 مستندهای بین‌المللی",
    "docs": "📖 مستندهای داخلی",
    "industry": "🏭 مستندهای صنعتی و سازمانی",
    "anim": "🎨 انیمیشن",
}

SAMPLES = {
    # ─── سریال‌های تلویزیونی ───
    "series_1": {
        "cat": "series",
        "title": "بهترین تابستان من",
        "desc": "کارگردانی — ۸ قسمت ۴۵ دقیقه‌ای\nموضوع: طنز دفاع مقدس\n\n🏆 پر مخاطب‌ترین مجموعه تلویزیونی در زمان پخش\n📺 بازپخش چندباره از شبکه یک و جام‌جم ۱، ۲ و ۳",
    },
    "series_2": {
        "cat": "series",
        "title": "شب هزار و یکم",
        "desc": "کارگردانی — ۲۳ قسمت ۴۰ دقیقه‌ای\nموضوع: نقش پزشکان در دفاع مقدس\n\n📺 پخش از شبکه اول سیما",
    },
    "series_3": {
        "cat": "series",
        "title": "عشق سالهای جنگ",
        "desc": "کارگردانی و تهیه‌کنندگی — ۱۳ قسمت ۴۵ دقیقه‌ای\nموضوع: دفاع مقدس\n\n📺 پخش از شبکه سوم سیما",
    },
    "series_4": {
        "cat": "series",
        "title": "برکت",
        "desc": "تهیه‌کنندگی و کارگردانی — ۴ قسمت ۴۵ دقیقه‌ای\nبا حضور بازیگران سینما و تلویزیون\n\n📺 پخش از سیمای مرکز خوزستان",
    },
    "series_5": {
        "cat": "series",
        "title": "مشتری‌مداری",
        "desc": "کارگردانی — ۳۰ قسمت آموزشی\nموضوع: رضایت مشتری در کسب‌وکار و خدمات",
    },

    # ─── فیلم‌های سینمایی و ویدیویی ───
    "film_1": {
        "cat": "films",
        "title": "قدم زدن در بهشت",
        "desc": "کارگردانی — تله‌فیلم با نوآوری خاص\n\n📺 پخش از شبکه‌های ۱، ۲، ۳، شبکه نمایش و سیمای مرکز همدان",
    },
    "film_2": {
        "cat": "films",
        "title": "ارثیه پرماجرا",
        "desc": "تهیه‌کنندگی — طنز اجتماعی\nکارگردان: رسول محمدی\n\n📺 پخش در شبکه خانگی",
    },
    "film_3": {
        "cat": "films",
        "title": "شاهزاده و گدا",
        "desc": "تهیه‌کنندگی — طنز اجتماعی\nکارگردان: رسول محمدی",
    },

    # ─── مستندهای بین‌المللی ───
    "intl_1": {
        "cat": "intl",
        "title": "نوروز در ازبکستان",
        "desc": "تهیه‌کنندگی و کارگردانی\n\n🏆 برنده دو جایزه بهترین تهیه‌کنندگی و بهترین تدوین از جشنواره دفاتر خارج از کشور صداوسیما",
    },
    "intl_2": {
        "cat": "intl",
        "title": "نوروز در تاجیکستان، قزاقستان و ترکمنستان",
        "desc": "تهیه‌کنندگی و کارگردانی\nمجموعه مستندهای نوروز در کشورهای آسیای مرکزی",
    },
    "intl_3": {
        "cat": "intl",
        "title": "بدخشان بام جهان",
        "desc": "تهیه‌کنندگی و کارگردانی — ۴ قسمت ۲۵ دقیقه‌ای\nتولید شده در تاجیکستان",
    },
    "intl_4": {
        "cat": "intl",
        "title": "میهمانی خدا در تاجیکستان",
        "desc": "تهیه‌کنندگی، کارگردانی و تدوین — ۳ قسمت ۲۵ دقیقه‌ای\n\n🏆 برنده جایزه بهترین تدوین از جشنواره دفاتر خارج از کشور صداوسیما",
    },
    "intl_5": {
        "cat": "intl",
        "title": "ایرانشناسان",
        "desc": "تهیه‌کنندگی و کارگردانی\n• در تاجیکستان — ۱۳ قسمت\n• در ازبکستان — ۱۰ قسمت",
    },

    # ─── مستندهای داخلی ───
    "doc_1": {
        "cat": "docs",
        "title": "زندگی",
        "desc": "نویسندگی و کارگردانی\n\n🏆 برنده سه جایزه از جشنواره فیلم دفاع مقدس، جشنواره بین‌المللی رشد و جشنواره فیلم کوتاه همدان",
    },
    "doc_2": {
        "cat": "docs",
        "title": "زنبورداری در ایران",
        "desc": "تهیه‌کنندگی و کارگردانی\n\n🏆 برنده جایزه ویژه از جشنواره سوره",
    },
    "doc_3": {
        "cat": "docs",
        "title": "عطر میعاد",
        "desc": "تهیه‌کنندگی و کارگردانی — ۷ قسمت\nموضوع: حج\n\n📺 پخش از شبکه اول سیما",
    },
    "doc_4": {
        "cat": "docs",
        "title": "نخل‌های صبور",
        "desc": "کارگردانی و تدوین — ۳۰ قسمت ۳۰ دقیقه‌ای\n\n📺 پخش از شبکه تهران",
    },
    "doc_5": {
        "cat": "docs",
        "title": "ولی نعمتان انقلاب",
        "desc": "نویسندگی و کارگردانی — ۱۵ قسمت ۳۰ دقیقه‌ای",
    },

    # ─── مستندهای صنعتی و سازمانی ───
    "ind_1": {
        "cat": "industry",
        "title": "نیم قرن تلاش و تجربه",
        "desc": "تهیه‌کنندگی و کارگردانی — ۳ قسمت\nنگاهی به تاریخ ۵۰ ساله گاز در ایران",
    },
    "ind_2": {
        "cat": "industry",
        "title": "گاز؛ انرژی پاک با نیم قرن تلاش",
        "desc": "تهیه‌کنندگی و کارگردانی\nمستند پژوهشی، تحقیقی و تاریخی\n\n📺 ۶۳ برنامه ۶۰ دقیقه‌ای — مجموعاً ۳۷۰۰ دقیقه",
    },
    "ind_3": {
        "cat": "industry",
        "title": "📚 کتاب مرجع «گاز انرژی پاک با نیم قرن تلاش»",
        "desc": "تهیه و تدوین — چاپ و انتشار سال ۱۳۹۵\n\n🏆 رونمایی در مراسم پنجاهمین سال تأسیس\nشرکت ملی گاز ایران با حضور\nریاست محترم جمهوری اسلامی ایران",
    },
    "ind_4": {
        "cat": "industry",
        "title": "روایت خدمت",
        "desc": "مستند ۳ قسمتی — گازرسانی در مناطق صعب‌العبور غرب کشور (۱۴۰۲)",
    },
    "ind_5": {
        "cat": "industry",
        "title": "تلاش بی‌پایان",
        "desc": "مستند ۱۰ قسمتی — تعمیرات اساسی در صنعت گاز کشور (۱۴۰۴)",
    },
    "ind_6": {
        "cat": "industry",
        "title": "روایتی از رسانه",
        "desc": "مستند تحقیقی و پژوهشی — ۱۸ قسمتی\nمدیریت رسانه ملی در دوره‌های مختلف (۱۴۰۳–۱۴۰۴)",
    },

    # ─── انیمیشن ───
    "anim_1": {
        "cat": "anim",
        "title": "اسرافی و انصافی",
        "desc": "تهیه‌کنندگی و کارگردانی — ۳ فصل ۱۰ قسمتی\nانیمیشن طنز-موزیکال",
    },
}

ABOUT = (
    "👤 علی بهادر\n\n"
    "🎓 لیسانس کارگردانی از دانشکده صداوسیما\n"
    "🎓 فوق‌لیسانس ادبیات نمایشی\n\n"
    "🎬 بیش از سه دهه فعالیت در صداوسیما\n"
    "در عرصه کارگردانی، تهیه‌کنندگی،\n"
    "تدوین و نویسندگی\n\n"
    "🏆 آثار متعدد برنده جایزه از جشنواره‌های\n"
    "ملی و بین‌المللی\n\n"
    "🌍 تولید مستند در تاجیکستان، ازبکستان،\n"
    "قزاقستان و ترکمنستان"
)

WELCOME = (
    "🎬 بهادر فیلم خوش اومدید!\n\n"
    "استودیوی علی بهادر — کارگردان و تهیه‌کننده\n"
    "با بیش از سه دهه تجربه در صداوسیما\n\n"
    "🎬 ساخت مستند، تیزر، آگهی و\n"
    "تولید محتوای اینستاگرام\n\n"
    "از منوی زیر انتخاب کنید 👇"
)


def main_menu():
    keyboard = [
        [InlineKeyboardButton("🎥 نمونه کارها", callback_data="samples")],
        [InlineKeyboardButton("👤 درباره علی بهادر", callback_data="about")],
        [InlineKeyboardButton("📋 خدمات و تعرفه", callback_data="services")],
        [InlineKeyboardButton("📝 ثبت سفارش", callback_data="order")],
        [InlineKeyboardButton("☎️ تماس با ما", callback_data="contact")],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_menu():
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منو", callback_data="menu")]]
    return InlineKeyboardMarkup(keyboard)


def samples_menu():
    rows = []
    for key, label in CATEGORIES.items():
        rows.append([InlineKeyboardButton(label, callback_data=f"cat_{key}")])
    rows.append([InlineKeyboardButton("🔙 بازگشت به منو", callback_data="menu")])
    return InlineKeyboardMarkup(rows)


def category_menu(cat):
    rows = []
    for key, s in SAMPLES.items():
        if s["cat"] == cat:
            rows.append([InlineKeyboardButton(f"🎬 {s['title']}", callback_data=f"sample_{key}")])
    rows.append([InlineKeyboardButton("🔙 بازگشت به نمونه کارها", callback_data="samples")])
    return InlineKeyboardMarkup(rows)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME, reply_markup=main_menu())


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "samples":
        await query.edit_message_text(
            "🎥 نمونه کارهای علی بهادر\n\nیک دسته را انتخاب کنید 👇",
            reply_markup=samples_menu(),
        )
    elif data.startswith("cat_"):
        cat = data.replace("cat_", "")
        label = CATEGORIES.get(cat, "")
        await query.edit_message_text(
            f"{label}\n\nیکی از آثار را انتخاب کنید 👇",
            reply_markup=category_menu(cat),
        )
    elif data.startswith("sample_"):
        key = data.replace("sample_", "")
        s = SAMPLES.get(key)
        if s:
            await query.edit_message_text(
                f"🎬 {s['title']}\n\n{s['desc']}\n\n"
                "━━━━━━━━━━━━━━\n"
                "برای مشاهده اثر یا مشاوره رایگان،\n"
                "از ☎️ تماس با ما استفاده کنید",
                reply_markup=back_menu(),
            )
    elif data == "about":
        await query.edit_message_text(ABOUT, reply_markup=back_menu())
    elif data == "services":
        await query.edit_message_text(
            "📋 خدمات ما:\n\n"
            "• ساخت مستند\n• تیزر\n• آگهی\n• تولید محتوای اینستاگرام\n\n"
            "(قیمت‌ها به‌زودی)",
            reply_markup=back_menu(),
        )
    elif data == "order":
        await query.edit_message_text(
            "📝 ثبت سفارش:\n\n(فرم سفارش به‌زودی)",
            reply_markup=back_menu(),
        )
    elif data == "contact":
        await query.edit_message_text(
            "☎️ تماس با ما:\n\n"
            f"📞 شماره تماس: {PHONE}\n"
            f"📸 اینستاگرام: @{INSTAGRAM}\n"
            f"🌐 وب‌سایت: {WEBSITE}\n\n"
            "برای مشاوره رایگان، پیام بدید!",
            reply_markup=back_menu(),
        )
    elif data == "menu":
        await query.edit_message_text(WELCOME, reply_markup=main_menu())


def main():
    # ساخت اپلیکیشن به صورت استاندارد بدون نیاز به پروکسی محلی
    app = (
        Application.builder()
        .token(TOKEN)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    print("Bot is running! Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()