import os
import re
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
MY_API_URL = os.getenv("MY_API_URL") 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بك في البوت الخارق المعتمد على سيرفرنا المنفصل!\n\n"
        "أرسل لي أي رابط عام من يوتيوب أو انستغرام وسأقوم بتحميله فوراً."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not re.match(r'(https?://)?(www\.)?(instagram\.com|youtube\.com|youtu\.be)', url):
        await update.message.reply_text("❌ عذراً، البوت يدعم روابط يوتيوب وإنستغرام العامة فقط.")
        return

    status_message = await update.message.reply_text("⚡ جاري إرسال الطلب للسيرفر الخاص بفك التشفير...")
    request_url = f"{MY_API_URL}/download?url={url}"

    try:
        response = requests.get(request_url, timeout=40)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                
                if data.get("source") == "playlist_or_carousel":
                    for item in data["data"]:
                        if item["type"] == "video":
                            await update.message.reply_video(video=item["url"])
                        else:
                            await update.message.reply_photo(photo=item["url"])
                else:
                    m_url = data["media_url"]
                    caption_text = f"🎬 **{data.get('title', 'تم الاستخراج!')}**\n\nتم التحميل من السيرفر المنفصل!"
                    
                    if data["type"] == "video":
                        await update.message.reply_video(video=m_url, caption=caption_text, parse_mode="Markdown")
                    else:
                        await update.message.reply_photo(photo=m_url, caption=caption_text, parse_mode="Markdown")
                
                await status_message.delete()
            else:
                await status_message.edit_text("❌ فشل السيرفر في استخراج روابط التحميل.")
        else:
            await status_message.edit_text(f"❌ واجه سيرفر الـ API مشكلة. كود الخطأ: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
        await status_message.edit_text("💥 حدث خطأ أثناء الاتصال بسيرفر الـ API المخصص.")

def main():
    if not TOKEN or not MY_API_URL:
        print("Error: Missing Environment Variables")
        return

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
