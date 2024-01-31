from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext, Application
from datetime import datetime
import pytz, json



TOKEN = 'YOUR TOKEN' # enter your TOKEN here
admin_id = YOUR ID # numbers
groupid = YOUR GROUP ID # numbers
user_nicknames = {}
processed_messages = []


async def help(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hi, I'm a bot."
                                    "\n/help    -- What can I do?"
                                    "\n/name   -- Create your nickname."
                                    "\n/status   -- Check your status.")
async def set_nickname(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    nickname = context.args[0] if context.args else None
    if nickname:
        user_nicknames[user_id] = nickname
        save_user_nicknames()
        await update.message.reply_text(f"Your name is: {nickname}")
    else:
        await update.message.reply_text("Please enter a name, ex: /name YourName")
        
async def handle_messages(update: Update, context: CallbackContext) -> None:
    try:
        user_id = update.message.from_user.id
        nickname = user_nicknames.get(user_id, "Anonymous")
        current_time = datetime.now(pytz.timezone("US/Eastern")).strftime("%Y-%m-%d %H:%M:%S")

        if update.message.text:
            text = update.message.text
            processed_messages.append(f"{user_id}, {nickname}, {current_time}, Text: {text}")
            await context.bot.send_message(chat_id=groupid, text=f"{nickname}: {text}")

        if update.message.photo:
            photo = update.message.photo[-1]
            text = update.message.caption
            processed_messages.append(f"{user_id}, {nickname}, {current_time}, Photo: {photo.file_id}")
            if text:
                await context.bot.send_photo(chat_id=groupid, photo=photo.file_id, caption=f"{nickname}: {text}")
            else:
                await context.bot.send_photo(chat_id=groupid, photo=photo.file_id, caption=f"{nickname}")

        if update.message.video:
            video = update.message.video
            text = update.message.caption
            processed_messages.append(f"{user_id}, {nickname}, {current_time}, Video: {video.file_id}")
            if text:
                await context.bot.send_video(chat_id=groupid, video=video.file_id, caption=f"{nickname}: {text}")
            else:
                await context.bot.send_video(chat_id=groupid, video=video.file_id, caption=f"{nickname}")

        if update.message.document:
            document = update.message.document
            text = update.message.caption
            processed_messages.append(f"{user_id}, {nickname}, {current_time}, Document: {document.file_id}")
            if text:
                await context.bot.send_document(chat_id=groupid, document=document.file_id, caption=f"{nickname}: {text}")
            else:
                await context.bot.send_document(chat_id=groupid, document=document.file_id, caption=f"{nickname}")
                
        if update.message.sticker:
            sticker = update.message.sticker
            processed_messages.append(f"{user_id}, {nickname}, {current_time}, Sticker: {sticker.file_id}")
            await context.bot.send_sticker(chat_id=groupid, sticker=sticker.file_id)
            await context.bot.send_message(chat_id=groupid, text=f"{nickname}")
                           
    except Exception as e:
        print(f"Error in handle_messages: {e}")
        raise
        
async def status(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    nickname = user_nicknames.get(user_id, "Anonymous")
    await update.message.reply_text(f"Hello there!"
                                    f"\nYour ID number: {user_id}"
                                    f"\nYour nickname: {nickname}\n")
# Allow admin to check all users' activities
async def view_log(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id == admin_id:
        log_content = "\n".join(map(str, processed_messages))
        with open("log.txt", "w", encoding="utf-8") as log_file:
            log_file.write(log_content)
        await update.message.reply_document(document=open("log.txt", "rb"), caption="Log file")
        processed_messages.clear()
    else:
        await update.message.reply_text("You do not have permission to view the log.")

def save_user_nicknames():
    with open("user_nicknames.json", "w", encoding="utf-8") as file:
        json.dump(user_nicknames, file)

def load_user_nicknames():
    try:
        with open("user_nicknames.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def main() -> None:
    global user_nicknames
    user_nicknames = load_user_nicknames()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("name", set_nickname))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("log", view_log))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_messages))
    app.run_polling()

if __name__ == '__main__':
    main()
