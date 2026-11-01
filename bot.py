import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Loglama ayarları
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Kanal kullanıcı adı
FEEDBACK_CHANNEL_ID = "@feeedbakcru" 

# Ana Menü (Start ve Geri Dönüşlerde gösterilecek butonlar)
def ana_menu_markup():
    keyboard = [
        [InlineKeyboardButton("💬 Feedback Gönder", callback_data="feedback_basla")],
        [InlineKeyboardButton("🌐 Sosyal Medya & Hesaplar", callback_data="sosyal_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"Selam {user_name}! Cruise bot aktif 🚀\n\nAşağıdaki menüden yapmak istediğin işlemi seçebilirsin:",
        reply_markup=ana_menu_markup()
    )

# Buton yönetim merkezi (Hangi butona basıldıysa onu yakalar)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # 1. Feedback Başlatma
    if query.data == "feedback_basla":
        context.user_data["beklenen_feedback"] = True
        
        # Geri dön butonu ile birlikte iptal seçeneği sunalım
        keyboard = [[InlineKeyboardButton("🔙 Ana Menüye Dön", callback_data="ana_menu_don")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "Evveet! Ne istemiştiniz / öneriyorsunuz? Lütfen istek veya geri bildiriminizi (varsa ekran görüntüsüyle birlikte) buraya yazın:",
            reply_markup=reply_markup
        )

    # 2. Sosyal Medya Menüsü
    elif query.data == "sosyal_menu":
        keyboard = [
            [InlineKeyboardButton("📢 Telegram Kanalım", url="https://t.me/+3Bwdx2XCQtdlY2Vk")],
            [InlineKeyboardButton("🎵 TikTok Hesabım", url="https://tiktok.com/@cruiseno15")],
            [InlineKeyboardButton("📺 YouTube Hesabım", url="https://www.youtube.com/@sadececryusebaba")],
            [InlineKeyboardButton("🔙 Geri Dön", callback_data="ana_menu_don")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "İşte sosyal medya hesaplarımız ve platformlarımız 👇 İstediğine tıklayabilirsin:",
            reply_markup=reply_markup
        )

    # 3. Ana Menüye Geri Dönüş
    elif query.data == "ana_menu_don":
        context.user_data["beklenen_feedback"] = False # Feedback durumunu iptal et
        await query.edit_message_text(
            "Ana menüye dönüldü 🚀 Yapmak istediğin işlemi seçebilirsin:",
            reply_markup=ana_menu_markup()
        )

# Kullanıcının gönderdiği feedback mesajlarını yakalayan fonksiyon
async def feedback_alici(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("beklenen_feedback"):
        user = update.effective_user
        user_text = update.message.text or update.message.caption or "Açıklama yok"
        
        baslik = f"📩 **Yeni Feedback Var!**\n👤 Gönderen: {user.first_name} (@{user.username})\n🆔 ID: `{user.id}`\n\n💬 **Mesaj:** {user_text}"

        # Fotoğraf veya metin kontrolü ile kanala yollama
        if update.message.photo:
            photo_file_id = update.message.photo[-1].file_id
            await context.bot.send_photo(
                chat_id=FEEDBACK_CHANNEL_ID,
                photo=photo_file_id,
                caption=baslik,
                parse_mode="Markdown"
            )
        else:
            await context.bot.send_message(
                chat_id=FEEDBACK_CHANNEL_ID,
                text=baslik,
                parse_mode="Markdown"
            )

        # Durumu sıfırla ve ana menü butonlarıyla teşekkür et
        context.user_data["beklenen_feedback"] = False
        await update.message.reply_text(
            "Teşekkürler! Geri bildiriminiz başarıyla kanalımıza iletildi. 🚀",
            reply_markup=ana_menu_markup()
        )

if __name__ == '__main__':
    TOKEN = "8710503570:AAGQHq_lfgvKjYJLN0oXdTjw4kZPN3tUcfg"

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & (~filters.COMMAND), feedback_alici))

    print("Bot çalışıyor...")
    app.run_polling()
        
