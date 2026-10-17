import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

# ဖိုင်များအတွက် Path သတ်မှတ်ခြင်း
RESPONSES_FILE = "responses.json"
USERS_FILE = "users.json"
ADMIN_ID = 8012437507  # သင့်ရဲ့ Admin ID

# အချက်အလက်များ တင်ယူရန်
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

# အချက်အလက်များ သိမ်းဆည်းရန်
def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

responses = load_data(RESPONSES_FILE)
users = load_data(USERS_FILE)

# /start အမိန့်အတွက်
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id_str = str(user.id)
    
    # User အသစ်ဖြစ်ပါက users.json ထဲသို့ မှတ်သားမည်
    if user_id_str not in users:
        users[user_id_str] = {
            "username": user.username,
            "first_name": user.first_name
        }
        save_data(USERS_FILE, users)
        
    await update.message.reply_text(
        "မင်္ဂလာပါ ခင်ဗျာ! 🙏\n\n"
        "ဤ Bot မှ သိရှိလိုသည်များကို အလိုအလျောက် ပြန်လည်ဖြေကြားပေးပါမည်။ "
        "သိလိုသည့် မေးခွန်းများကို ရိုက်ပို့နိုင်ပါတယ် ခင်ဗျာ။"
    )

# Admin အတွက် ပုံပါသော သို့မဟုတ် စာသားသီးသန့် FAQ အသစ်ထည့်ရန် (!add keyword | ဖြေမည့်စာသား)
async def add_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⚠ ဤအမိန့်ကို Admin သာ အသုံးပြုနိုင်ပါသည်။")
        return

    text = update.message.text
    command_content = text[len("!add"):].strip()
    
    # ပုံပါလာခြင်း ရှိမရှိ စစ်ဆေးမည်
    if update.message.photo:
        photo_file_id = update.message.photo[-1].file_id
        parts = command_content.split(":", 1)
        if len(parts) < 2:
            await update.message.reply_text("⚠ ပုံစံမမှန်ပါ။ ဥပမာ - `!add keyword: အဖြေစာသား` ဟု ပုံနှင့်အတူ caption ရေးပို့ပါ။")
            return
        keyword = parts[0].strip().lower()
        reply_text = parts[1].strip()
        
        responses[keyword] = {
            "text": reply_text,
            "photo": photo_file_id
        }
        save_data(RESPONSES_FILE, responses)
        await update.message.reply_text(f"✅ ပုံပါသော '{keyword}' မေးခွန်းနှင့် အဖြေကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ!")
        return

    parts = command_content.split(":", 1)
    if len(parts) < 2:
        await update.message.reply_text("⚠ ပုံစံမမှန်ပါ။ ဥပမာ - `!add keyword: အဖြေစာသား`")
        return

    keyword = parts[0].strip().lower()
    reply_text = parts[1].strip()

    responses[keyword] = {
        "text": reply_text,
        "photo": None
    }
    save_data(RESPONSES_FILE, responses)
    await update.message.reply_text(f"✅ '{keyword}' မေးခွန်းနှင့် အဖြေကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ!")

# /list အမိန့် (သိမ်းထားသမျှ FAQ များကို ကြည့်ရန်)
async def list_responses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⚠ ဤအမိန့်ကို Admin သာ အသုံးပြုနိုင်ပါသည်။")
        return

    if not responses:
        await update.message.reply_text("📭 လက်ရှိတွင် သိမ်းဆည်းထားသော အချက်အလက် မရှိသေးပါ။")
        return

    msg = "📋 **သိမ်းဆည်းထားသော မေးခွန်းများစာရင်း:**\n\n"
    for idx, (kw, val) in enumerate(responses.items(), 1):
        has_photo = " [📸 ပုံပါရှိသည်]" if val.get("photo") else ""
        msg += f"{idx}. `{kw}`{has_photo}\n"
    
    await update.message.reply_text(msg, parse_mode="Markdown")

# /stats အမိန့် (Bot သုံးစွဲသူဦးရေ စစ်ဆေးရန်)
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⚠ ဤအမိန့်ကို Admin သာ အသုံးပြုနိုင်ပါသည်။")
        return

    total_users = len(users)
    await update.message.reply_text(f"📊 လက်ရှိ Bot အသုံးပြုနေသူ စုစုပေါင်း: **{total_users}** ဦး ရှိပါသည်။", parse_mode="Markdown")

# /broadcast အမိန့် (သုံးစွဲသူအားလုံးဆီသို့ စာပို့ရန်)
async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⚠ ဤအမိန့်ကို Admin သာ အသုံးပြုနိုင်ပါသည်။")
        return

    # ပေးပို့လိုသော စာသားကို ယူမည် (ဥပမာ - /broadcast မင်္ဂလာပါ...)
    text = update.message.text
    broadcast_text = text[len("/broadcast"):].strip()
    
    if not broadcast_text:
        await update.message.reply_text("⚠ ပို့လိုသည့် စာသားကို ထည့်ပါ။ ဥပမာ - `/broadcast အရေးကြီးကြေညာချက်...`", parse_mode="Markdown")
        return

    if not users:
        await update.message.reply_text("📭 Bot ကို အသုံးပြုထားသူ လုံးဝ မရှိသေးပါ။")
        return

    success_count = 0
    fail_count = 0

    await update.message.reply_text(f"📤 စုစုပေါင်း သုံးစွဲသူ {len(users)} ဦးဆီသို့ စာစတင်ပို့နေပါပြီ...")

    for uid_str in users.keys():
        try:
            await context.bot.send_message(chat_id=int(uid_str), text=broadcast_text)
            success_count += 1
        except Exception as e:
            fail_count += 1

    await update.message.reply_text(f"✅ ပို့ပြီးပါပြီ!\n- အောင်မြင်သူ: {success_count} ဦး\n- မအောင်မြင်သူ (Bot ကို Block ထားသူများ): {fail_count} ဦး")

# ပုံ သို့မဟုတ် စာသားဖြင့် မေးခွန်းများကို ပြန်ဖြေပေးမည့် Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text.lower()
    
    for keyword, data in responses.items():
        if keyword in user_text:
            reply_text = data.get("text")
            photo_id = data.get("photo")
            
            if photo_id:
                await update.message.reply_photo(photo=photo_id, caption=reply_text)
            else:
                await update.message.reply_text(reply_text)
            return

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Error: BOT_TOKEN environment variable not found!")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers များ သတ်မှတ်ခြင်း
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_responses))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast_message))  # Broadcast အမိန့် အသစ်ထည့်သွင်းခြင်း
    
    app.add_handler(MessageHandler(filters.Regex(r"^!add") & filters.User(user_id=ADMIN_ID), add_response))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
