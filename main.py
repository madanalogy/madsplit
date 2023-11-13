from dotenv import load_dotenv
import asyncio
import os
import functions_framework
import telegram


@functions_framework.http
def webhook(request):
    # Set CORS headers for the preflight request
    if request.method == "OPTIONS":
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
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
    chat_id = update.message.chat.id
    response = get_response(update.message.text)
    await bot.sendMessage(chat_id=chat_id, text=response)


def get_response(text):
    lines = text.split("\n")
    if lines[0].startswith("/start"):
        return "Hey there :)"
    if lines[0].startswith("/add"):
        return entry
    return text


commands = '''

'''

entry = '''
== Format ==

Expense Name, Amount, Payer
- Name 1, [Optional Amount]
- Name 2, [Optional Amount]
...

== Examples ==

Dinner at Wendy's, 456, John
- Andy, 123
- Bob, 78

Drinks at Harry's, 654, Bob
- Andy
- John
- Mary

'''

load_dotenv()
