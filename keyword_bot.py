
import telebot
import os
from telebot import types
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

BOT_TOKEN = "8759639066:AAEL-GZz07N31r_y1sFLwmPSK6S3hydhZzQ"

bot = telebot.TeleBot(BOT_TOKEN)
users = {}

UCH_TOSH = ["uchqo'rg'on toshkent", "uchqurgon toshkent", "uchqo'rg'ondan toshkent", "uchqo'rg'on → toshkent"]
TOSH_UCH = ["toshkent uchqo'rg'on", "toshkent uchqurgon", "toshkentdan uchqo'rg'on", "toshkent → uchqo'rg'on"]

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🚗 Uchqo'rg'on → Toshkent"))
    markup.add(types.KeyboardButton("🚗 Toshkent → Uchqo'rg'on"))
    markup.add(types.KeyboardButton("⛔ Kuzatishni to'xtatish"))
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
    users[message.from_user.id] = {"direction": "uch_tosh"}
    bot.send_message(message.from_user.id,
        "✅ Uchqo'rg'on → Toshkent kuzatilmoqda!",
        reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.chat.type == "private" and m.text == "🚗 Toshkent → Uchqo'rg'on")
def set_tosh_uch(message):
    users[message.from_user.id] = {"direction": "tosh_uch"}
    bot.send_message(message.from_user.id,
        "✅ Toshkent → Uchqo'rg'on kuzatilmoqda!",
        reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.chat.type == "private" and m.text == "⛔ Kuzatishni to'xtatish")
def stop(message):
    users[message.from_user.id] = {"direction": None}
    bot.send_message(message.from_user.id, "⛔ Kuzatish to'xtatildi.", reply_markup=main_menu())

@bot.message_handler(
    func=lambda m: m.chat.type in ["group", "supergroup"] and m.text,
    content_types=["text"]
)
def handle_group(message):
    text = message.text.lower()
    for user_id, data in users.items():
        direction = data.get("direction")
        if not direction:
            continue
        keywords = UCH_TOSH if direction == "uch_tosh" else TOSH_UCH
        if any(kw in text for kw in keywords):
            sender = message.from_user
            sender_name = f"@{sender.username}" if sender.username else sender.first_name
            group_name = message.chat.title or "Gurux"
            msg_link = ""
            if message.chat.type == "supergroup":
                chat_id_str = str(message.chat.id).replace("-100", "")
                msg_link = f"\n🔗 https://t.me/c/{chat_id_str}/{message.message_id}"
            bot.send_message(user_id,
                f"🔔 Mos xabar topildi!\n\n"
                f"👥 {group_name}\n"
                f"👤 {sender_name}\n\n"
                f"💬 {message.text}" + msg_link)

print("✅ Bot ishga tushdi...")
threading.Thread(target=run_server, daemon=True).start()
bot.infinity_polling()
