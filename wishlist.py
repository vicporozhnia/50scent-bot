from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import ContextTypes, ConversationHandler

from config import WISHLIST_PAGE_SIZE, MAIN_KEYBOARD, SEASON
from database import conn, cursor
from db import get_catalog_perfume, get_notes_for_perfume


# ---------- HELPERS ----------

def _get_wishlist(user_id: int) -> list:
    cursor.execute(
        "SELECT id, catalog_id, brand, name FROM user_wishlist WHERE user_id=? ORDER BY brand, name",
        (user_id,),
    )
    return cursor.fetchall()


def _wishlist_keyboard(rows: list, page: int) -> InlineKeyboardMarkup:
    total_pages = max(1, (len(rows) - 1) // WISHLIST_PAGE_SIZE + 1)
    chunk = rows[page * WISHLIST_PAGE_SIZE: (page + 1) * WISHLIST_PAGE_SIZE]
    buttons = []
    for wl_id, catalog_id, brand, name in chunk:
        label = f"{brand} — {name}"
        if len(label) > 55:
            label = label[:52] + "..."
        buttons.append([InlineKeyboardButton(label, callback_data=f"wl:{wl_id}:{page}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"wl:list:{page - 1}"))
    nav.append(InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="wl:noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("➡️", callback_data=f"wl:list:{page + 1}"))
    if total_pages > 1:
        buttons.append(nav)
    return InlineKeyboardMarkup(buttons)


# ---------- HANDLERS ----------

async def show_wishlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    rows = _get_wishlist(user_id)
    if not rows:
        await update.message.reply_text("Вішліст порожній 🥲")
        return
    await update.message.reply_text("💝 Вішліст:", reply_markup=_wishlist_keyboard(rows, 0))


async def wishlist_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("wl:list:"):
        page = int(data.split(":")[-1])
        rows = _get_wishlist(query.from_user.id)
        if not rows:
            await query.edit_message_text("Вішліст порожній 🥲")
            return
        try:
            await query.edit_message_text("💝 Вішліст:", reply_markup=_wishlist_keyboard(rows, page))
        except BadRequest:
            pass
        return

    if data == "wl:noop":
        return

    # Remove from wishlist: wlr:{wl_id}:{page}
    if data.startswith("wlr:"):
        parts = data.split(":")
        wl_id = int(parts[1])
        page = int(parts[2]) if len(parts) > 2 else 0
        cursor.execute("DELETE FROM user_wishlist WHERE id=? AND user_id=?", (wl_id, query.from_user.id))
        conn.commit()
        rows = _get_wishlist(query.from_user.id)
        if not rows:
            await query.edit_message_text("Вішліст порожній 🥲")
            return
        page = min(page, max(0, (len(rows) - 1) // WISHLIST_PAGE_SIZE))
        try:
            await query.edit_message_text("💝 Вішліст:", reply_markup=_wishlist_keyboard(rows, page))
        except BadRequest:
            pass
        return

    # Add to wishlist from catalog detail: wla:{catalog_id}:{page}
    if data.startswith("wla:"):
        parts = data.split(":")
        catalog_id = int(parts[1])
        page = int(parts[2]) if len(parts) > 2 else 0
        perfume = get_catalog_perfume(catalog_id)
        if perfume:
            cursor.execute(
                "INSERT OR IGNORE INTO user_wishlist (user_id, catalog_id, brand, name) VALUES (?, ?, ?, ?)",
                (query.from_user.id, catalog_id, perfume["brand"], perfume["name"]),
            )
            conn.commit()
        from catalog import _show_catalog_detail
        await _show_catalog_detail(query, context, catalog_id, page)
        return

    # Remove from wishlist from catalog detail: wlra:{catalog_id}:{page}
    if data.startswith("wlra:"):
        parts = data.split(":")
        catalog_id = int(parts[1])
        page = int(parts[2]) if len(parts) > 2 else 0
        cursor.execute(
            "DELETE FROM user_wishlist WHERE user_id=? AND catalog_id=?",
            (query.from_user.id, catalog_id),
        )
        conn.commit()
        from catalog import _show_catalog_detail
        await _show_catalog_detail(query, context, catalog_id, page)
        return

    # Add wardrobe item to wishlist: wlaw:{perfume_id}:{back_page}
    if data.startswith("wlaw:"):
        parts = data.split(":")
        perfume_id = int(parts[1])
        cursor.execute(
            "SELECT brand, name FROM user_perfumes WHERE id=? AND user_id=?",
            (perfume_id, query.from_user.id),
        )
        row = cursor.fetchone()
        if row:
            brand, name = row
            cursor.execute(
                "SELECT cp.id FROM catalog_perfumes cp JOIN catalog_brands cb ON cp.brand_id=cb.id "
                "WHERE LOWER(cb.name)=LOWER(?) AND LOWER(cp.name)=LOWER(?)",
                (brand, name),
            )
            cat_row = cursor.fetchone()
            if cat_row:
                cursor.execute(
                    "INSERT OR IGNORE INTO user_wishlist (user_id, catalog_id, brand, name) VALUES (?, ?, ?, ?)",
                    (query.from_user.id, cat_row[0], brand, name),
                )
                conn.commit()
                await query.answer("Додано до вішлісту 💝", show_alert=False)
            else:
                await query.answer("Аромат не знайдено в каталозі 😔", show_alert=True)
        return

    # Wishlist item detail: wl:{wl_id}:{page}
    parts = data.split(":")
    wl_id = int(parts[1])
    back_page = int(parts[2]) if len(parts) > 2 else 0
    cursor.execute(
        "SELECT catalog_id, brand, name FROM user_wishlist WHERE id=? AND user_id=?",
        (wl_id, query.from_user.id),
    )
    row = cursor.fetchone()
    if not row:
        await query.edit_message_text("Не знайдено.")
        return
    catalog_id, brand, name = row
    notes = get_notes_for_perfume(catalog_id)
    lines = [f"💝 {brand} — {name}"]
    if notes:
        lines.append(f"\n🎵 Ноти: {', '.join(notes)}")
    buttons = [
        [InlineKeyboardButton("➕ Перенести до гардеробу", callback_data=f"wlm:{wl_id}:{back_page}")],
        [InlineKeyboardButton("🗑 Видалити з вішлісту", callback_data=f"wlr:{wl_id}:{back_page}")],
        [InlineKeyboardButton("⬅️ Назад", callback_data=f"wl:list:{back_page}")],
    ]
    try:
        await query.edit_message_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(buttons))
    except BadRequest:
        pass


async def move_from_wishlist_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":")
    wl_id = int(parts[1])
    context.user_data["from_wishlist_id"] = wl_id
    cursor.execute(
        "SELECT catalog_id, brand, name FROM user_wishlist WHERE id=? AND user_id=?",
        (wl_id, query.from_user.id),
    )
    row = cursor.fetchone()
    if not row:
        await query.answer("Не знайдено", show_alert=True)
        return ConversationHandler.END
    catalog_id, brand, name = row
    context.user_data["brand"] = brand
    context.user_data["name"] = name
    await query.message.reply_text(
        f"Переносимо: {brand} — {name}\n\nНа який сезон він більше підходить?",
        reply_markup=ReplyKeyboardMarkup([["Головне меню 🏠"]], resize_keyboard=True),
    )
    return SEASON
