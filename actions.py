import firebase_admin
from firebase_admin import firestore

# Application Default credentials are automatically created.
app = firebase_admin.initialize_app()
db = firestore.client()


async def run_add(chat_id, text):
    trans_db = db.collection("chats").document(chat_id).collection("transactions")
    update_time, trans_ref = await trans_db.add(text)
    return f"{trans_ref.id} created on {update_time}"


def run_list(chat_id, text):
    trans_db = db.collection("chats").document(chat_id).collection("transactions")
    docs = trans_db.stream()

    output = ""
    for doc in docs:
        output += f"{doc.id} => {doc.to_dict()}"
    return output


def run_detail(chat_id, text):
    return text


def run_delete(chat_id, text):
    return text


def run_settle(chat_id, text):
    return text
