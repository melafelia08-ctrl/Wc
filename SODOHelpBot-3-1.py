import asyncio
import json
import os
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8976765441:AAFB6QeetUHac1ZPBNqSw79FNO29WxxqtLA")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "8609127164"))

BRAND = "🛟 <b>SODO Support</b>"
DIVIDER = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
USERS_FILE = "known_users.json"


def load_known_users() -> set:
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return set(json.load(f))
        except (json.JSONDecodeError, IOError):
            return set()
    return set()


def save_known_users(users: set):
    with open(USERS_FILE, "w") as f:
        json.dump(list(users), f)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    known_users = context.application.bot_data["known_users"]
    is_new = chat_id not in known_users
    if is_new:
        known_users.add(chat_id)
        save_known_users(known_users)

    if is_new:
        welcome_text = (
            f"{BRAND}\n"
            f"{DIVIDER}\n\n"
            f"🎉 <b>Swagat Hai, {user.first_name} Bhai!</b> 🎉\n\n"
            "✨ <b>SODO Family Mein Aapka Dil Se Swagat Hai!</b> ✨\n\n"
            "📌 <b>Yahan Aap:</b>\n"
            "💬 <b>Koi bhi sawal pooch sakte ho</b>\n"
            "🛠️ <b>Support le sakte ho</b>\n"
            "📢 <b>Apni baat hum tak pahuncha sakte ho</b>\n\n"
            f"{DIVIDER}\n"
            "⚡ <b>Bas neeche type karo — hum hain yahan!</b> 👇\n"
            f"{DIVIDER}"
        )
    else:
        welcome_text = (
            f"{BRAND}\n"
            f"{DIVIDER}\n\n"
            f"👋 <b>Welcome Back, {user.first_name}!</b>\n\n"
            "😊 <b>Acha Laga Aapko Dobara Dekhke!</b> 🌟\n\n"
            "💬 <b>Apna message neeche bhejo — jaldi reply karenge!</b> ⚡\n"
            f"{DIVIDER}"
        )

    await update.message.reply_text(welcome_text, parse_mode="HTML")


async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = update.effective_user
    chat_id = update.effective_chat.id

    if user.id == ADMIN_ID:
        return

    known_users = context.application.bot_data["known_users"]
    if chat_id not in known_users:
        known_users.add(chat_id)
        save_known_users(known_users)

    username = f"@{user.username}" if user.username else "❌ No Username"
    timestamp = datetime.now().strftime("%d %b, %I:%M %p")

    # User ko turant confirmation do
    await update.message.reply_text(
        "✅ <b>Message Mil Gaya!</b>\n"
        "⏳ <b>Humari team jald hi reply karegi!</b> 🚀",
        parse_mode="HTML",
    )

    await context.bot.send_chat_action(chat_id=ADMIN_ID, action="typing")

    info = await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "📩 <b>NEW MESSAGE</b>\n"
            f"{DIVIDER}\n"
            f"👤 <b>Name:</b> {user.full_name}\n"
            f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
            f"🔗 <b>Username:</b> {username}\n"
            f"🕐 <b>Time:</b> {timestamp}\n"
            f"{DIVIDER}\n"
            "💬 <b>Message niche hai</b> ⬇️"
        ),
        parse_mode="HTML",
    )

    copied = await context.bot.copy_message(
        chat_id=ADMIN_ID,
        from_chat_id=chat_id,
        message_id=message.message_id,
    )

    context.application.bot_data[copied.message_id] = chat_id
    context.application.bot_data[info.message_id] = chat_id


async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if update.effective_user.id != ADMIN_ID:
        return

    if not message.reply_to_message:
        return

    reply_to_id = message.reply_to_message.message_id
    target_user_id = context.application.bot_data.get(reply_to_id)

    if not target_user_id:
        await message.reply_text(
            "❌ <b>User ke message par reply karo.</b>\n"
            "Bot ko seedha message bhejne se relay nahi hoga.",
            parse_mode="HTML",
        )
        return

    try:
        await context.bot.send_chat_action(chat_id=target_user_id, action="typing")
        await context.bot.copy_message(
            chat_id=target_user_id,
            from_chat_id=ADMIN_ID,
            message_id=message.message_id,
        )
        await message.reply_text("✅ <b>Reply user ko send ho gaya!</b> 🚀", parse_mode="HTML")

    except Exception as e:
        await message.reply_text(
            f"❌ <b>User ko reply nahi bhej saka:</b>\n<code>{e}</code>",
            parse_mode="HTML",
        )


