import logging
import requests

from ai_service import (
    detect_intent,
    extract_requirements,
    real_estate_chat
)


from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.error import Conflict

from user_memory import (
    get_user_memory,
    set_user_memory,
    clear_user_memory
)

# Only show WARNING+ from noisy libraries; keep our own prints clean
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("telegram.ext").setLevel(logging.WARNING)

TOKEN = "8622581317:AAGinMyRGRYUmYL4kVzCmYeHJXRB0oAxvaw"


async def handle_bot_error(update: object, context: ContextTypes.DEFAULT_TYPE):

    error = context.error

    if isinstance(error, Conflict):
        print("[ERROR] Duplicate bot instance detected. Stop other bot.py processes.")
        return

    print(f"[ERROR] {type(error).__name__}: {error}")


# START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    print("[BOT] /start")

    await update.message.reply_text(
        "🏠 Welcome to Real Estate AI Assistant"
    )


# RESET MEMORY COMMAND
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id

    clear_user_memory(user_id)

    await update.message.reply_text(
        "✅ Search filters cleared"
    )


# MAIN MESSAGE HANDLER
async def handle_message(update, context):

    user_message = update.message.text

    user_id = update.message.from_user.id

    print(f"[MSG] {user_message}")

    try:

        # STEP 1 → Detect intent
        intent = detect_intent(user_message)

        # =========================
        # PROPERTY SEARCH FLOW
        # =========================

        if intent in ["property_search", "follow_up"]:

            previous_memory = get_user_memory(user_id)

            updated_memory = extract_requirements(
                user_message,
                previous_memory
            )

            set_user_memory(
                user_id,
                updated_memory
            )

            print(f"[SEARCH] intent={intent} | filters={updated_memory}")

            # Send to FastAPI
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/match-properties",
                    json=updated_memory,
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
            except requests.exceptions.RequestException as api_err:
                print(f"[ERROR] API call failed: {api_err}")
                await update.message.reply_text("⚠️ Search service unavailable. Please try again.")
                return

            matches = data.get("matches", [])

            if len(matches) == 0:

                await update.message.reply_text(
                    "❌ No matching properties found"
                )

                return

            message = "🏠 Top Recommended Properties\n\n"

            for property in matches[:5]:

                message += (
                    f"📍 {property['location']}, {property['city']}\n"
                    f"🏢 {property['bhk']} BHK\n"
                    f"💰 ₹{property['price']}\n"
                    f"⭐ Match Score: {property['match_score']}/100\n\n"
                    f"Why Recommended:\n"
                )

                for reason in property["reasons"]:
                    message += f"✅ {reason}\n"

                message += "\n-------------------\n\n"

            await update.message.reply_text(message)

        # =========================
        # AI CONSULTANT FLOW
        # =========================

        else:

            print(f"[CHAT] intent={intent}")

            ai_reply = real_estate_chat(user_message)

            await update.message.reply_text(ai_reply)

    except Exception as e:

        print(f"[ERROR] {type(e).__name__}: {e}")

        await update.message.reply_text(
            "⚠️ Error processing your request"
        )

# MAIN FUNCTION
def main():

    print("Starting bot...")

    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_error_handler(handle_bot_error)

    # Messages
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("Bot Running...")

    app.run_polling()


if __name__ == "__main__":
    main()