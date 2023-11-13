from dotenv import load_dotenv
import asyncio
import os
import functions_framework
import telegram
import constants
import actions


@functions_framework.http
def webhook(request):
    # Set CORS headers for the preflight request
    if request.method == "OPTIONS":
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for 3600s
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        }

        return "", 204, headers

    if request.method == "POST":
        asyncio.run(process(request))

    # Set CORS headers for the main request
    headers = {"Access-Control-Allow-Origin": "*"}

    return "OK", 200, headers


async def process(request):
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    bot = telegram.Bot(token=BOT_TOKEN)
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    print(f"Received update: {update}")
    if not update or not update.message or not update.message.chat or not update.message.chat.id:
        return
    chat_id = update.message.chat.id
    response = get_response(chat_id, update.message.text)
    await bot.sendMessage(chat_id=chat_id, text=response)


def get_response(chat_id, text):
    print(f"Received message: {text}")
    if not text:
        return
    if text.startswith("/start"):
        return constants.INTRO
    if text.startswith("/add"):
        return actions.run_add(chat_id, text[len("/add"):])
    if text.startswith("/list"):
        return actions.run_list(chat_id)
    if text.startswith("/detail"):
        return actions.run_detail(chat_id, text[len("/detail"):])
    if text.startswith("/delete"):
        return actions.run_delete(chat_id, text[len("/delete"):])
    if text.startswith("/settle"):
        return actions.run_settle(chat_id)
    if text.startswith("/help"):
        return constants.INTRO
    return constants.ERROR_GENERIC


load_dotenv()
