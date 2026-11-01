
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ["BOT_TOKEN"]

SITE = "https://yenisitecru.netlify.app"
KANAL = "https://t.me/+3Bwdx2XCQtdlY2Vk"
TIKTOK = "https://tiktok.com/@cruiseno15"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌐 SİTEM", url=SITE)],
        [InlineKeyboardButton("📢 TELEGRAM KANALIM", url=KANAL)]
    ]

    await update.message.reply_text(
        "👋 Hoş geldin!\n\nBağlantılardan birini seç:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def sosyal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎵 TikTok", url=TIKTOK)]
    ]

    await update.message.reply_text(
        "📱 Sosyal medya hesaplarım:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("sosyal", sosyal))

print("BOT ÇALIŞIYOR!")
app.run_polling()
