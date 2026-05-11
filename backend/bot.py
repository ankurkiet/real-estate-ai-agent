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
    MessageHandler,
    filters,
    ContextTypes
)

from user_memory import (
    get_user_memory,
    set_user_memory,
    clear_user_memory
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8622581317:AAGinMyRGRYUmYL4kVzCmYeHJXRB0oAxvaw"


# START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    print("START COMMAND RECEIVED")

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

    print("USER MESSAGE:", user_message)

    try:

        # STEP 1 → Detect intent
        intent = detect_intent(user_message)

        # =========================
        # PROPERTY SEARCH FLOW
        # =========================

        if intent in ["property_search", "follow_up"]:

            previous_memory = get_user_memory(user_id)

            print("PREVIOUS MEMORY:", previous_memory)

            updated_memory = extract_requirements(
                user_message,
                previous_memory
            )

            print("UPDATED MEMORY:", updated_memory)

            set_user_memory(
                user_id,
                updated_memory
            )

            # Send to FastAPI
            response = requests.post(
                "http://127.0.0.1:8000/match-properties",
                json=updated_memory
            )

            data = response.json()

            matches = data["matches"]

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

            ai_reply = real_estate_chat(user_message)

            await update.message.reply_text(ai_reply)

    except Exception as e:

        print("ERROR:", e)

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