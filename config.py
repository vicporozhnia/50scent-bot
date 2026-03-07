import os
import warnings

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

warnings.filterwarnings("ignore", message=".*per_message=False.*")

from telegram.ext import filters

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError(
        "BOT_TOKEN environment variable is not set. "
        "Copy .env.example to .env and add your token."
    )

MAIN_KEYBOARD = [
    ["👗 Мої аромати", "🔍 Пошук"],
    ["💝 Вішліст"],
    ["🔄 Перезапустити бот"],
]

# Conversation states
BRAND, NAME, SEASON, MOOD, NOTES = range(5)
SEARCH_INPUT = 10
ADD_NOTE = 20

# Pagination
WARDROBE_PAGE_SIZE = 10
WISHLIST_PAGE_SIZE = 10
SEARCH_PAGE_SIZE = 5

RESTART_NOTIFY_FILE = "restart_notify.txt"

MENU_FILTER = ~filters.Regex("^(Головне меню 🏠|🔍 Пошук|💝 Вішліст|🔄 Перезапустити бот)$")
