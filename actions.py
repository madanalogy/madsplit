import constants


def get_transactions(chat_id):
    import firebase_admin
    from firebase_admin import firestore
    app = firebase_admin.initialize_app()
    db = firestore.client(app)
    return db.collection("chats").document(chat_id).collection("transactions")


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


async def run_list(chat_id, text):
    transactions = get_transactions(chat_id)
    docs = transactions.stream()

    output = ""
    for doc in docs:
        output += f"{doc.id} => {doc.to_dict()}"
    return output


async def run_detail(chat_id, text):
    return text


async def run_delete(chat_id, text):
    return text


async def run_settle(chat_id, text):
    return text


def is_valid_amount(value):
    if not value:
        return False
    decimals = value.split(".")
    if len(decimals) == 1:
        return value.isnumeric() and float(value) > 0
    if len(decimals) == 2:
        return decimals[0].isnumeric() and len(decimals[1]) == 2 and decimals[1].isnumeric() and float(value) > 0
    return False
