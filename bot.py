import requests
import os
from waitress import serve

import time
from flask import Flask, request
import json

from datetime import datetime
import logging

from telegram import Bot
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)
from binance.client import Client
from binance.enums import *


PORT = int(os.environ.get("PORT", "8080"))

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)
TOKEN = os.environ.get("TOKEN")
KEY = os.environ.get("KEY")
CHATID = os.environ.get("CHATID")
BINANCE_API_KEY = os.environ.get("BINANCE-API-KEY")
BINANCE_SECRET_KEY = os.environ.get("BINANCE-SECRET-KEY")

now = datetime.now()
timestamp = now.strftime("%Y-%m-%d %X")
app = Flask(__name__)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text("Hi!")


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def main():
    serve(app, host="0.0.0.0", port=int(PORT))

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("test_order", test_order_command))

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # add error_handlers
    dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
    updater.bot.setWebhook("https://tradingview-trading-bot.herokuapp.com/" + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

    @app.route("/webhook", methods=["POST", "GET"])
    def webhook():
        try:
            if request.method == "POST":
                data = request.get_json()
                key = data["key"]
                if key == KEY:
                    print(timestamp, "Alert Received & Sent!")
                    tg_bot = Bot(token=TOKEN)
                    try:
                        tg_bot.sendMessage(data["telegram"], data["msg"])
                    except KeyError:
                        tg_bot.sendMessage(CHATID, data["msg"])
                    except Exception as e:
                        print("[X] Telegram Error:\n>", e)
                    return "Sent alert", 200

                else:
                    print("[X]", timestamp, "Alert Received & Refused! (Wrong Key)")
                    return "Refused alert", 400
            if request.method == "GET":
                return "OK", 200

        except Exception as e:
            print("[X]", timestamp, "Error:\n>", e)
            return "Error", 400


client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

if __name__ == "__main__":
    main()
