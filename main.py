import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
GAME_URL = "https://oscurantismo.github.io/gleamorrow/"

if not TOKEN:
    raise ValueError("BOT_TOKEN is missing. Please set it in Railway environment variables.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Tap below to open Gleamorrow:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text="🚀 Launch Gleamorrow", web_app={"url": GAME_URL})]
        ])
    )

def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", start))
    app.run_polling()  # No await

if __name__ == "__main__":
    main()
