
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import logging, os

# إعداد السجل
logging.basicConfig(level=logging.INFO)

# قاعدة بيانات مؤقتة (dict) - استبدلها لاحقاً بقاعدة SQLite
ratings = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً! أرسل /rate @username لتقييم بائع.")

async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("يرجى استخدام الأمر بهذا الشكل:\n/rate @اسم_المستخدم")
        return

    seller = context.args[0]
    keyboard = [
        [InlineKeyboardButton("⭐", callback_data=f"{seller}:1"),
         InlineKeyboardButton("⭐⭐", callback_data=f"{seller}:2"),
         InlineKeyboardButton("⭐⭐⭐", callback_data=f"{seller}:3"),
         InlineKeyboardButton("⭐⭐⭐⭐", callback_data=f"{seller}:4"),
         InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data=f"{seller}:5")]
    ]
    await update.message.reply_text(f"اختر تقييمك لـ {seller}:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    seller, stars = data.split(":")
    user_id = query.from_user.id

    ratings.setdefault(seller, {})
    if user_id in ratings[seller]:
        await query.edit_message_text("لقد قمت بتقييم هذا البائع من قبل.")
        return

    ratings[seller][user_id] = int(stars)
    await query.edit_message_text(f"تم تسجيل تقييمك: {stars} ⭐ لـ {seller}")

async def view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("استخدم الأمر: /view @اسم_المستخدم")
        return

    seller = context.args[0]
    if seller not in ratings or not ratings[seller]:
        await update.message.reply_text("لا يوجد تقييمات لهذا البائع بعد.")
        return

    all_ratings = list(ratings[seller].values())
    avg = sum(all_ratings) / len(all_ratings)
    await update.message.reply_text(f"تقييم {seller}: ⭐ {round(avg, 2)} من 5 ({len(all_ratings)} تقييم)")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/rate @username - تقييم بائع\n/view @username - عرض التقييمات")

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("rate", rate))
    app.add_handler(CommandHandler("view", view))
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()

if __name__ == '__main__':
    main()
