import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = os.environ.get("BOT_TOKEN")
GAME_URL = "https://oscurantismo.github.io/gleamorrow/"

if not TOKEN:
    raise ValueError("BOT_TOKEN is missing. Please set it in Railway environment variables.")

# /start and /play command
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


# /about command or button
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

# Handle inline button "About"
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "about":
        await query.answer()  # remove loading
        await query.message.reply_text(
            "*About Gleamorrow*\n\n"
            "🧚 *Gleamorrow* is a cosy self-care adventure where you grow with Seren.\n\n"
            "*Features:*\n"
            "• 🌱 To-do list + progress tracker\n"
            "• 🧘‍♀️ Built-in timer\n"
            "• 🦊 Fox pet, potions, rewards and more coming soon!",
            parse_mode="Markdown"
        )

# Simulate /start on first message
async def on_first_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private" and update.message.text:
        await start(update, context)

def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", start))
    app.add_handler(CommandHandler("about", about))

    # Button callbacks
    from telegram.ext import CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(handle_callback))

    # Auto-start on first user text message
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, on_first_message))

    app.run_polling()

if __name__ == "__main__":
    main()
