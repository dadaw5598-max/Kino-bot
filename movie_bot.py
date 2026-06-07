import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = "8503519871:AAFVIxzEvVjJZlmRr6M-dRf0Gl2xzU7YGt4"
CHANNEL_ID = -1002853664312

MOVIES = {
    "001": {
        "title": "Birinchi kino",
        "msg_id": 1,
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
    await update.message.reply_text("🎬", reply_markup=movie_keyboard(code))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("watch_"):
        code = data.split("_")[1]
        movie = MOVIES.get(code)
        if movie:
            await query.message.edit_text("⏳ *Yuklanmoqda...*", parse_mode="Markdown")
            try:
                invite = await context.bot.create_chat_invite_link(
                    chat_id=CHANNEL_ID,
                    expire_date=int(asyncio.get_event_loop().time()) + 14400,
                    member_limit=1,
                )
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=f"🎬 *Kino tayyor!*\n\n"
                         f"👇 Quyidagi tugma orqali oching:\n{invite.invite_link}\n\n"
                         f"⚠️ _Link 4 soatdan keyin o'chadi!_",
                    parse_mode="Markdown"
                )
                await query.message.edit_text("🎉 *Maroqli tomosha!*", parse_mode="Markdown")
                await asyncio.sleep(10)
                await query.message.delete()
            except Exception as e:
                await query.message.edit_text("❌ Xatolik yuz berdi!", parse_mode="Markdown")
                logging.error(e)

    elif data.startswith("rate_"):
        await query.message.reply_text("⭐ Baholash funksiyasi tez orada!")
    elif data.startswith("later_"):
        await query.message.reply_text("🕐 Keyinroq ko'rish ro'yxatiga qo'shildi!")
    elif data == "menu":
        await start(update, context)

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))
app.run_polling()
