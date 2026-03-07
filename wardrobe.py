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

from config import MAIN_KEYBOARD, WARDROBE_PAGE_SIZE, ADD_NOTE, MENU_FILTER
from database import conn, cursor
from common import cancel


# ---------- HELPERS ----------

def _get_wardrobe(user_id: int) -> list:
    cursor.execute(
        "SELECT id, brand, name FROM user_perfumes WHERE user_id=? ORDER BY brand, name",
        (user_id,),
    )
    return cursor.fetchall()


def _no_note(notes) -> bool:
    return not notes or notes.strip() in ("", "-", "—")


def _wardrobe_keyboard(rows: list, page: int) -> InlineKeyboardMarkup:
    total_pages = max(1, (len(rows) - 1) // WARDROBE_PAGE_SIZE + 1)
    chunk = rows[page * WARDROBE_PAGE_SIZE: (page + 1) * WARDROBE_PAGE_SIZE]

    buttons = []
    for pid, brand, name in chunk:
        label = f"{brand} — {name}"
        if len(label) > 55:
            label = label[:52] + "..."
        buttons.append([InlineKeyboardButton(label, callback_data=f"wp:{pid}:{page}")])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"wp:list:{page - 1}"))
    nav.append(InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="wp:noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("➡️", callback_data=f"wp:list:{page + 1}"))
    if total_pages > 1:
        buttons.append(nav)

    buttons.append([InlineKeyboardButton("➕ Додати аромат", callback_data="wp:add")])
    return InlineKeyboardMarkup(buttons)


_EMPTY_WARDROBE_MARKUP = InlineKeyboardMarkup(
    [[InlineKeyboardButton("➕ Додати аромат", callback_data="wp:add")]]
)


def _detail_text_and_markup(
    perfume_id: int, brand: str, name: str, season: str, mood: str, notes: str, back_page: int = 0
):
    lines = [f"✨ {brand} — {name}", ""]
    lines.append(f"🌿 Сезон: {season}")
    lines.append(f"💫 Настрій: {mood}")
    if not _no_note(notes):
        lines.append(f"\n📝 {notes}")

    buttons = []
    if _no_note(notes):
        buttons.append([InlineKeyboardButton("✏️ Додати нотатку", callback_data=f"wna:{perfume_id}:{back_page}")])
    buttons.append([InlineKeyboardButton("💝 До вішлісту", callback_data=f"wlaw:{perfume_id}:{back_page}")])
    buttons.append([
        InlineKeyboardButton("⬅️ Назад", callback_data=f"wp:list:{back_page}"),
        InlineKeyboardButton("🗑 Видалити", callback_data=f"wpd:{perfume_id}:{back_page}"),
    ])
    return "\n".join(lines), InlineKeyboardMarkup(buttons)


# ---------- HANDLERS ----------

async def show_perfumes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    rows = _get_wardrobe(user_id)
    if not rows:
        await update.message.reply_text("У тебе ще немає ароматів 🥲", reply_markup=_EMPTY_WARDROBE_MARKUP)
        return
    await update.message.reply_text("👗 Твій гардероб:", reply_markup=_wardrobe_keyboard(rows, 0))


async def search_by_mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.lower()
    user_id = update.message.from_user.id
    cursor.execute(
        "SELECT brand, name, mood, season FROM user_perfumes WHERE user_id=? AND (mood LIKE ? OR season LIKE ?)",
        (user_id, f"%{query}%", f"%{query}%"),
    )
    results = cursor.fetchall()
    if not results:
        await update.message.reply_text("Нічого не знайшла 😔")
    else:
        text = "\n".join([f"✨ {b} {n} — {m}, {s}" for b, n, m, s in results])
        await update.message.reply_text(f"Ось що знайшла:\n{text}")


async def wardrobe_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("wp:list:") or data == "wp:back":
        page = int(data.split(":")[-1]) if data.startswith("wp:list:") else 0
        rows = _get_wardrobe(query.from_user.id)
        if not rows:
            await query.edit_message_text("У тебе ще немає ароматів 🥲", reply_markup=_EMPTY_WARDROBE_MARKUP)
            return
        try:
            await query.edit_message_text("👗 Твій гардероб:", reply_markup=_wardrobe_keyboard(rows, page))
        except BadRequest:
            pass
        return

    if data == "wp:noop":
        return

    if data.startswith("wpd:"):
        parts = data.split(":")
        perfume_id = int(parts[1])
        back_page = int(parts[2]) if len(parts) > 2 else 0
        cursor.execute("DELETE FROM user_perfumes WHERE id=? AND user_id=?", (perfume_id, query.from_user.id))
        conn.commit()
        rows = _get_wardrobe(query.from_user.id)
        if not rows:
            try:
                await query.edit_message_text(
                    "🗑 Парфум видалено\n\nГардероб порожній 🥲",
                    reply_markup=_EMPTY_WARDROBE_MARKUP,
                )
            except BadRequest:
                pass
            return
        page = min(back_page, max(0, (len(rows) - 1) // WARDROBE_PAGE_SIZE))
        try:
            await query.edit_message_text(
                "🗑 Парфум видалено\n\n👗 Твій гардероб:",
                reply_markup=_wardrobe_keyboard(rows, page),
            )
        except BadRequest:
            pass
        return

    # Detail card: "wp:{id}:{back_page}"
    parts = data.split(":")
    perfume_id = int(parts[1])
    back_page = int(parts[2]) if len(parts) > 2 else 0
    cursor.execute(
        "SELECT brand, name, season, mood, notes FROM user_perfumes WHERE id=? AND user_id=?",
        (perfume_id, query.from_user.id),
    )
    row = cursor.fetchone()
    if not row:
        await query.edit_message_text("Аромат не знайдено.")
        return
    brand, name, season, mood, notes = row
    text, markup = _detail_text_and_markup(perfume_id, brand, name, season, mood, notes, back_page)
    try:
        await query.edit_message_text(text, reply_markup=markup)
    except BadRequest:
        pass


# ---------- ADD NOTE ----------

async def add_note_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":")
    perfume_id = int(parts[1])
    back_page = int(parts[2]) if len(parts) > 2 else 0
    context.user_data["note_for_perfume"] = perfume_id
    context.user_data["note_back_page"] = back_page
    await query.message.reply_text(
        "Введи нотатку (до 140 символів):",
        reply_markup=ReplyKeyboardMarkup([["Головне меню 🏠"]], resize_keyboard=True),
    )
    return ADD_NOTE


async def add_note_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if len(text) > 140:
        await update.message.reply_text("Нотатка занадто довга 😅 Максимум 140 символів. Спробуй ще раз:")
        return ADD_NOTE

    perfume_id = context.user_data.get("note_for_perfume")
    cursor.execute(
        "UPDATE user_perfumes SET notes=? WHERE id=? AND user_id=?",
        (text, perfume_id, update.message.from_user.id),
    )
    conn.commit()
    cursor.execute(
        "SELECT brand, name, season, mood, notes FROM user_perfumes WHERE id=? AND user_id=?",
        (perfume_id, update.message.from_user.id),
    )
    row = cursor.fetchone()
    await update.message.reply_text(
        "📝 Нотатку збережено!",
        reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True),
    )
    if row:
        brand, name, season, mood, notes = row
        back_page = context.user_data.get("note_back_page", 0)
        detail_text, detail_markup = _detail_text_and_markup(perfume_id, brand, name, season, mood, notes, back_page)
        await update.message.reply_text(detail_text, reply_markup=detail_markup)
    return ConversationHandler.END


add_note_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(add_note_start, pattern="^wna:")],
    states={
        ADD_NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND & MENU_FILTER, add_note_save)],
    },
    fallbacks=[
        MessageHandler(filters.Regex("^Головне меню 🏠$"), cancel),
        CommandHandler("cancel", cancel),
    ],
)
