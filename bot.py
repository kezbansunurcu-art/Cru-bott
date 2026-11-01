import logging
import os
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Loglama ayarları
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# --- 1. KISIM: Render'ı uyandırık tutmak için Flask Sunucusu ---
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Cruise Bot Aktif ve Çalışıyor! 🚀"

def run_flask():
    # Render'ın verdiği PORT'u kullanır, yoksa yerelde 8080'de açılır
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()
# -----------------------------------------------------------

# Kanal kullanıcı adı ve senin Telegram ID'n
FEEDBACK_CHANNEL_ID = "@feeedbakcru"
ADMIN_ID = 7177504155  # Senin Telegram ID'n

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

    data = query.data
    user_id = update.effective_user.id

    if data == "feedback_basla":
        context.user_data["beklenen_feedback"] = True
        keyboard = [[InlineKeyboardButton("🔙 Ana Menüye Dön", callback_data="ana_menu_don")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "Evveet! Lütfen oyun ekran görüntüsünü (fotoğrafı) ve mesajını gönder. İnceleme için yetkiliye iletilecek!",
            reply_markup=reply_markup
        )

    elif data == "sosyal_menu":
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

    elif data == "ana_menu_don":
        context.user_data["beklenen_feedback"] = False
        await query.edit_message_text(
            "Ana menüye dönüldü 🚀 Yapmak istediğin işlemi seçebilirsin:",
            reply_markup=ana_menu_markup()
        )

    elif data.startswith("onayla_"):
        if user_id != ADMIN_ID:
            await query.answer("Bu işlemi yapmaya yetkin yok!", show_alert=True)
            return

        parts = data.split("_")
        gonderen_id = parts[1]
        
        try:
            caption = query.message.caption or ""
            temiz_baslik = caption.split("\n\n────────────────\n")[0] + "\n\n✅ *Onaylandı ve Yayınlandı!*"

            if query.message.photo:
                photo_file_id = query.message.photo[-1].file_id
                await context.bot.send_photo(
                    chat_id=FEEDBACK_CHANNEL_ID,
                    photo=photo_file_id,
                    caption=temiz_baslik,
                    parse_mode="Markdown"
                )
            
            await query.edit_message_caption(caption="✅ *Bu feedback ONAYLANDI ve kanala atıldı.*", parse_mode="Markdown")
            await context.bot.send_message(chat_id=int(gonderen_id), text="🎉 Geri bildirimin yetkili tarafından onaylandı ve kanalda yayınlandı!")
        except Exception as e:
            await query.edit_message_caption(caption=f"⚠️ Hata oluştu: {str(e)}")

    elif data.startswith("reddet_"):
        if user_id != ADMIN_ID:
            await query.answer("Bu işlemi yapmaya yetkin yok!", show_alert=True)
            return

        parts = data.split("_")
        gonderen_id = parts[1]
        
        try:
            await query.edit_message_caption(caption="❌ *Bu feedback REDDEDİLDİ.*", parse_mode="Markdown")
            await context.bot.send_message(chat_id=int(gonderen_id), text="❌ Üzgünüz, gönderdiğiniz geri bildirim yetkili tarafından reddedildi.")
        except Exception as e:
            print(f"Reddetme hatası: {e}")

async def feedback_alici(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("beklenen_feedback"):
        user = update.effective_user
        
        if not update.message.photo:
            await update.message.reply_text(
                "❌ **Hata!** Sadece metin gönderemezsin. Lütfen ekran görüntüsü (fotoğraf) yükle."
            )
            return

        user_text = update.message.caption or update.message.text or "Açıklama yok"
        photo_file_id = update.message.photo[-1].file_id
        
        admin_mesaji = (
            f"📩 **Yeni Onay Bekleyen Feedback!**\n"
            f"👤 Gönderen: {user.first_name} (@{user.username})\n"
            f"🆔 ID: `{user.id}`\n\n"
            f"💬 **Mesaj:** {user_text}\n\n"
            f"────────────────"
        )

        keyboard = [
            [
                InlineKeyboardButton("✅ Onayla", callback_data=f"onayla_{user.id}"),
                InlineKeyboardButton("❌ Reddet", callback_data=f"reddet_{user.id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_file_id,
            caption=admin_mesaji,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

        context.user_data["beklenen_feedback"] = False
        await update.message.reply_text(
            "🚀 Geri bildirimin ve ekran görüntün inceleme için yetkiliye gönderildi. Onaylandığında kanalda yayınlanacak!",
            reply_markup=ana_menu_markup()
        )

if __name__ == '__main__':
    # 1. Flask sunucusunu arka planda başlat (Uykuyu önlemek için)
    keep_alive()

    # 2. Telegram Botunu başlat
    TOKEN = "8710503570:AAGQHq_lfgvKjYJLN0oXdTjw4kZPN3tUcfg"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & (~filters.COMMAND), feedback_alici))

    print("Bot ve Web Sunucusu çalışıyor...")
    app.run_polling()
    
