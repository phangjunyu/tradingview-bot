import requests
import os
from waitress import serve

import time
from flask import Flask, request
import json

from datetime import datetime

from telegram import Bot
from binance.client import Client

PORT = int(os.environ.get("PORT", "8080"))

TOKEN = os.environ.get("TOKEN")
KEY = os.environ.get("KEY")
CHATID = os.environ.get("CHATID")
BINANCE_API_KEY = os.environ.get("BINANCE-API-KEY")
BINANCE_SECRET_KEY = os.environ.get("BINANCE-SECRET-KEY")

now = datetime.now()
timestamp = now.strftime("%Y-%m-%d %X")
app = Flask(__name__)


def binance_report(client):
    update = ""
    for asset in ["BTC", "ETH", "DAI"]:
        _b = client.get_asset_balance(asset)
        update += _b + "\n\n"
    print("update:", update)
    return update


def round_format(string, decimal):
    return str(round(float(string), decimal))


def _readable(b):
    return (
        "Available "
        + b["asset"]
        + ": "
        + round_format(b["free"], 2)
        + "\n"
        + "Locked "
        + b["asset"]
        + ": "
        + round_format(b["locked"], 2)
    )


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
                    tg_bot.sendMessage(data["telegram"], binance_report(client))
                except KeyError:
                    tg_bot.sendMessage(CHATID, data["msg"])
                    tg_bot.sendMessage(CHATID, binance_report(client))
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
    client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
    serve(app, host="0.0.0.0", port=int(PORT))
