from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler,
    filters,
)

from config import SEARCH_PAGE_SIZE, SEARCH_INPUT, SEASON, MOOD, NOTES, MENU_FILTER
from database import conn, cursor
from db import search_catalog, get_catalog_perfume, get_notes_for_perfume
from add_perfume import add_season, add_mood, add_notes
from wishlist import move_from_wishlist_start
from common import cancel


# ---------- SEARCH ----------

async def search_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup([["Головне меню 🏠"]], resize_keyboard=True)
    await update.message.reply_text("Введи назву, бренд або ноту:", reply_markup=reply_markup)
    return SEARCH_INPUT


async def search_start_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Catalog search triggered from the wardrobe 'Add perfume' button."""
    query = update.callback_query
    await query.answer()
    reply_markup = ReplyKeyboardMarkup([["Головне меню 🏠"]], resize_keyboard=True)
    await query.message.reply_text("Введи назву, бренд або ноту:", reply_markup=reply_markup)
    return SEARCH_INPUT


def _build_search_message(
    results: list, page: int, wardrobe_set: set | None = None, wishlist_set: set | None = None
) -> tuple[str, InlineKeyboardMarkup]:
    if wardrobe_set is None:
        wardrobe_set = set()
    if wishlist_set is None:
        wishlist_set = set()
    total_pages = (len(results) - 1) // SEARCH_PAGE_SIZE + 1
    chunk = results[page * SEARCH_PAGE_SIZE: (page + 1) * SEARCH_PAGE_SIZE]

    rows = []
    for r in chunk:
        key = (r["brand"].lower(), r["name"].lower())
        in_wardrobe = key in wardrobe_set
        in_wishlist = key in wishlist_set
        prefix = ("✅" if in_wardrobe else "") + ("💝" if in_wishlist else "")
        if prefix:
            prefix += " "
        label = f"{prefix}{r['brand']} — {r['name']}"
        if len(label) > 55:
            label = label[:52] + "..."
        rows.append([InlineKeyboardButton(label, callback_data=f"afc:{r['id']}:{page}")])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"sp:{page - 1}"))
    nav.append(InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="sp:noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("➡️", callback_data=f"sp:{page + 1}"))
    if total_pages > 1:
        rows.append(nav)

    return f"Результати ({page + 1}/{total_pages}):", InlineKeyboardMarkup(rows)


async def search_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    results = search_catalog(query, limit=500)
    if not results:
        await update.message.reply_text(
            f"Нічого не знайшла за «{query}» 😔\nСпробуй інший запит або натисни Головне меню 🏠"
        )
        return SEARCH_INPUT

    user_id = update.message.from_user.id
    cursor.execute("SELECT brand, name FROM user_perfumes WHERE user_id=?", (user_id,))
    wardrobe_set = {(r[0].lower(), r[1].lower()) for r in cursor.fetchall()}
    cursor.execute("SELECT brand, name FROM user_wishlist WHERE user_id=?", (user_id,))
    wishlist_set = {(r[0].lower(), r[1].lower()) for r in cursor.fetchall()}
    context.user_data["search_results"] = results
    context.user_data["wardrobe_set"] = wardrobe_set
    context.user_data["wishlist_set"] = wishlist_set
    text, inline_markup = _build_search_message(results, 0, wardrobe_set, wishlist_set)
    await update.message.reply_text(text, reply_markup=inline_markup)
    return SEARCH_INPUT


async def search_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "sp:noop":
        return

    page = int(query.data.split(":")[1])
    results = context.user_data.get("search_results", [])
    if not results:
        await query.edit_message_text("Результати не знайдено.")
        return

    wardrobe_set = context.user_data.get("wardrobe_set", set())
    wishlist_set = context.user_data.get("wishlist_set", set())
    text, inline_markup = _build_search_message(results, page, wardrobe_set, wishlist_set)
    try:
        await query.edit_message_text(text, reply_markup=inline_markup)
    except BadRequest:
        pass


# ---------- CATALOG DETAIL ----------

async def _show_catalog_detail(query, context, perfume_id: int, page: int):
    perfume = get_catalog_perfume(perfume_id)
    if not perfume:
        await query.edit_message_text("Аромат не знайдено.")
        return
    notes = get_notes_for_perfume(perfume_id)
    lines = [f"✨ {perfume['brand']} — {perfume['name']}"]
    if notes:
        lines.append(f"\n🎵 Ноти: {', '.join(notes)}")
    cursor.execute(
        "SELECT id FROM user_wishlist WHERE user_id=? AND catalog_id=?",
        (query.from_user.id, perfume_id),
    )
    in_wishlist = cursor.fetchone() is not None
    buttons = [
        [InlineKeyboardButton("➕ Додати до гардеробу", callback_data=f"afc_add:{perfume_id}")],
    ]
    if in_wishlist:
        buttons.append([InlineKeyboardButton("💝 Видалити з вішлісту", callback_data=f"wlra:{perfume_id}:{page}")])
    else:
        buttons.append([InlineKeyboardButton("💝 До вішлісту", callback_data=f"wla:{perfume_id}:{page}")])
    buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"afc_back:{page}")])
    try:
        await query.edit_message_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(buttons))
    except BadRequest:
        pass


async def catalog_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("afc_back:"):
        page = int(query.data.split(":")[1])
        results = context.user_data.get("search_results", [])
        if not results:
            await query.edit_message_text("Результати не знайдено.")
            return
        wardrobe_set = context.user_data.get("wardrobe_set", set())
        wishlist_set = context.user_data.get("wishlist_set", set())
        text, markup = _build_search_message(results, page, wardrobe_set, wishlist_set)
        try:
            await query.edit_message_text(text, reply_markup=markup)
        except BadRequest:
            pass
        return

    parts = query.data.split(":")
    perfume_id = int(parts[1])
    page = int(parts[2]) if len(parts) > 2 else 0
    await _show_catalog_detail(query, context, perfume_id, page)


# ---------- ADD FROM CATALOG ----------

async def add_from_catalog_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    perfume_id = int(query.data.split(":")[1])
    perfume = get_catalog_perfume(perfume_id)
    if not perfume:
        await query.answer("Аромат не знайдено", show_alert=True)
        return ConversationHandler.END

    context.user_data["brand"] = perfume["brand"]
    context.user_data["name"] = perfume["name"]
    reply_markup = ReplyKeyboardMarkup([["Головне меню 🏠"]], resize_keyboard=True)
    await query.message.reply_text(
        f"Додаємо: {perfume['brand']} — {perfume['name']}\n\nНа який сезон він більше підходить?",
        reply_markup=reply_markup,
    )
    return SEASON


# ---------- CONVERSATION HANDLERS ----------

search_handler = ConversationHandler(
    entry_points=[
        MessageHandler(filters.TEXT & filters.Regex("^🔍 Пошук$"), search_start),
        CallbackQueryHandler(search_start_inline, pattern="^wp:add_search$"),
    ],
    states={
        SEARCH_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND & MENU_FILTER, search_query)],
    },
    fallbacks=[
        MessageHandler(filters.Regex("^Головне меню 🏠$"), cancel),
        CommandHandler("cancel", cancel),
    ],
)

add_from_catalog_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(add_from_catalog_start, pattern="^afc_add:"),
        CallbackQueryHandler(move_from_wishlist_start, pattern="^wlm:"),
    ],
    states={
        SEASON: [MessageHandler(filters.TEXT & ~filters.COMMAND & MENU_FILTER, add_season)],
        MOOD: [MessageHandler(filters.TEXT & ~filters.COMMAND & MENU_FILTER, add_mood)],
        NOTES: [MessageHandler(filters.TEXT & ~filters.COMMAND & MENU_FILTER, add_notes)],
    },
    fallbacks=[
        MessageHandler(filters.Regex("^Головне меню 🏠$"), cancel),
        CommandHandler("cancel", cancel),
    ],
)
