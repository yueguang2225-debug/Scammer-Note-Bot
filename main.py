import logging
import json
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Admin ရဲ့ Telegram User ID
ADMIN_ID = 8012437507

# ဒေတာများ သိမ်းဆည်းမည့် JSON ဖိုင်များ
USERS_FILE = "users.json"
DATA_FILE = "responses.json"

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def load_json(filename, default_val):
    """JSON ဖိုင်မှ ဒေတာများ ဖတ်ယူခြင်း"""
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_val
    return default_val

def save_json(filename, data):
    """JSON ဖိုင်ထဲသို့ ဒေတာများ သိမ်းဆည်းခြင်း"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Error saving {filename}: {e}")

def load_users():
    return set(load_json(USERS_FILE, []))

def save_users(users):
    save_json(USERS_FILE, list(users))

def track_user(user_id):
    """User ID အသစ်များကို မှတ်တမ်းတင်ခြင်း"""
    users = load_users()
    if user_id not in users:
        users.add(user_id)
        save_users(users)

def load_responses():
    """မေးခွန်းနှင့် အဖြေများကို ဖတ်ယူခြင်း"""
    default_data = {
        "ငွေသွင်းအဆင့်": "💳 **ငွေသွင်းရမည့် အဆင့်များ:**\n\n၁။ KPay / Wave နံပါတ်သို့ ငွေလွှဲပါ။\n၂။ ငွေလွှဲစလစ် (Screenshot) ကို ပို့ပေးပါ။",
        "စာရင်းသွင်းအဆင့်": "📝 **စာရင်းသွင်းရမည့် အဆင့်များ:**\n\n၁။ အမည်နှင့် ဖုန်းနံပါတ် ပေးပို့ပါ။\n၂။ စာရင်းသွင်းမှု အတည်ပြုပေးပါမည်။"
    }
    return load_json(DATA_FILE, default_data)

def save_responses(data):
    save_json(DATA_FILE, data)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start command လက်ခံခြင်း"""
    user_id = update.effective_user.id
    track_user(user_id)
    
    await update.message.reply_text(
        "မင်္ဂလာပါ ခင်ဗျာ! 🙏\n\n"
        "ဤ Bot မှ သိရှိလိုသည်များကို အလိုအလျောက် ပြန်လည်ဖြေကြားပေးပါမည်။\n"
        "သိလိုသည့် မေးခွန်းများကို ရိုက်ပို့နိုင်ပါတယ် ခင်ဗျာ။"
    )

async def add_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin က Chat ထဲကနေ မေးခွန်းနှင့် အဖြေအသစ် ထည့်ရန်"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("ဒီ command ကို Admin သာ အသုံးပြုနိုင်ပါတယ် ခင်ဗျာ။")
        return

    text = update.message.text[len("!add"):].strip()
    if ":" not in text:
        await update.message.reply_text("ပုံစံ မှားယွင်းနေပါသည်။ ဥပမာ - `!add မေးခွန်း: အဖြေစာသား` ဟု ပို့ပါ ခင်ဗျာ။")
        return

    keyword, response_text = text.split(":", 1)
    keyword = keyword.strip()
    response_text = response_text.strip()

    responses = load_responses()
    responses[keyword] = response_text
    save_responses(responses)

    await update.message.reply_text(f"✅ အောင်မြင်ပါပြီ! **'{keyword}'** အတွက် အဖြေစာသားကို သိမ်းဆည်းပြီးပါပြီ။")

async def list_responses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin က လက်ရှိ သိမ်းဆည်းထားသော အချက်အလက်များ ကြည့်ရန်"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return

    responses = load_responses()
    if not responses:
        await update.message.reply_text("လက်ရှိ မည်သည့် အချက်အလက်မှ သိမ်းဆည်းထားခြင်း မရှိသေးပါ။")
        return

    msg = "📋 **လက်ရှိ သိမ်းဆည်းထားသော အချက်အလက်များ:**\n\n"
    for k, v in responses.items():
        msg += f"• **{k}**:\n{v}\n\n"
    await update.message.reply_text(msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """အသုံးပြုသူများ ပို့လိုက်သော စာများကို စစ်ဆေးပြီး အကြောင်းပြန်ပေးခြင်း"""
    user_id = update.effective_user.id
    track_user(user_id)
    
    text = update.message.text.strip()
    responses = load_responses()

    matched = False
    for keyword, response_text in responses.items():
        if keyword in text:
            await update.message.reply_text(response_text)
            matched = True
            break

    if not matched:
        await update.message.reply_text(
            "အချက်အလက်ကို နားမလည်ပါ ခင်ဗျာ။ တိကျသော စာသားများကိုသာ ရိုက်ပို့ပေးပါ ခင်ဗျာ။"
        )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin က သုံးစွဲသူ စာရင်း အရေအတွက် ကြည့်ရန်"""
    user_id = update.effective_user.id
    if user_id == ADMIN_ID:
        users = load_users()
        await update.message.reply_text(f"📊 **Bot သုံးစွဲသူ စာရင်းအချက်အလက်**\n\nစုစုပေါင်း သုံးစွဲသူ: **{len(users)}** ယောက် ရှိပါသည်။")
    else:
        await update.message.reply_text("ဒီ command ကို Admin ပဲ သုံးခွင့်ရှိပါတယ် ခင်ဗျာ။")

if __name__ == "__main__":
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise ValueError("BOT_TOKEN မတွေ့ပါ။ Environment Variables ထဲတွင် ထည့်သွင်းပေးပါ။")
        
    app = ApplicationBuilder().token(TOKEN).connect_timeout(30).read_timeout(30).write_timeout(30).build()

    # Handlers များ ထည့်သွင်းခြင်း
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("list", list_responses))
    app.add_handler(MessageHandler(filters.Regex("^!add"), add_response))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()
