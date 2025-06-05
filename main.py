import os
import logging
import threading
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# ───── Load ENV ───── #
load_dotenv()  # Use Railway variables or .env in local
TOKEN = os.environ.get("BOT_TOKEN")
GAME_URL = "https://oscurantismo.github.io/gleamorrow/"

if not TOKEN:
    raise ValueError("❌ BOT_TOKEN is missing. Set it in Railway environment variables.")

# ───── Telegram Imports ───── #
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, CallbackQueryHandler, filters
)

# ───── Flask Routes ───── #
from routes.debug_logs import debug_logs
from handling.coin_rewards import coin_rewards
from routes.user import user
from routes.tasks import tasks

# ───── Telegram Bot Handlers ───── #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    first_name = user.first_name if user and user.first_name else "Anonymous"

    await update.message.reply_text(
        f"🌿 Welcome, *{first_name}*, to *Gleamorrow*! Tap below to launch the game:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🌟 Launch Gleamorrow", web_app={"url": GAME_URL})],
            [InlineKeyboardButton("ℹ️ About the Game", callback_data="about")]
        ])
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*About Gleamorrow*\n\n"
        "🧚 *Welcome to Gleamorrow*! I'm Seren, and I will help guide you on this adventure. Gleamorrow is a gamified To-Do List, meaning you get rewards for completing your tasks - just like in videogames!\n\n"
        "*Current Features:*\n"
        "• 🌱 Track your tasks & receive rewards\n"
        "• 🧘‍♀️ Use timers for focus sessions\n"
        "• 🌿 Collect plants and grow your garden\n"
        "• 🎨 Beautiful visuals and hand-drawn art\n\n"
        "*Upcoming Features:*\n"
        "• 🦊 Care for your fox pet\n"
        "• 🛍️ Customise Seren and your space\n"
        "• 🏆 Leaderboard rewards and daily quests\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "about":
        await query.answer()
        await query.message.reply_text(
            "*About Gleamorrow*\n\n"
            "🧚 *Gleamorrow* is a cosy self-care adventure where you grow with Seren.\n\n"
            "*Features:*\n"
            "• 🌱 To-do list + progress tracker\n"
            "• 🧘‍♀️ Built-in timer\n"
            "• 🦊 Fox pet, potions, rewards and more coming soon!",
            parse_mode="Markdown"
        )

async def on_first_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private" and update.message.text:
        await start(update, context)

# ───── Telegram Bot Starter ───── #
def start_telegram_bot():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", start))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, on_first_message))

    app.run_polling()

# ───── Flask App Starter ───── #
def start_flask_app():
    flask_app = Flask(__name__)
    CORS(flask_app, origins=[
        "https://oscurantismo.github.io", 
        "http://localhost:5173"
    ])
    flask_app.register_blueprint(debug_logs)
    flask_app.register_blueprint(coin_rewards)
    flask_app.register_blueprint(user)
    flask_app.register_blueprint(tasks)

    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# ───── Run Both Flask and Telegram ───── #
if __name__ == "__main__":
    threading.Thread(target=start_flask_app).start()
    start_telegram_bot()
