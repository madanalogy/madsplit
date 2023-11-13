import constants
import firebase_admin
from firebase_admin import firestore
from collections import deque

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
        debt_each = (amount - running_sum) / (split_count + 1)
        for debtor in owed_amounts:
            if owed_amounts[debtor] == 0:
                owed_amounts[debtor] = debt_each

    transactions = get_transactions(chat_id)
    update_time, trans_ref = transactions.add(details)
    debt_ref = trans_ref.collection("debtors")
    for debtor in owed_amounts:
        debt_ref.add({"name": debtor.lower(), "amount": owed_amounts[debtor]})

    return "Added successfully! Use /list if you want to see all pending transactions"


def run_list(chat_id):
    transactions = get_transactions(chat_id)
    docs = transactions.order_by("timestamp").stream()
    output = "Transaction List\n"
    counter = 1
    for doc in docs:
        doc_dict = doc.to_dict()
        output += f"\n{counter}. {doc_dict['name'].title()}, {doc_dict['amount']}, {doc_dict['payer'].title()}"
        counter += 1

    return output


def run_detail(chat_id, text):
    print("Received detail index:", text)
    if not text or int(text) < 1:
        return constants.ERROR_GENERIC
    transactions = get_transactions(chat_id)
    trans_id, transaction = get_at(transactions, int(text))
    print("Processed trans_id:", trans_id)
    if trans_id == 0:
        return constants.ERROR_SUM_MISMATCH
    output = f"{transaction['name']}, {transaction['amount']}, {transaction['payer']}"
    debtors = transactions.document(trans_id).collection("debtors").stream()
    for debtor in debtors:
        curr = debtor.to_dict()
        amt_str = "{:.2f}".format(round(curr['amount'], 2))
        output += f"\n{curr['name'].title()}, {amt_str}"

    return output


def run_delete(chat_id, text):
    if not text or int(text) < 1:
        return constants.ERROR_GENERIC
    transactions = get_transactions(chat_id)
    trans_id, unused = get_at(transactions, int(text))
    if trans_id == 0:
        return constants.ERROR_SUM_MISMATCH
    debtors = transactions.document(trans_id).collection("debtors")
    debts_ptr = debtors.stream()
    for debtor in debts_ptr:
        debtors.document(debtor.id).delete()
    transactions.document(trans_id).delete()

    return "Deleted successfully! Use /list if you want to see all pending transactions"


def run_settle(chat_id):
    transactions = get_transactions(chat_id)
    trans_ptr = transactions.stream()
    balances = {}
    for trans_ref in trans_ptr:
        debtors = transactions.document(trans_ref.id).collection("debtors")
        debts_ptr = debtors.stream()
        total = 0
        for debt_ref in debts_ptr:
            debt = debt_ref.to_dict()
            if debt['name'] in balances:
                balances[debt['name']] -= debt['amount']
            else:
                balances[debt['name']] = -1 * debt['amount']
            total += debt['amount']
            debtors.document(debt_ref.id).delete()
        transaction = trans_ref.to_dict()
        if transaction['payer'] in balances:
            balances[transaction['payer']] += total
        else:
            balances[transaction['payer']] = total
        transactions.document(trans_ref.id).delete()
    if not balances:
        return constants.ERROR_EMPTY_LIST

    creditors = []
    debtors = []
    for person in balances:
        if balances[person] > 0:
            creditors.append((person, balances[person]))
        elif balances[person] < 0:
            debtors.append((person, abs(balances[person])))
    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda y: y[1])
    debtors = deque(debtors)

    output = {}
    for creditor, amount in creditors:
        curr = amount
        while curr > 0 and len(debtors) > 0:
            debtor, other = debtors.pop()
            if other >= curr:
                value = curr
                if other > curr:
                    debtors.append((debtor, other - curr))
                curr = 0
            else:
                value = other
                curr -= other
            value_str = "{:.2f}".format(round(value, 2))
            if debtor in output:
                output[debtor] += f", Pay {creditor} ${value_str}"
            else:
                output[debtor] = f"Pay {creditor} ${value_str}"
            if creditor in output:
                output[creditor] += f", Get ${value_str} from {debtor}"
            else:
                output[creditor] = f"Get ${value_str} from {debtor}"
    final = "Here's the final tally!\n"
    for person in output:
        final += f"\n{person.title()}: {output[person]}"

    return final


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
    docs = transactions.order_by("timestamp").stream()
    counter = 1
    for doc in docs:
        if index == counter:
            return doc.id, doc.to_dict()
        counter += 1
    return 0, {}
