import constants
import firebase_admin
from firebase_admin import firestore
app = firebase_admin.initialize_app()
db = firestore.client()


def get_transactions(chat_id):
    return db.collection("chats").document(str(chat_id)).collection("transactions")


async def run_add(chat_id, text):
    transactions = get_transactions(chat_id)
    lines = text.split("\n")
    if len(lines) < 2:
        return constants.ERROR_PRECONDITION
    core = lines[0].split(",")
    if len(core) != 3:
        return constants.ERROR_ADD_FORMAT
    amount = core[1].strip()
    if not is_valid_amount(amount):
        return constants.ERROR_PRECONDITION
    details = {
        "name": core[0].strip().lower(),
        "amount": float(amount),
        "payer": core[2].strip().lower(),
    }
    
    debtors = {}
    for line in lines[1:]:
        parsed = line.split(",")
        if not parsed or len(parsed) > 2:
            return constants.ERROR_ADD_FORMAT
        if len(parsed) == 2 and not is_valid_amount(parsed[1]):
            return constants.ERROR_PRECONDITION
        if len(parsed) == 2:
            debtors[parsed[0].strip()] = float(parsed[1])
        else:
            debtors[parsed[0].strip()] = -1

    update_time, trans_ref = await transactions.add(details)
    debt_ref = trans_ref.collection("debtors")
    for debtor in debtors:
        await debt_ref.document(debtor).set({"amount": debtors[debtor]})

    return "Added successfully! Use /list if you want to see all pending transactions"


def get_time(transaction):
    return transaction.update_time


async def run_list(chat_id, text):
    transactions = get_transactions(chat_id)
    docs = transactions.stream()
    parsed_transactions = []
    for doc in docs:
        parsed_transactions.append(doc)
    parsed_transactions.sort(key=get_time)

    output = "SN. Name, Amount, Payer"
    counter = 1
    for transaction in parsed_transactions:
        output += f"\n{counter}. {transaction.name}, {transaction.amount}, {transaction.payer}"
        counter += 1
    return output


async def run_detail(chat_id, text):
    transactions = get_transactions(chat_id)
    if not text or not text.strip().isnumeric():
        return constants.ERROR_GENERIC
    sn = int(text.strip())
    docs = transactions.stream()
    parsed_transactions = []
    for doc in docs:
        parsed_transactions.append(doc)
    if len(parsed_transactions) > sn:
        return constants.ERROR_GENERIC
    parsed_transactions.sort(key=get_time)
    to_get = parsed_transactions[sn]

    output = f"{to_get.name}, {to_get.amount}, {to_get.payer}"
    debtors = transactions.document(to_get.id).collection("debtors")
    for debtor in debtors:
        output += f"\n{debtor.name}"
        if debtor.amount:
            output += f", {debtor.amount}"

    return output


async def run_delete(chat_id, text):
    return "TODO"


async def run_settle(chat_id, text):
    return "TODO"


def is_valid_amount(value):
    if not value:
        return False
    decimals = value.split(".")
    if len(decimals) == 1:
        return value.isnumeric() and float(value) > 0
    if len(decimals) == 2:
        return decimals[0].isnumeric() and len(decimals[1]) == 2 and decimals[1].isnumeric() and float(value) > 0
    return False
