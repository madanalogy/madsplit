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
    response = get_response(chat_id, update.message.text)
    await bot.sendMessage(chat_id=chat_id, text=response)


def get_response(chat_id, text):
    if text.startswith("/start"):
        return INTRO
    if text.startswith("/help"):
        return INSTRUCTIONS
    return ERROR_MSG


TRANSACTION_FORMAT = '''
== Format ==

/add Label, Amount, Payer Name
- Payee Name, [Optional Amount]
- Payee Name, [Optional Amount]
...
'''

EXAMPLES = '''
== Examples ==

/add Dinner, 456, John
- Andy, 123
- Bob, 78

/add Drinks, 654, Bob
- Andy
- John
- Mary
'''

COMMANDS = '''
- /add to add a transaction to the list.
- /list to view the current pending transactions.
- /detail followed by a number from /list to show details of a transaction.
- /delete followed by a number from /list to remove a transaction.
- /settle to settle up all pending transactions. This will remove all transactions.
- /help to bring up the available instructions and format.
'''

EXPLAINER = '''
How it works:
- If a payee's amount is specified in a transaction, that share will first be deducted from the amount.
- The remaining amount will be split amongst all payees that do not have an amount specified.
- The bot will then calculate all relationships between transactions to come up with a final tally.

Tips:
- Make sure the spelling of each name is consitent across transactions. The name is not case sensitive.
- Amounts support up to 2 decimal digits. Any rounding difference in division will go to the payer.
'''

INSTRUCTIONS = '''
${COMMANDS}

${TRANSACTION_FORMAT}

${EXAMPLES}

${EXPLAINER}
'''

INTRO = '''
Hey there, here's how you can use me ;)

${INSTRUCTIONS}
'''

ERROR_MSG = '''
Hey sorry I didn't quite get that. Please see the command list below:

${COMMANDS}
'''

load_dotenv()
