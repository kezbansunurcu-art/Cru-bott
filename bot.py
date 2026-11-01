import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Loglama ayarları (terminalde hareketleri görmek için)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"Selam {user_name}! Cruise bot başarıyla çalıştı 🚀")

# Kullanıcının yazdığı normal metinlere cevap veren fonksiyon
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.reply_text(f"Bana şunu yazdın: {user_message}")

if __name__ == '__main__':
    # Token'ın
    TOKEN = "8710503570:AAGQHq_lfgvKjYJLN0oXdTjw4kZPN3tUcfg"

    app = ApplicationBuilder().token(TOKEN).build()

    # Komut dinleyicileri
    app.add_handler(CommandHandler("start", start))

    # Normal metin mesajlarını dinleyen handler
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))

    print("Bot çalışıyor...")
    app.run_polling()
    
