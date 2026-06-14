import telebot
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8759639066:AAEL-GZz07N31r_y1sFLwmPSK6S3hydhZzQ")

bot = telebot.TeleBot(BOT_TOKEN)
users = {}

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
    users[user_id] = {"keywords": [], "step": ""}
    bot.send_message(user_id,
        "👋 Salom! Men guruxdagi xabarlarni kuzataman.\n\n"
        "📌 Kalit so'zlarni belgilash uchun /setkeywords buyrug'ini yuboring.")

@bot.message_handler(commands=["setkeywords"])
def set_keywords(message):
    if message.chat.type != "private":
        return
    user_id = message.from_user.id
    if user_id not in users:
        users[user_id] = {"keywords": [], "step": ""}
    users[user_id]["step"] = "waiting_keywords"
    bot.send_message(user_id,
        "✏️ Kalit so'zlarni kiriting (vergul bilan ajrating):\n\n"
        "Misol: ish, vakansiya, ishga qabul",
        parse_mode="Markdown")

@bot.message_handler(commands=["mykeywords"])
def my_keywords(message):
    if message.chat.type != "private":
        return
    user_id = message.from_user.id
    kw = users.get(user_id, {}).get("keywords", [])
    if kw:
        bot.send_message(user_id, "📋 Sizning kalit so'zlaringiz:\n\n" + "\n".join(f"• {k}" for k in kw))
    else:
        bot.send_message(user_id, "❌ Kalit so'z yo'q. /setkeywords orqali belgilang.")

@bot.message_handler(commands=["clear"])
def clear_keywords(message):
    if message.chat.type != "private":
        return
    user_id = message.from_user.id
    if user_id in users:
        users[user_id]["keywords"] = []
    bot.send_message(user_id, "🗑 Kalit so'zlar o'chirildi.")

@bot.message_handler(commands=["help"])
def help_cmd(message):
    if message.chat.type != "private":
        return
    bot.send_message(message.chat.id,
        "📖 Buyruqlar:\n\n"
        "/setkeywords — kalit so'zlarni belgilash\n"
        "/mykeywords — mavjud kalit so'zlarni ko'rish\n"
        "/clear — kalit so'zlarni o'chirish\n"
        "/help — yordam")

@bot.message_handler(func=lambda m: m.chat.type == "private")
def handle_private(message):
    user_id = message.from_user.id
    user = users.get(user_id, {})
    if user.get("step") == "waiting_keywords":
        keywords = [k.strip().lower() for k in message.text.split(",") if k.strip()]
        users[user_id]["keywords"] = keywords
        users[user_id]["step"] = ""
        bot.send_message(user_id,
            f"✅ Saqlandi! {len(keywords)} ta kalit so'z:\n\n" + "\n".join(f"• {k}" for k in keywords))
    else:
        bot.send_message(user_id, "ℹ️ /help — buyruqlar ro'yxati")

@bot.message_handler(
    func=lambda m: m.chat.type in ["group", "supergroup"] and m.text,
    content_types=["text"]
)
def handle_group(message):
    text_lower = message.text.lower()
    sender = message.from_user
    for user_id, data in users.items():
        keywords = data.get("keywords", [])
        matched = [kw for kw in keywords if kw in text_lower]
        if matched:
            group_name = message.chat.title or "Gurux"
            sender_name = f"@{sender.username}" if sender.username else sender.first_name
            msg_link = ""
            if message.chat.type == "supergroup":
                chat_id_str = str(message.chat.id).replace("-100", "")
                msg_link = f"\n🔗 Xabarga o'tish: https://t.me/c/{chat_id_str}/{message.message_id}"
            bot.send_message(user_id,
                f"🔔 Kalit so'z topildi!\n\n"
                f"👥 Gurux: {group_name}\n"
                f"👤 Kim yozdi: {sender_name}\n"
                f"🏷 Kalit so'z: {', '.join(matched)}\n\n"
                f"💬 Xabar:\n{message.text}" + msg_link)

print("✅ Bot ishga tushdi...")
threading.Thread(target=run_server, daemon=True).start()
bot.infinity_polling()
