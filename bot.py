import requests
import os
from datetime import date

import logging

from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)
TOKEN = os.environ.get("TOKEN")
PORT = int(os.environ.get("PORT", "8080"))

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text("Hello World!")


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")


# def stats_command(update: Update, context: CallbackContext) -> None:
#     """Send a message when the command /stats is issued."""
#     # to get eth price from coinmarketcap
#     headers = headers = {
#         "Accepts": "application/json",
#         "X-CMC_PRO_API_KEY": CMC,
#     }
#     r = requests.get(
#         "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest",
#         headers=headers,
#         params={"symbol": "ETH", "convert": "USD"},
#     )

#     if r.status_code == 200:
#         data = r.json()["data"]
#         eth_price = data["ETH"]["quote"]["USD"]["price"]
#     else:
#         result = "Error"
#     r = requests.get("https://beaconcha.in/api/v1/validator/30670")

#     if r.status_code == 200:
#         data = r.json()["data"]
#         timedelta = date.today() - START_DATE
#         days = timedelta.days
#         appreciate = (eth_price - ENTRY_PRICE) / ENTRY_PRICE
#         gains = (data["balance"] - data["effectivebalance"]) / (10 ** 9)
#         cr = gains / 32
#         effective_cr = (1 + cr) * (1 + appreciate)
#         apr = gains / days * 365 / 32
#         effective_apr = (1 + apr) * (1 + appreciate)

#         status = data["status"]
#         status_emoji = ":white_check_mark:" if status == "active_online" else ":x:"

#         slashed = data["slashed"]
#         slashed_emoji = ":white_check_mark:" if not slashed else ":x:"

#         price_emoji = (
#             ":chart_with_upwards_trend:"
#             if appreciate > 0
#             else ":chart_with_downwards_trend:"
#         )
#         fire_emoji = emojize(":fire:", use_aliases=True)
#         rocket_emoji = emojize(":rocket:", use_aliases=True)
#         result = (
#             "Validator: "
#             + str(data["validatorindex"])
#             + "\n"
#             + "Status: "
#             + str(status)
#             + " "
#             + emojize(status_emoji, use_aliases=True)
#             + "\n"
#             + "Slashed: "
#             + str(slashed)
#             + " "
#             + emojize(slashed_emoji, use_aliases=True)
#             + "\n\n"
#             + "Total Balance: "
#             + str(round(data["balance"] / (10 ** 9), 3))
#             + "ETH"
#             + "\n"
#             + "Amount Earned: "
#             + str(round(gains, 3))
#             + "ETH"
#             + "\n"
#             + "Price Change since Entry: "
#             + str(round(appreciate * 100, 2))
#             + "%"
#             + emojize(price_emoji, use_aliases=True)
#             + "\n\n"
#             + "Current Return: "
#             + str(round(cr * 100, 2))
#             + "%"
#             + "\n"
#             + fire_emoji
#             + " Effective Current Return: "
#             + str(round((effective_cr - 1) * 100, 2))
#             + "%"
#             + "\n\n"
#             + "Annualized Return: "
#             + str(round(apr * 100, 2))
#             + "%"
#             + "\n"
#             + rocket_emoji
#             + " Effective Annualized Return: "
#             + str(round((effective_apr - 1) * 100, 2))
#             + "%"
#         )

#     else:
#         result = "Error"
#     update.message.reply_text(result)


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
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

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # add error_handlers
    dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
    updater.bot.setWebhook("https://tradingview-trading-bot.herokuapp.com/" + TOKEN)

    # updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
