import os
import json
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

CHAT_DIR = "chat_storage"
os.makedirs(CHAT_DIR, exist_ok=True)

def list_chats():
    files = [f for f in os.listdir(CHAT_DIR) if f.endswith('.json')]
    chats = []
    for f in files:
        try:
            with open(os.path.join(CHAT_DIR, f), "r", encoding="utf-8") as file:
                data = json.load(file)
                timestamp = data["timestamp"]
                chat_id = f.replace(".json", "")
                title = data["messages"][0]["content"] if data["messages"] else "Senza titolo"
                chats.append({"id": chat_id, "timestamp": timestamp, "title": title})
        except Exception:
            continue
    chats.sort(key=lambda x: x["timestamp"], reverse=True)
    return chats

@app.route("/")
def index():
    chats = list_chats()
    return render_template("index.html", chats=chats)

@app.route("/chat/<chat_id>")
def load_chat(chat_id):
    file_path = os.path.join(CHAT_DIR, f"{chat_id}.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            chat_data = json.load(file)
    else:
        chat_data = {
            "id": chat_id,
            "timestamp": datetime.now().isoformat(),
            "messages": []
        }
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(chat_data, file, ensure_ascii=False, indent=2)
    chats = list_chats()
    return render_template("index.html", chats=chats, active_chat=chat_data)

@app.route("/new_chat", methods=["POST"])
def new_chat():
    chat_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    new_chat_data = {
        "id": chat_id,
        "timestamp": timestamp,
        "messages": []
    }
    with open(os.path.join(CHAT_DIR, f"{chat_id}.json"), "w", encoding="utf-8") as file:
        json.dump(new_chat_data, file, ensure_ascii=False, indent=2)
    return redirect(url_for("load_chat", chat_id=chat_id))

@app.route("/delete_chat/<chat_id>", methods=["POST"])
def delete_chat(chat_id):
    file_path = os.path.join(CHAT_DIR, f"{chat_id}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for("index"))

@app.route("/send_message/<chat_id>", methods=["POST"])
def send_message(chat_id):
    user_message = request.form["message"]
    ai_response = generate_ai_response(user_message)

    file_path = os.path.join(CHAT_DIR, f"{chat_id}.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            chat_data = json.load(file)
    else:
        chat_data = {
            "id": chat_id,
            "timestamp": datetime.now().isoformat(),
            "messages": []
        }

    chat_data["messages"].append({"role": "user", "content": user_message})
    chat_data["messages"].append({"role": "ai", "content": ai_response})

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(chat_data, file, ensure_ascii=False, indent=2)

    return redirect(url_for("load_chat", chat_id=chat_id))

def generate_ai_response(message):
    return "¡Hola! Come stai? Spero che tu abbia un bel giorno! Se hai bisogno di una mano con qualcosa, specialmente per quanto riguarda la finanza, sono qui per aiutarti. Non esitare a chiedere!"

if __name__ == "__main__":
    app.run(debug=True)
