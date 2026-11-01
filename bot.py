import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# Loglama ayarları
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Kanal kullanıcı adı
FEEDBACK_CHANNEL_ID = "@feeedbakcru"

# OpenAI Yapay Zeka Ayarları
client = OpenAI(api_key="BURAYA_OPENAI_API_ANAHTARINI_YAZ")

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
            "Evveet! Lütfen ilgili oyunun ekran görüntüsünü gönder. Yapay zeka kontrol edecek!",
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

# Yapay Zeka ile Fotoğrafı Esnek Analiz Etme
async def yapay_zeka_oyun_kontrolu(photo_file_url):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Bu görsel herhangi bir video oyununa, oyun ekranına, lobiye, menüye veya oyun içi bir görüntüye (PUBG, Roblox, Standoff, Counter, Flame vb.) benziyor mu? Lütfen çok esnek ol ve oyunla ilgili herhangi bir görselse sadece 'EVET' de. Alakasız bir fotoğrafsa (kedi, insan yüzü, manzara vb.) 'HAYIR' de. Sadece EVET veya HAYIR yaz."
                        },
                        {
                            "image_url": {"url": photo_file_url},
                            "type": "image_url"
                        }
                    ]
                }
            ],
            max_tokens=5
        )
        cevap = response.choices[0].message.content.strip().upper()
        return "EVET" in cevap
    except Exception as e:
        print(f"Yapay zeka hata verdi: {e}")
        return True # Hata durumunda kullanıcıyı mağdur etmemek için geçmesine izin verelim

# Kullanıcının gönderdiği feedback mesajlarını denetleyen fonksiyon
async def feedback_alici(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("beklenen_feedback"):
        user = update.effective_user
        
        if not update.message.photo:
            await update.message.reply_text(
                "❌ **Hata!** Sadece metin gönderemezsin. Lütfen ekran görüntüsü yükle."
            )
            return

        bekleme_mesaji = await update.message.reply_text("🤖 Yapay zeka inceliyor...")

        try:
            photo_file = await update.message.photo[-1].get_file()
            photo_url = photo_file.file_path

            oyun_onaylandi = await yapay_zeka_oyun_kontrolu(photo_url)

            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=bekleme_mesaji.message_id)

            if not oyun_onaylandi:
                await update.message.reply_text(
                    "❌ **Yapay Zeka Reddetti!** Bu fotoğraf bir oyun ekran görüntüsüne benzemiyor. Lütfen geçerli bir oyun SS'i at."
                )
                return

            user_text = update.message.caption or update.message.text or "Açıklama yok"
            photo_file_id = update.message.photo[-1].file_id
            
            baslik = f"📩 **Yapay Zeka Onaylı Feedback!**\n👤 Gönderen: {user.first_name} (@{user.username})\n🆔 ID: `{user.id}`\n\n💬 **Mesaj:** {user_text}"

            await context.bot.send_photo(
                chat_id=FEEDBACK_CHANNEL_ID,
                photo=photo_file_id,
                caption=baslik,
                parse_mode="Markdown"
            )

            context.user_data["beklenen_feedback"] = False
            await update.message.reply_text(
                "Teşekkürler! Geri bildirimin başarıyla kanalımıza iletildi. 🚀",
                reply_markup=ana_menu_markup()
            )

        except Exception as e:
            await update.message.reply_text(f"Bir hata oluştu: {str(e)}")

if __name__ == '__main__':
    TOKEN = "8710503570:AAGQHq_lfgvKjYJLN0oXdTjw4kZPN3tUcfg"

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & (~filters.COMMAND), feedback_alici))

    print("Bot çalışıyor...")
    app.run_polling()
            
