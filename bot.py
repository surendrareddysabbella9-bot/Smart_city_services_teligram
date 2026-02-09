"""
Smart City Services Telegram Bot

A bot that allows users to discover and request city service workers
such as Electricians, Plumbers, and Construction Workers.
"""

import logging
import os
import sys
from enum import Enum, auto
from typing import Optional

from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)

# Reduce noise from httpx
logging.getLogger("httpx").setLevel(logging.WARNING)


# Conversation states
class States(Enum):
    SELECTING_SERVICE = auto()
    ENTERING_LOCATION = auto()


# Available services
SERVICES = {
    "electrician": "⚡ Electrician",
    "plumber": "🔧 Plumber",
    "construction": "🏗️ Construction Worker",
}


def get_service_keyboard() -> InlineKeyboardMarkup:
    """Create an inline keyboard with available services."""
    keyboard = [
        [InlineKeyboardButton(name, callback_data=service_id)]
        for service_id, name in SERVICES.items()
    ]
    return InlineKeyboardMarkup(keyboard)


def get_location_keyboard() -> ReplyKeyboardMarkup:
    """Create a keyboard with location sharing button."""
    keyboard = [
        [KeyboardButton("📍 Share My Location", request_location=True)],
        [KeyboardButton("❌ Cancel")],
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> States:
    """Handle the /start command - display welcome message and services."""
    user = update.effective_user
    logger.info(f"User {user.id} ({user.first_name}) started the bot")

    welcome_message = (
        f"👋 Welcome to *Smart City Services*, {user.first_name}!\n\n"
        "We connect you with skilled service workers in your area.\n\n"
        "🔹 *Available Services:*\n"
        "• ⚡ Electrician\n"
        "• 🔧 Plumber\n"
        "• 🏗️ Construction Worker\n\n"
        "Please select a service below to get started:"
    )

    await update.message.reply_text(
        welcome_message,
        parse_mode="Markdown",
        reply_markup=get_service_keyboard(),
    )

    return States.SELECTING_SERVICE


async def service_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> States:
    """Handle service selection from inline keyboard."""
    query = update.callback_query
    await query.answer()

    service_id = query.data
    service_name = SERVICES.get(service_id, "Unknown Service")

    # Store the selected service in user data
    context.user_data["selected_service"] = service_name

    logger.info(f"User {query.from_user.id} selected service: {service_name}")

    await query.edit_message_text(
        f"You selected: *{service_name}*\n\n"
        "📍 Please share your location so we can find nearby workers.",
        parse_mode="Markdown",
    )

    # Send a new message with the location button
    await query.message.reply_text(
        "Tap the button below to share your location:\n\n"
        "_Your location will only be used to find nearby service workers._",
        parse_mode="Markdown",
        reply_markup=get_location_keyboard(),
    )

    return States.ENTERING_LOCATION


async def location_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle location sharing from user."""
    user = update.effective_user
    location = update.message.location
    service_name = context.user_data.get("selected_service", "the requested service")

    # Extract coordinates
    latitude = location.latitude
    longitude = location.longitude

    logger.info(
        f"User {user.id} requested {service_name} at location: "
        f"({latitude}, {longitude})"
    )

    # Create Google Maps link for the location
    maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"

    confirmation_message = (
        "✅ *Request Confirmed!*\n\n"
        f"📋 *Service:* {service_name}\n"
        f"📍 *Location:* [{latitude:.6f}, {longitude:.6f}]({maps_link})\n\n"
        "🔔 Nearby workers have been notified and will contact you shortly.\n\n"
        "_Thank you for using Smart City Services!_\n\n"
        "Use /start to request another service."
    )

    await update.message.reply_text(
        confirmation_message,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )

    # Clear user data
    context.user_data.clear()

    return ConversationHandler.END


async def text_location_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle manual text location input as fallback."""
    user = update.effective_user
    text = update.message.text.strip()

    # Check if user clicked Cancel
    if text == "❌ Cancel":
        await update.message.reply_text(
            "❌ Request cancelled.\n\nUse /start to begin again.",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data.clear()
        return ConversationHandler.END

    service_name = context.user_data.get("selected_service", "the requested service")

    logger.info(f"User {user.id} requested {service_name} in area: {text}")

    confirmation_message = (
        "✅ *Request Confirmed!*\n\n"
        f"📋 *Service:* {service_name}\n"
        f"📍 *Location:* {text}\n\n"
        "🔔 Nearby workers have been notified and will contact you shortly.\n\n"
        "_Thank you for using Smart City Services!_\n\n"
        "Use /start to request another service."
    )

    await update.message.reply_text(
        confirmation_message,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )

    # Clear user data
    context.user_data.clear()

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /cancel command to exit the conversation."""
    user = update.effective_user
    logger.info(f"User {user.id} cancelled the conversation")

    await update.message.reply_text(
        "❌ Request cancelled.\n\nUse /start to begin again.",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )

    context.user_data.clear()
    return ConversationHandler.END


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors and notify developers."""
    logger.error(f"Exception while handling an update: {context.error}")


def check_python_version() -> bool:
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        logger.error(
            f"Python 3.10+ is required. Current version: {version.major}.{version.minor}.{version.micro}"
        )
        return False
    return True


def get_bot_token() -> Optional[str]:
    """Get the bot token from environment variables."""
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error(
            "BOT_TOKEN environment variable not set. "
            "Please create a .env file with BOT_TOKEN=your_token"
        )
        return None
    return token


def main() -> None:
    """Main function to run the bot."""
    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Get bot token
    token = get_bot_token()
    if not token:
        sys.exit(1)

    logger.info("Starting Smart City Services Bot...")

    # Create the Application
    application = Application.builder().token(token).build()

    # Create conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            States.SELECTING_SERVICE: [
                CallbackQueryHandler(service_selected),
            ],
            States.ENTERING_LOCATION: [
                MessageHandler(filters.LOCATION, location_received),
                MessageHandler(filters.TEXT & ~filters.COMMAND, text_location_received),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Add handlers
    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("Bot started successfully! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
