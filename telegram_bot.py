from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext, Application
from datetime import datetime
import pytz



TOKEN = 'YOUR TOKEN' # enter your TOKEN here
admin_id = YOUR ID # numbers
groupid = YOUR GROUP ID # numbers
user_nicknames = {}
processed_messages = []


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hi, I'm a bot."
                                    "\n/start    -- Restart the bot"
                                    "\n/name   -- Create your nickname."
                                    "\n/status   -- Check your status.")
async def set_nickname(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    nickname = context.args[0] if context.args else None
    if nickname:
        user_nicknames[user_id] = nickname
        await update.message.reply_text(f"Your name is: {nickname}")
    else:
        await update.message.reply_text("Please enter a name, ex: /name YourName")
        
async def handle_messages(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    nickname = user_nicknames.get(user_id, "Anonymous")
    # Set the current time in EST
    current_time = datetime.now(pytz.timezone("US/Eastern")).strftime("%Y-%m-%d %H:%M:%S")
    # SEND text
    if update.message.text:
        text = update.message.text
        processed_messages.append(f"{user_id}, {nickname}, {current_time}, Text: {text}")
        await context.bot.send_message(chat_id=groupid, text=f"{nickname}:{text}")
    # SEND photos
    elif update.message.photo:
        photo = update.message.photo[-1]
        processed_messages.append(f"{user_id}, {nickname}, {current_time}, Photo: {photo.file_id}")
        await context.bot.send_photo(chat_id=groupid, photo=photo.file_id, caption=f"{nickname}")
    # SEND videos
    elif update.message.video:
        video = update.message.video
        processed_messages.append(f"{user_id}, {nickname}, {current_time}, Video: {video.file_id}")
        await context.bot.send_video(chat_id=groupid, video=video.file_id, caption=f"{nickname}")
    # SEND files
    elif update.message.document:
        document = update.message.document
        processed_messages.append(f"{user_id}, {nickname}, {current_time}, Document: {document.file_id}")
        await context.bot.send_document(chat_id=groupid, document=document.file_id, caption=f"{nickname}")

async def status(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    nickname = user_nicknames.get(user_id, "Anonymous")
    await update.message.reply_text(f"Hello there!"
                                    f"\nYour ID number: {user_id}"
                                    f"\nYour name: {nickname}\n")
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

def main() -> None:
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("name", set_nickname))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("log", view_log))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_messages))
    app.run_polling()

if __name__ == '__main__':
    main()
