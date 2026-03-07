# 50scent 🌸

A personal Telegram bot for managing your perfume wardrobe.

## Features

- **My Perfumes** — your personal wardrobe. Add, browse, and delete fragrances
- **Search** — find perfumes in the catalog by name, brand, or note. Add to wardrobe or wishlist directly from results
- **Wishlist** — save fragrances you want to buy. Move to wardrobe in one tap
- **Add manually** — add a perfume from your own collection: brand, name, season, mood, and a personal note
- **Catalog** — browse a curated perfume database with notes and brand info

## Tech Stack

- Python 3
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) v22
- SQLite

## Local Setup

1. Clone the repo
2. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your bot token:
   ```bash
   cp .env.example .env
   ```
4. Run:
   ```bash
   python3 bot.py
   ```

## Deployment

Deployed on [Fly.io](https://fly.io) with a persistent volume for the SQLite database.

```bash
fly deploy
```
