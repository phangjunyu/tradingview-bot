import requests
import os
from waitress import serve

import time
from flask import Flask, request
import json

from datetime import datetime

from telegram import Bot

PORT = int(os.environ.get("PORT", "8080"))

TOKEN = os.environ.get("TOKEN")
KEY = os.environ.get("KEY")
CHATID = os.environ.get("CHATID")
TD_TOKEN = os.environ.get("TD-TOKEN")

now = datetime.now()
timestamp = now.strftime("%Y-%m-%d %X")
app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        if request.method == "POST":
            data = request.get_json()
            key = data["key"]
            if key == KEY:
                print(timestamp, "Alert Received & Sent!")
                tg_bot = Bot(token=TOKEN)
                try:
                    msg = (
                        "Order "
                        + data["action"]
                        + "/n"
                        + data["qty"]
                        + " of "
                        + data["ticker"]
                        + ". Current Position is "
                        + data["position"]
                    )
                    tg_bot.sendMessage(data["telegram"], msg)
                except KeyError:
                    msg = (
                        "Order "
                        + data["action"]
                        + "/n"
                        + data["qty"]
                        + " of "
                        + data["ticker"]
                        + ". Current Position is "
                        + data["position"]
                    )
                    tg_bot.sendMessage(CHATID, data["msg"])
                except Exception as e:
                    print("[X] Telegram Error:\n>", e)
                return "Sent alert", 200

            else:
                print("[X]", timestamp, "Alert Received & Refused! (Wrong Key)")
                return "Refused alert", 400

    except Exception as e:
        print("[X]", timestamp, "Error:\n>", e)
        return "Error", 400


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=int(PORT))
