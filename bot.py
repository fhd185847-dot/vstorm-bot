import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
import yt_dlp

BOT_TOKEN = "9165875979:AAG6L4dnuBc-hyczG09JPP_6EG_jUYikV3Q"

def extract_username(text: str):
    match = re.search(r"tiktok\.com/@([a-zA-Z0-9._]+)", text)
    if match:
        return match.group(1)
    return None

def get_tiktok_info(username: str):
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'skip_download': True
    }
    url = f"https://www.tiktok.com/@{username}"
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except Exception:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك في بوت فحص الحسابات! 👋\nأرسل رابط أي حساب تيك توك وسأعرض لك المعلومات العامة المتاحة عنه."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    username = extract_username(text)

    if not username:
        await update.message.reply_text("يرجى إرسال رابط حساب تيك توك صحيح (مثال: https://www.tiktok.com/@username)")
        return

    msg = await update.message.reply_text("جاري فحص الحساب...")
    info = get_tiktok_info(username)

    if not info:
        await msg.edit_text("تعذر جلب بيانات هذا الحساب. قد يكون الحساب خاصاً أو غير موجود.")
        return

    channel_name = info.get('uploader', username)
    channel_id = info.get('uploader_id', username)
    description = info.get('description', 'لا يوجد وصف')
    country = info.get('country') or info.get('location') or "غير محدد علناً"

    reply_content = (
        f"📋 **معلومات الحساب:**\n"
        f"• **المستخدم:** @{channel_id}\n"
        f"• **الاسم التعريفي:** {channel_name}\n"
        f"• **الدولة المسجلة:** {country}\n"
        f"• **البايو:**\n{description}\n\n"
        f"⚠️ *ملاحظة: تيك توك لا يشارك الموقع الجغرافي أو الـ GPS لحماية الخصوصية.*"
    )

    await msg.edit_text(reply_content, parse_mode="Markdown")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("البوت قيد التشغيل الآن...")
    app.run_polling()
