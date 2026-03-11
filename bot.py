import logging
import os
import sys
import threading

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import TOKEN, MAIN_KEYBOARD, RESTART_NOTIFY_FILE
from common import cancel
from add_perfume import conv_handler
from wardrobe import show_perfumes, wardrobe_detail_callback, add_note_handler, search_by_mood
from wishlist import show_wishlist, wishlist_callback
from catalog import search_handler, search_page_callback, catalog_detail_callback, add_from_catalog_handler


# ---------- START ----------

async def start(update: Update, context):
    reply_markup = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)
    await update.message.reply_text("Привіт 🌸 Обери дію:", reply_markup=reply_markup)


# ---------- RESTART ----------

async def restart(update: Update, context):
    with open(RESTART_NOTIFY_FILE, "w") as f:
        f.write(str(update.effective_chat.id))
    # Delay so handler returns first — lets the framework advance the Telegram
    # update offset before replacing the process. Without the delay the same
    # restart message gets redelivered on every startup, causing an infinite loop.
    threading.Timer(1.0, lambda: os.execv(sys.executable, [sys.executable] + sys.argv)).start()


# ---------- STARTUP NOTIFICATION ----------

async def on_startup(app):
    if os.path.exists(RESTART_NOTIFY_FILE):
        with open(RESTART_NOTIFY_FILE) as f:
            chat_id = int(f.read().strip())
        os.remove(RESTART_NOTIFY_FILE)
        onboarding = (
            "✅ Бот перезапущено\\!\n\n"
            "Ось що я вмію:\n\n"
            "👗 *Мої аромати* — твій особистий гардероб\\. Додавай парфуми вручну або з каталогу, переглядай і видаляй\\. Ділись карткою окремого аромату з друзями кнопкою 📤\\.\n\n"
            "🔍 *Пошук* — знаходь аромати в каталозі за назвою, брендом або нотою\\. Додавай у гардероб або вішліст прямо з результатів\\.\n\n"
            "💝 *Вішліст* — зберігай аромати, які хочеш придбати\\. Переміщуй до гардеробу одним натисканням\\. Ділись усім списком бажань кнопкою 📤\\.\n\n"
            "✍️ *Ввести вручну* — додай аромат із власної колекції: бренд, назва, сезон, настрій та нотатка\\.\n\n"
            "🔄 *Перезапустити бот* — якщо щось пішло не так\\."
        )
        await app.bot.send_message(chat_id=chat_id, text=onboarding, parse_mode="MarkdownV2")


# ---------- MAIN ----------

def main():
    app = ApplicationBuilder().token(TOKEN).post_init(on_startup).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(conv_handler)
    app.add_handler(add_from_catalog_handler)
    app.add_handler(add_note_handler)
    app.add_handler(search_handler)
    app.add_handler(CallbackQueryHandler(search_page_callback, pattern="^sp:"))
    app.add_handler(CallbackQueryHandler(catalog_detail_callback, pattern="^afc"))
    app.add_handler(CallbackQueryHandler(wardrobe_detail_callback, pattern="^wp"))
    app.add_handler(CallbackQueryHandler(wishlist_callback, pattern="^wl"))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("👗 Мої аромати"), show_perfumes))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^💝 Вішліст$"), show_wishlist))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Головне меню 🏠$"), cancel))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^🔄 Перезапустити бот$"), restart))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_by_mood))

    logger.info("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
