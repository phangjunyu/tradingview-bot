import requests
import os
from waitress import serve

import time
from flask import Flask, request
import json

from datetime import datetime
import logging

from queue import Queue
from threading import Thread
from telegram import Bot
from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    Dispatcher,
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


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text("Test Order")


def setup(token):
    # Create bot, update queue and dispatcher instances
    bot = Bot(token)
    update_queue = Queue()

    dispatcher = Dispatcher(bot, update_queue)

    ##### Register handlers here #####
    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("test_order", test_order_command))

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # add error_handlers
    dispatcher.add_error_handler(error)

    # Start the thread
    thread = Thread(target=dispatcher.start, name="dispatcher")
    thread.start()

    return update_queue, dispatcher
    # you might want to return dispatcher as well,
    # to stop it at server shutdown, or to register more handlers:
    # return (update_queue, dispatcher)


def webhook(update):
    update_queue.put(update)


def main():
    update_queue, dispatcher = setup(token=TOKEN)
    serve(app, host="0.0.0.0", port=int(PORT))

    @app.route("/webhook", methods=["POST", "GET"])
    def webhook():
        try:
            if request.method == "POST":
                data = request.get_json()
                key = data["key"]
                if key == KEY:
                    print(timestamp, "Alert Received & Sent!")

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
