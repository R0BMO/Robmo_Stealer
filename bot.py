import telegram
from telegram.ext import Updater, CommandHandler

def start(update, context):
    user = update.effective_user
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Hello {user.first_name}!")

def main():
    # Crea un objeto bot con tu token
    bot = telegram.Bot(token='6650505242:AAHtEQdkIvxn5PoWaKsSTIBeZRd7xrZGpnI')

    # Crea un Updater y pásale el objeto bot
    updater = Updater(bot=bot, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
