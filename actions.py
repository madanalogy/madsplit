import firebase_admin
from firebase_admin import firestore


async def get_transactions(chat_id):
    app = firebase_admin.initialize_app()
    db = firestore.client(app)
    return db.collection("chats").document(chat_id).collection("transactions")


async def run_add(chat_id, text):
    transactions = get_transactions(chat_id)
    update_time, trans_ref = await transactions.add(text)
    return f"{trans_ref.id} created on {update_time}"


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