async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    context.application.bot_data["awaiting_broadcast"] = True
    count = len(context.application.bot_data["known_users"])

    await update.message.reply_text(
        "📢 <b>Broadcast Mode ON</b>\n"
        f"{DIVIDER}\n"
        f"📊 <b>Total Users:</b> {count}\n"
        "⚡ <b>Ab jo bhi bhejoge, sabko chala jayega!</b>\n\n"
        "❌ Cancel: /cancel",
        parse_mode="HTML",
    )


async def broadcast_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    context.application.bot_data["awaiting_broadcast"] = False
    await update.message.reply_text("❌ <b>Broadcast cancel ho gaya.</b>", parse_mode="HTML")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    count = len(context.application.bot_data["known_users"])
    await update.message.reply_text(
        f"📊 <b>BOT STATS</b>\n"
        f"{DIVIDER}\n"
        f"👥 <b>Total Users:</b> {count}",
        parse_mode="HTML",
    )


async def admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if update.effective_user.id != ADMIN_ID:
        return

    if context.application.bot_data.get("awaiting_broadcast"):
        context.application.bot_data["awaiting_broadcast"] = False
        known_users = context.application.bot_data["known_users"]

        sent, failed = 0, 0
        for uid in known_users:
            try:
                await context.bot.copy_message(
                    chat_id=uid,
                    from_chat_id=ADMIN_ID,
                    message_id=message.message_id,
                )
                sent += 1
            except Exception:
                failed += 1

        await message.reply_text(
            "📢 <b>Broadcast Complete!</b>\n"
            f"{DIVIDER}\n"
            f"✅ <b>Sent:</b> {sent}\n"
            f"❌ <b>Failed:</b> {failed}",
            parse_mode="HTML",
        )
        return

    await message.reply_text(
        "ℹ️ <b>User ke message par reply karo</b> usko respond karne ke liye,\n"
        "ya <b>/broadcast</b> se sabko ek saath message bhejo.",
        parse_mode="HTML",
    )


async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = len(context.application.bot_data["known_users"])
    await update.message.reply_text(
        "👑 <b>SODO ADMIN PANEL</b>\n"
        f"{DIVIDER}\n\n"
        f"👥 <b>Total Users:</b> {count}\n\n"
        "📩 <b>Naya message</b> → notification milegi\n"
        "↩️ <b>Reply</b> karo → seedha user tak jayega\n"
        "📢 <b>/broadcast</b> → sabhi users ko message bhejo\n"
        "📊 <b>/stats</b> → user count dekho\n\n"
        f"{DIVIDER}\n"
        "⚡ <b>Simple. Fast. Ready!</b>",
        parse_mode="HTML",
    )


def main():
    print("🤖 SODO Support Bot is running...")

    app = Application.builder().token(BOT_TOKEN).build()
    app.bot_data["known_users"] = load_known_users()
    app.bot_data["awaiting_broadcast"] = False

    app.add_handler(CommandHandler("broadcast", broadcast_start, filters=filters.User(ADMIN_ID)))
    app.add_handler(CommandHandler("cancel", broadcast_cancel, filters=filters.User(ADMIN_ID)))
    app.add_handler(CommandHandler("stats", stats, filters=filters.User(ADMIN_ID)))

    app.add_handler(
        MessageHandler(
            filters.COMMAND & filters.ChatType.PRIVATE & ~filters.User(ADMIN_ID),
            start,
        )
    )
    app.add_handler(
        MessageHandler(
            filters.COMMAND & filters.ChatType.PRIVATE & filters.User(ADMIN_ID),
            admin_start,
        )
    )
    app.add_handler(
        MessageHandler(
            filters.Chat(ADMIN_ID) & ~filters.COMMAND & filters.REPLY,
            admin_reply,
        )
    )
    app.add_handler(
        MessageHandler(
            filters.Chat(ADMIN_ID) & ~filters.COMMAND & ~filters.REPLY,
            admin_message,
        )
    )
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & ~filters.COMMAND & ~filters.User(ADMIN_ID),
            user_message,
        )
    )

    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=False,
    )


if __name__ == "__main__":
    asyncio.set_event_loop(asyncio.new_event_loop())
    main()
