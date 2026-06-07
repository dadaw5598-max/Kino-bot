import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = "8503519871:AAFVIxzEvVjJZlmRr6M-dRf0Gl2xzU7YGt4"

MOVIES = {
    "001": {
        "title": "Birinchi kino",
        "file_id": "BAACAgEAAxkBAAMGaiS-Pls08mdOirvxxVmQeBC5WJEAAwQAAqwNEEdb4RiDHppNJTsE",
    },
}

logging.basicConfig(level=logging.INFO)

def movie_keyboard(code):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📹 Tomosha qilish", callback_data=f"watch_{code}")],
        [InlineKeyboardButton("⭐ Baholash", callback_data=f"rate_{code}"),
         InlineKeyboardButton("🕐 Ko'rmoqchiman", callback_data=f"later_{code}")],
        [InlineKeyboardButton("🏠 Asosiy Menyu", callback_data="menu")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.callback_query.message
    await msg.reply_text(
        "🎬 *Kino Botga xush kelibsiz!*\n\n"
        "🎥 Kerakli kinongizning kodini yuboring",
        parse_mode="Markdown"
    )

async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip().zfill(3)
    movie = MOVIES.get(code)
    if not movie:
        await update.message.reply_text(
            "❌ *Kino topilmadi!*\n\n"
            "🔢 Iltimos, to'g'ri kodni kiriting",
            parse_mode="Markdown"
        )
        return
    keyboard = movie_keyboard(code)
    await update.message.reply_text(
        "🎬",
        reply_markup=keyboard
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("watch_"):
        code = data.split("_")[1]
        movie = MOVIES.get(code)
        if movie:
            loading = await query.message.reply_text("⏳ *Yuklanmoqda...*", parse_mode="Markdown")
            await context.bot.send_video(
                chat_id=query.message.chat_id,
                video=movie["file_id"],
                caption=f"🎬 {movie['title']}",
                protect_content=True,
            )
            await loading.edit_text("🎉 *Maroqli tomosha!*", parse_mode="Markdown")
            await asyncio.sleep(10)
            await loading.delete()

    elif data.startswith("rate_"):
        await query.message.reply_text("⭐ Baholash funksiyasi tez orada!")
    elif data.startswith("later_"):
        await query.message.reply_text("🕐 Keyinroq ko'rish ro'yxatiga qo'shildi!")
    elif data == "menu":
        await start(update, context)

async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.video:
        file_id = update.message.video.file_id
        await update.message.reply_text(f"File ID:\n`{file_id}`", parse_mode="Markdown")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.VIDEO, get_file_id))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))
app.run_polling()
