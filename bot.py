import requests
import os
from waitress import serve

import time
from flask import Flask, request
import json

from datetime import datetime
import logging
import sys

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
    print("echo?")
    update.message.reply_text(update.message.text)


def test_order_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text("Test Order")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def setup(token):
    # Create bot, update queue and dispatcher instances
    bot = Bot(token)

    dispatcher = Dispatcher(bot, None, workers=0)

    ##### Register handlers here #####
    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("test_order", test_order_command))

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # add error_handlers
    dispatcher.add_error_handler(error)

    return dispatcher
    # you might want to return dispatcher as well,
    # to stop it at server shutdown, or to register more handlers:
    # return (update_queue, dispatcher)


@app.route("/<string:param>", methods=["POST", "GET"])
def tele_message(param):
    if param == TOKEN:
        try:
            if request.method == "POST":
                data = request.get_json()
                # do verification check here
                print("here1")
                dispatcher.process_update(data)
                print("here2")
                return "Message received", 200
            if request.method == "GET":
                return "HELLO WORLD", 200

        except Exception as e:
            print("[X]", timestamp, "Error:\n>", e)
            return "Error", 400
    if param == "webhook":
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


if __name__ == "__main__":
    dispatcher = setup(token=TOKEN)
    serve(app, host="0.0.0.0", port=int(PORT))

    client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
