import telebot
import os
import requests
from telebot import types
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

BOT_TOKEN = "8759639066:AAEL-GZz07N31r_y1sFLwmPSK6S3hydhZzQ"
GROQ_API_KEY = "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"

bot = telebot.TeleBot(BOT_TOKEN)

# {user_id: {"direction": "uch_tosh" yoki "tosh_uch" yoki None}}
users = {}

def check_with_ai(message_text, direction):
    if direction == "uch_tosh":
        topic = "Uchqo'rg'ondan Toshkentga taksi, yo'lovchi, mashina"
    else:
        topic = "Toshkentdan Uchqo'rg'onga taksi, yo'lovchi, mashina"

    prompt = f"""Quyidagi xabar shu mavzuga to'g'ri keladimi?

Mavzu: {topic}

Xabar: {message_text}

Faqat "ha" yoki "yo'q" deb javob ber."""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 10
            },
            timeout=10
        )
        result = response.json()
        answer = result["choices"][0]["message"]["content"].strip().lower()
        return "ha" in answer
    except:
        return False

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🚗 Uchqo'rg'on → Toshkent")
    btn2 = types.KeyboardButton("🚗 Toshkent → Uchqo'rg'on")
    btn3 = types.KeyboardButton("⛔ Kuzatishni to'xtatish")
    markup.add(btn1, btn2)
    markup.add(btn3)
    return markup

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot ishlayapti!")
    def log_message(self, format, *args):
        pass

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

@bot.message_handler(commands=["start"])
def start(message):
    if message.chat.type != "private":
        return
    user_id = message.from_user.id
    users[user_id] = {"direction": None}
    bot.send_message(user_id,
        "👋 Salom! Qaysi yo'nalishni kuzatmoqchisiz?",
        reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.chat.type == "private" and m.text == "🚗 Uchqo'rg'on → Toshkent")
def set_uch_tosh(message):
    user_id = message.from_user.id
    if user_id not in users:
        users[user_id] = {}
    users[user_id]["direction"] = "uch_tosh"
    bot.send_message(user_id,
        "✅ Uchqo'rg'on → Toshkent yo'nalishi kuzatilmoqda!\n\n"
        "Guruxda mos xabar chiqsa darhol xabar beraman 📩",
        reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.chat.type == "private" and m.text == "🚗 Toshkent → Uchqo'rg'on")
def set_tosh_uch(message):
    user_id = message.from_user.id
    if user_id not in users:
        users[user_id] = {}
    users[user_id]["direction"] = "tosh_uch"
    bot.send_message(user_id,
        "✅ Toshkent → Uchqo'rg'on yo'nalishi kuzatilmoqda!\n\n"
        "Guruxda mos xabar chiqsa darhol xabar beraman 📩",
        reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.chat.type == "private" and m.text == "⛔ Kuzatishni to'xtatish")
def stop_watching(message):
    user_id = message.from_user.id
    if user_id in users:
        users[user_id]["direction"] = None
    bot.send_message(user_id,
        "⛔ Kuzatish to'xtatildi.",
        reply_markup=main_menu())

@bot.message_handler(
    func=lambda m: m.chat.type in ["group", "supergroup"] and m.text,
    content_types=["text"]
)
def handle_group(message):
    if len(message.text) < 5:
        return
    for user_id, data in users.items():
        direction = data.get("direction")
        if not direction:
            continue
        if check_with_ai(message.text, direction):
            group_name = message.chat.title or "Gurux"
            sender = message.from_user
            sender_name = f"@{sender.username}" if sender.username else sender.first_name
            msg_link = ""
            if message.chat.type == "supergroup":
                chat_id_str = str(message.chat.id).replace("-100", "")
                msg_link = f"\n🔗 Xabarga o'tish: https://t.me/c/{chat_id_str}/{message.message_id}"
            
            direction_text = "Uchqo'rg'on → Toshkent" if direction == "uch_tosh" else "Toshkent → Uchqo'rg'on"
            
            bot.send_message(user_id,
                f"🔔 Mos xabar topildi!\n\n"
                f"📍 Yo'nalish: {direction_text}\n"
                f"👥 Gurux: {group_name}\n"
                f"👤 Kim yozdi: {sender_name}\n\n"
                f"💬 Xabar:\n{message.text}" + msg_link)

print("✅ Bot ishga tushdi...")
threading.Thread(target=run_server, daemon=True).start()
bot.infinity_polling()
