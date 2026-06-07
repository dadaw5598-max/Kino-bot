import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8503519871:AAFVIxzEvVjJZlmRr6M-dRf0Gl2xzU7YGt4"

MOVIES = {
    "001": {"title": "Birinchi kino", "file_id": "BAACAgEAAxkBAAMGaiS-Pls08mdOirvxxVmQeBC5WJEAAwQAAqwNEEdb4RiDHppNJTsE"},
}

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Kino kodini yozing (masalan: 001)")

async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.video:
        file_id = update.message.video.file_id
        await update.message.reply_text(f"File ID:\n`{file_id}`", parse_mode="Markdown")

async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip().zfill(3)
    movie = MOVIES.get(code)
    if not movie:
        await update.message.reply_text("Kino topilmadi. /list yozing.")
        return
    await update.message.reply_text("Yuklanmoqda...")
    await context.bot.send_video(chat_id=update.effective_chat.id, video=movie["file_id"], caption=movie["title"])

async def list_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Kinolar:\n"
    for code, m in MOVIES.items():
        text += f"{code} - {m['title']}\n"
    await update.message.reply_text(text)

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("list", list_movies))
app.add_handler(MessageHandler(filters.VIDEO, get_file_id))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))
app.run_polling()
