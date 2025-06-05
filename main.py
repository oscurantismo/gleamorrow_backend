import os
import asyncio
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load token from Railway environment
TOKEN = os.environ.get("BOT_TOKEN")
GAME_URL = "https://oscurantismo.github.io/gleamorrow/"

# Bot command: /start or /play
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Tap below to open Gleamorrow:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text="🚀 Launch Gleamorrow", web_app={"url": GAME_URL})]
        ])
    )

# Set up and run the bot
async def main():
    logging.basicConfig(level=logging.INFO)
    await asyncio.sleep(2)  # Delay to allow Railway container to settle

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", start))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
