from telegram import Update, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "BOT_TOKEN"
GAME_SHORT_NAME = "gleamorrow"  # Must be registered with BotFather
GAME_URL = "https://oscurantismo.github.io/gleamorrow/"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_game(
        game_short_name=GAME_SHORT_NAME,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Play Game", callback_game={"game_short_name": GAME_SHORT_NAME})]
        ])
    )

async def game_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(url=GAME_URL)  # Opens the game

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", start))
    app.add_handler(CommandHandler("help", start))  # Optional
    app.add_handler(CommandHandler(GAME_SHORT_NAME, start))

    from telegram.ext import CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(game_callback, pattern="^" + GAME_SHORT_NAME + "$"))

    app.run_polling()
