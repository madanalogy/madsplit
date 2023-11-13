import constants
import firebase_admin
from firebase_admin import firestore
app = firebase_admin.initialize_app()
db = firestore.client()


def get_transactions(chat_id):
    return db.collection("chats").document(str(chat_id)).collection("transactions")


def run_add(chat_id, text):
    lines = text.split("\n")
    if len(lines) < 2:
        return constants.ERROR_ADD_FORMAT
    core = lines[0].split(",")
    if len(core) != 3:
        return constants.ERROR_ADD_FORMAT
    amount = core[1].strip()
    if not is_valid_amount(amount):
        return constants.ERROR_PRECONDITION
    amount = float(amount)
    details = {
        "name": core[0].strip().lower(),
        "amount": amount,
        "payer": core[2].strip().lower(),
        "timestamp": firestore.SERVER_TIMESTAMP
    }
    
    owed_amounts = {}
    split_count = 0
    running_sum = float(0)
    for line in lines[1:]:
        parsed = line.split(",")
        if not parsed or len(parsed) > 2:
            return constants.ERROR_ADD_FORMAT
        if len(parsed) == 2:
            owed = parsed[1].strip()
            if not is_valid_amount(owed):
                return constants.ERROR_PRECONDITION
            owed = float(owed)
            owed_amounts[parsed[0].strip()] = owed
            running_sum += owed
        else:
            owed_amounts[parsed[0].strip()] = 0
            split_count += 1
    if running_sum > amount:
        return constants.ERROR_SUM_MISMATCH
    if running_sum == amount and split_count != 0:
        return constants.ERROR_SUM_MISMATCH
    if split_count != 0:
        debt_each = (amount-running_sum)/(split_count + 1)
        for debtor in owed_amounts:
            if owed_amounts[debtor] == 0:
                owed_amounts[debtor] = debt_each
    

    transactions = get_transactions(chat_id)
    update_time, trans_ref = transactions.add(details)
    debt_ref = trans_ref.collection("debtors")
    for debtor in owed_amounts:
        debt_ref.add({"name": debtor, "amount": owed_amounts[debtor]})

    return "Added successfully! Use /list if you want to see all pending transactions"


def run_list(chat_id, text):
    transactions = get_transactions(chat_id)
    docs = transactions.stream()
    parsed_transactions = []
    for doc in docs:
        parsed_transactions.append(doc.to_dict())
    if len(parsed_transactions) == 0:
        return constants.ERROR_EMPTY_LIST
    parsed_transactions.sort(key=lambda x: x.timestamp)
    
    output = "SN. Name, Amount, Payer"
    counter = 1
    for transaction in parsed_transactions:
        output += f"\n{counter}. {transaction.name}, {transaction.amount}, {transaction.payer}"
        counter += 1

    return output


def run_detail(chat_id, text):
    transactions = get_transactions(chat_id)
    to_get = get_at(transactions, text.strip())

    output = f"{to_get.name}, {to_get.amount}, {to_get.payer}"
    debtors = transactions.document(to_get.id).collection("debtors")
    for debtor in debtors:
        output += f"\n{debtor.name}, {debtor.amount}"

    return output


def run_delete(chat_id, text):
    transactions = get_transactions(chat_id)
    to_get = get_at(transactions, text.strip())
    debtors = transactions.document(to_get.id).collection("debtors")
    docs = debtors.stream()
    for doc in docs:
        doc.delete()
    transactions.document(to_get.id).delete()
    return "Deleted successfully! Use /list if you want to see all pending transactions"


def run_settle(chat_id, text):
    transactions = get_transactions(chat_id)
    trans_ptr = transactions.stream()
    balances = {}
    for ref in trans_ptr:
        transaction = ref.to_dict()
        balances[transaction.payer] += transaction.amount
        debtors = transaction.collection("debtors")
        debts_ptr = debtors.stream()
        for debt in debts_ptr:
            balances[debt.name] -= debt.amount
    print(balances)
    creditors = []
    debtors = []
    for person in balances:
        if balances[person] > 0:
            creditors.append((person, balances[person]))
        elif balances < 0:
            debtors.append((person, abs(balances[person])))
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
    if not index or not index.isnumeric() or int(index) < 1:
        return None
    sn = int(index)
    docs = transactions.stream()
    parsed_transactions = []
    for doc in docs:
        parsed_transactions.append(doc.to_dict())
    if len(parsed_transactions) > sn:
        return None
    parsed_transactions.sort(key=lambda x: x.timestamp)
    return parsed_transactions[sn-1]