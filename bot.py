from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import json, os, time
import keep_alive  # <-- استدعاء السيرفر

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 إرسال رسالة", callback_data='send_text')],
        [InlineKeyboardButton("🔘 حدد أماكن النشر يدويًا", callback_data='manual_targets')],
        [InlineKeyboardButton("⚙️ إعدادات إضافية (لاحقًا)", callback_data='settings')]
    ]
    await update.message.reply_text("🎛️ *لوحة التحكم للنشر*", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'send_text':
        context.user_data['mode'] = 'send_text'
        await query.edit_message_text("📝 أرسل الرسالة الآن وسيتم نشرها في الأماكن المحددة.")
    elif query.data == 'manual_targets':
        context.user_data['mode'] = 'manual_targets'
        await query.edit_message_text("📥 أرسل معرفات القنوات أو الجروبات (مثال:\n@ch1 -100xxxx)")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = load_config()
    mode = context.user_data.get('mode')

    if mode == 'manual_targets':
        targets = update.message.text.strip().split()
        config['active_targets'] = targets
        save_config(config)
        await update.message.reply_text(f"✅ تم حفظ {len(targets)} مكان.")
    elif mode == 'send_text':
        msg = update.message.text
        delay = config.get('delay_seconds', 5)
        sent = 0
        for cid in config.get("active_targets", []):
            try:
                await context.bot.send_message(chat_id=cid, text=msg)
                sent += 1
                time.sleep(delay)
            except Exception as e:
                print(f"❌ خطأ مع {cid}: {e}")
        await update.message.reply_text(f"✅ تم النشر في {sent} مكان.")
    context.user_data.clear()

def main():
    keep_alive.keep_alive()  # <-- تشغيل السيرفر
    TOKEN = os.getenv("BOT_TOKEN")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT, message_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
