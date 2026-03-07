from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler,
    filters,
)

from config import BRAND, NAME, SEASON, MOOD, NOTES, MENU_FILTER
from database import conn, cursor
from db import suggest_by_notes
from common import cancel


async def add_start_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show choice: search catalog or enter manually."""
    query = update.callback_query
    await query.answer()
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Знайти в каталозі", callback_data="wp:add_search")],
        [InlineKeyboardButton("✍️ Ввести вручну", callback_data="wp:add_manual")],
    ])
    await query.edit_message_text("Як хочеш додати аромат?", reply_markup=markup)
    return ConversationHandler.END


async def add_start_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual entry flow: ask for brand."""
    query = update.callback_query
    await query.answer()
    reply_markup = ReplyKeyboardMarkup([["Головне меню 🏠"]], resize_keyboard=True)
    await query.message.reply_text("Введи бренд парфуму:", reply_markup=reply_markup)
    return BRAND


async def add_brand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["brand"] = update.message.text
    await update.message.reply_text("Тепер назву аромату:")
    return NAME


async def add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("На який сезон він більше підходить?")
    return SEASON


async def add_season(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["season"] = update.message.text
    await update.message.reply_text("Який настрій цього аромату?")
    return MOOD


async def add_mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mood"] = update.message.text.lower()
    await update.message.reply_text(
        "Додай нотатку до аромату (до 140 символів), або напиши — щоб пропустити:"
    )
    return NOTES


async def add_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "—":
        notes = None
    elif len(text) > 140:
        await update.message.reply_text(
            "Нотатка занадто довга 😅 Максимум 140 символів. Спробуй ще раз:"
        )
        return NOTES
    else:
        notes = text

    cursor.execute(
        "INSERT INTO user_perfumes (user_id, brand, name, season, mood, notes) VALUES (?, ?, ?, ?, ?, ?)",
        (
            update.message.from_user.id,
            context.user_data["brand"],
            context.user_data["name"],
            context.user_data["season"],
            context.user_data["mood"],
            notes,
        ),
    )
    conn.commit()

    from_wishlist_id = context.user_data.get("from_wishlist_id")
    if from_wishlist_id:
        cursor.execute(
            "DELETE FROM user_wishlist WHERE id=? AND user_id=?",
            (from_wishlist_id, update.message.from_user.id),
        )
        conn.commit()
        await update.message.reply_text("💝 Аромат перенесено до гардеробу!")
    else:
        await update.message.reply_text("✨ Аромат збережено у гардероб!")

    if notes:
        note_list = [n.strip().lower() for n in notes.split(",") if n.strip()]
        suggestions = suggest_by_notes(note_list, limit=3)
        if suggestions:
            lines = [
                f"  • {s['brand']} — {s['name']} ({s['shared']} спільних нот)"
                for s in suggestions
            ]
            await update.message.reply_text("Схожі аромати з каталогу:\n" + "\n".join(lines))

    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(add_start_inline, pattern="^wp:add$"),
        CallbackQueryHandler(add_start_manual, pattern="^wp:add_manual$"),
    ],
    states={
        BRAND: [MessageHandler(filters.TEXT & ~filters.COMMAND & MENU_FILTER, add_brand)],
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND & MENU_FILTER, add_name)],
        SEASON: [MessageHandler(filters.TEXT & ~filters.COMMAND & MENU_FILTER, add_season)],
        MOOD: [MessageHandler(filters.TEXT & ~filters.COMMAND & MENU_FILTER, add_mood)],
        NOTES: [MessageHandler(filters.TEXT & ~filters.COMMAND & MENU_FILTER, add_notes)],
    },
    fallbacks=[
        MessageHandler(filters.Regex("^Головне меню 🏠$"), cancel),
        CommandHandler("cancel", cancel),
    ],
)
