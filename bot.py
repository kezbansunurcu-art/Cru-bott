import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Loglama ayarları
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Feedback kanalının kullanıcı adı
FEEDBACK_CHANNEL_ID = "@feeedbakcru" 

# /start komutu ve Feedback butonunu gönderme
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    
    # İnline buton oluşturuyoruz
    keyboard = [[InlineKeyboardButton("💬 Feedback Gönder", callback_data="feedback_basla")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Selam {user_name}! Cruise bot aktif 🚀\n\nBize görüş, öneri veya istek bildirmek için aşağıdaki butona tıklayabilirsin:",
        reply_markup=reply_markup
    )

# Kullanıcı "Feedback Gönder" butonuna bastığında çalışacak fonksiyon
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "feedback_basla":
        # Kullanıcıya ne istediklerini soruyoruz
        context.user_data["beklenen_feedback"] = True
        await query.message.reply_text(
            "Evveet! Ne istemiştiniz / öneriyorsunuz? Lütfen istek veya geri bildiriminizi (varsa ekran görüntüsüyle birlikte) buraya yazın:"
        )

# Kullanıcının gönderdiği mesajları (metin veya fotoğraf) yakalayıp feedback kanalına atan fonksiyon
async def feedback_alici(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Eğer kullanıcı feedback sürecindeyse
    if context.user_data.get("beklenen_feedback"):
        user = update.effective_user
        
        # Kullanıcının yazdığı metin veya resim açıklaması (varsa)
        user_text = update.message.text or update.message.caption or "Açıklama yok"
        
        baslik = f"📩 **Yeni Feedback Var!**\n👤 Gönderen: {user.first_name} (@{user.username})\n🆔 ID: `{user.id}`\n\n💬 **Mesaj:** {user_text}"

        # Eğer kullanıcı fotoğraf/ekran görüntüsü gönderdiyse
        if update.message.photo:
            photo_file_id = update.message.photo[-1].file_id
            await context.bot.send_photo(
                chat_id=FEEDBACK_CHANNEL_ID,
                photo=photo_file_id,
                caption=baslik,
                parse_mode="Markdown"
            )
        else:
            # Sadece metindiyse
            await context.bot.send_message(
                chat_id=FEEDBACK_CHANNEL_ID,
                text=baslik,
                parse_mode="Markdown"
            )

        # Kullanıcıya teşekkür edip durumu sıfırlıyoruz
        context.user_data["beklenen_feedback"] = False
        await update.message.reply_text("Teşekkürler! Geri bildiriminiz başarıyla kanalımıza iletildi. 🚀")

if __name__ == '__main__':
    # Token'ın
    TOKEN = "8710503570:AAGQHq_lfgvKjYJLN0oXdTjw4kZPN3tUcfg"

    app = ApplicationBuilder().token(TOKEN).build()

    # Handler'ları ekliyoruz
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Normal metin veya fotoğraf mesajlarını yakalayan handler
    app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & (~filters.COMMAND), feedback_alici))

    print("Bot çalışıyor...")
    app.run_polling()
    
