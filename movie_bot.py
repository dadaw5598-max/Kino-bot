import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = "8503519871:AAFVIxzEvVjJZlmRr6M-dRf0Gl2xzU7YGt4"

MOVIES = {
    "001": {
        "title": "Birinchi kino",
        "file_id": "BAACAgEAAxkBAAMGaiS-Pls08mdOirvxxVmQeBC5WJEAAwQAAqwNEEdb4RiDHppNJTsE",
        "photo": None,
        "country": "O'zbekiston",
        "language": "O'zbek",
        "year": "2024",
        "genre": "Drama",
    },
}

logging.basicConfig(level=logging.INFO)

def movie_keyboard(code):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📹 Tomosha qilish", callback_data=f"watch_{code}")],
        [InlineKeyboardButton("📤 Ulashish", switch_inline_query=code),
         InlineKeyboardButton("⭐ Baholash", callback_data=f"rate_{code}")],
        [InlineKeyboardButton("🕐 Ko'rmoqchiman", callback_data=f"later_{code}"),
         InlineKeyboardButton("🏠 Asosiy Menyu", callback_data="menu")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎬 Kinolar ro'yxati", callback_data="list")],
        [InlineKeyboardButton("🔍 Qidirish", switch_inline_query="")],
    ])
    await update.message.reply_text(
        "🎬 *Kino Botga xush kelibsiz!*\n\n"
        "Kino kodini yozing yoki quyidagi tugmalardan foydalaning:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def show_movie(update, context, code, movie):
    caption = (
        f"🎬 *{movie['title']}*\n\n"
        f"🌍 Davlati: {movie['country']}\n"
        f"🗣 Tarjima: {movie['language']}\n"
        f"📅 Yili: {movie['year']}\n"
        f"🎭 Janri: {movie['genre']}"
    )
    keyboard = movie_keyboard(code)
    if update.message:
        await update.message.reply_text(caption, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await update.callback_query.message.reply_text(caption, parse_mode="Markdown", reply_markup=keyboard)

async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip().zfill(3)
    movie = MOVIES.get(code)
    if not movie:
        await update.message.reply_text("❌ Kino topilmadi!\n\n📋 Ro'yxat uchun /list yozing.")
        return
    await show_movie(update, context, code, movie)

async def list_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🎬 *Kinolar ro'yxati:*\n\n"
    for code, m in MOVIES.items():
        text += f"🎥 *{m['title']}* — Kod: `{code}`\n"
    await update.message.reply_text(text, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("watch_"):
        code = data.split("_")[1]
        movie = MOVIES.get(code)
        if movie:
            await query.message.reply_text("⏳ Yuklanmoqda...")
            await context.bot.send_video(
                chat_id=query.message.chat_id,
                video=movie["file_id"],
                caption=f"🎬 {movie['title']}",
            )
    elif data.startswith("rate_"):
        await query.message.reply_text("⭐ Baholash funksiyasi tez orada!")
    elif data.startswith("later_"):
        await query.message.reply_text("🕐 Keyinroq ko'rish ro'yxatiga qo'shildi!")
    elif data == "menu":
        await start(query, context)
    elif data == "list":
        text = "🎬 *Kinolar ro'yxati:*\n\n"
        for code, m in MOVIES.items():
            text += f"🎥 *{m['title']}* — Kod: `{code}`\n"
        await query.message.reply_text(text, parse_mode="Markdown")

async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.video:
        file_id = update.message.video.file_id
        await update.message.reply_text(f"File ID:\n`{file_id}`", parse_mode="Markdown")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("list", list_movies))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.VIDEO, get_file_id))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))
app.run_polling()
