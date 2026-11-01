import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Loglama ayarları
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Kanal kullanıcı adı
FEEDBACK_CHANNEL_ID = "@feeedbakcru" 

# İzin verilen oyunlar listesi (küçük harfe çevirerek kontrol edeceğiz)
IZIN_VERILEN_OYUNLAR = ["pubg", "roblox", "standoff", "counter", "flame", "cs"]

# Ana Menü
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

# Buton yönetim merkezi
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "feedback_basla":
        context.user_data["beklenen_feedback"] = True
        
        keyboard = [[InlineKeyboardButton("🔙 Ana Menüye Dön", callback_data="ana_menu_don")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "Evveet! Hangi oyun için yazıyorsun? (PUBG, Roblox, Standoff, Counter, Flame)\nLütfen oyun adını da belirterek istek veya geri bildiriminizi yazın:",
            reply_markup=reply_markup
        )

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

    elif query.data == "ana_menu_don":
        context.user_data["beklenen_feedback"] = False
        await query.edit_message_text(
            "Ana menüye dönüldü 🚀 Yapmak istediğin işlemi seçebilirsin:",
            reply_markup=ana_menu_markup()
        )

# Kullanıcının gönderdiği feedback mesajlarını kontrol edip işleyen fonksiyon
async def feedback_alici(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("beklenen_feedback"):
        user = update.effective_user
        user_text = update.message.text or update.message.caption or ""
        
        # Kullanıcının yazdığı mesajı küçük harfe çevirip oyunların geçip geçmediğini kontrol ediyoruz
        mesaj_kucuk = user_text.lower()
        oyun_bulundu = any(oyun in mesaj_kucuk for oyun in IZIN_VERILEN_OYUNLAR)

        # Eğer izin verilen oyunlardan biri geçmiyorsa hata ver ve kanala atma
        if not oyun_bulundu:
            await update.message.reply_text(
                "❌ **Hata!** Gönderdiğiniz mesajda desteklenen oyunlardan biri (PUBG, Roblox, Standoff, Counter, Flame) bulunamadı. Lütfen geçerli bir oyun belirterek tekrar yazın."
            )
            return  # Burada işlemi kesiyoruz, kanala göndermiyor

        # Oyun bulunduysa kanala ilet
        baslik = f"📩 **Yeni Feedback Var!**\n👤 Gönderen: {user.first_name} (@{user.username})\n🆔 ID: `{user.id}`\n\n💬 **Mesaj:** {user_text}"

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
    
