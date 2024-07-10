import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace this with your actual Telegram bot token
TOKEN = '7118549863:AAERm18KSWB00ZGTHIKaglMTU7HlpKikaRY'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi! Use /spam to start spamming "Hello, World!". Use /stop to stop.')

async def spam_hello_world(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Function to send 'Hello, World!' messages."""
    chat_id = context.job.data['chat_id']
    await context.bot.send_message(chat_id=chat_id, text='Hello, World!')

async def start_spamming(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ask the user if they want to start spamming."""
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data='start_spamming'),
            InlineKeyboardButton("No", callback_data='cancel_spamming'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Do you want to start spamming?', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the button press."""
    query = update.callback_query
    await query.answer()
    if query.data == 'start_spamming':
        chat_id = query.message.chat_id
        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(spam_hello_world, interval=1, first=0, data={'chat_id': chat_id}, name=str(chat_id))
        text = 'Started spamming "Hello, World!".' + ('\nRemoved old job.' if job_removed else '')
        await query.edit_message_text(text=text)
    else:
        await query.edit_message_text(text='Spamming canceled.')

async def stop_spamming(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stop spamming 'Hello, World!' messages."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Stopped spamming "Hello, World!".' if job_removed else 'No job to stop.'
    await update.message.reply_text(text)

def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

def main() -> None:
    """Start the bot."""
    application = ApplicationBuilder().token(TOKEN).build()

    # Ensure job_queue is available
    job_queue = application.job_queue

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("spam", start_spamming))
    application.add_handler(CommandHandler("stop", stop_spamming))
    application.add_handler(CallbackQueryHandler(button))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
