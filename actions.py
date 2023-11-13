import constants
import firebase_admin
from firebase_admin import firestore
app = firebase_admin.initialize_app()
db = firestore.client()


def get_transactions(chat_id):
    return db.collection("chats").document(str(chat_id)).collection("transactions")


async def run_add(chat_id, text):
    lines = text.split("\n")
    if len(lines) < 2:
        return constants.ERROR_ADD_FORMAT
    core = lines[0].split(",")
    if len(core) != 3:
        return constants.ERROR_ADD_FORMAT
    amount = core[1].strip()
    if not is_valid_amount(amount):
        print("Detected not valid amount: ", amount)
        return constants.ERROR_PRECONDITION
    details = {
        "name": core[0].strip().lower(),
        "amount": float(amount),
        "payer": core[2].strip().lower(),
    }
    
    owed_amount = {}
    for line in lines[1:]:
        parsed = line.split(",")
        if not parsed or len(parsed) > 2:
            return constants.ERROR_ADD_FORMAT
        if len(parsed) == 2 and not is_valid_amount(parsed[1]):
            print("Detected not valid amount: ", parsed[1])
            return constants.ERROR_PRECONDITION
        if len(parsed) == 2:
            owed_amount[parsed[0].strip()] = float(parsed[1])
        else:
            owed_amount[parsed[0].strip()] = -1

    transactions = get_transactions(chat_id)
    update_time, trans_ref = await transactions.add(details)
    debt_ref = trans_ref.collection("debtors")
    for debtor in owed_amount:
        await debt_ref.document(debtor).add({"name": debtor, "amount": owed_amount[debtor]})

    return "Added successfully! Use /list if you want to see all pending transactions"


async def run_list(chat_id, text):
    transactions = get_transactions(chat_id)
    docs = transactions.stream()
    parsed_transactions = []
    for doc in docs:
        parsed_transactions.append(doc)
    if len(parsed_transactions) == 0:
        return constants.ERROR_EMPTY_LIST
    parsed_transactions.sort(key=lambda x: x.update_time)
    
    output = "SN. Name, Amount, Payer"
    counter = 1
    for transaction in parsed_transactions:
        output += f"\n{counter}. {transaction.name}, {transaction.amount}, {transaction.payer}"
        counter += 1

    return output


async def run_detail(chat_id, text):
    transactions = get_transactions(chat_id)
    to_get = get_at(transactions, text.strip())

    output = f"{to_get.name}, {to_get.amount}, {to_get.payer}"
    debtors = transactions.document(to_get.id).collection("debtors")
    for debtor in debtors:
        output += f"\n{debtor.name}"
        if debtor.amount:
            output += f", {debtor.amount}"

    return output


async def run_delete(chat_id, text):
    transactions = get_transactions(chat_id)
    to_get = get_at(transactions, text.strip())
    debtors = transactions.document(to_get.id).collection("debtors")
    docs = debtors.stream()
    for doc in docs:
        await doc.delete()
    await transactions.document(to_get.id).delete()
    return "Deleted successfully! Use /list if you want to see all pending transactions"


async def run_settle(chat_id, text):
    transactions = get_transactions(chat_id)

    return "TODO"


def is_valid_amount(value):
    if not value:
        return False
    decimals = value.split(".")
    if len(decimals) == 1:
        return value.isnumeric() and float(value) > 0
    if len(decimals) == 2:
        return decimals[0].isnumeric() and len(decimals[1]) <= 2 and decimals[1].isnumeric() and float(value) > 0
    return False


def get_at(transactions, index):
    if not index or not index.isnumeric():
        return None
    sn = int(index)
    if sn < 1:
        return None
    docs = transactions.stream()
    parsed_transactions = []
    for doc in docs:
        parsed_transactions.append(doc)
    if len(parsed_transactions) > sn:
        return None
    parsed_transactions.sort(key=lambda x: x.update_time)
    return parsed_transactions[sn]