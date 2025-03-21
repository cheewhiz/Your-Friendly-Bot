import time
print("🚀 Bot is starting...")
time.sleep(5)

import os
import openai
import telegram
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Set up OpenAI API client
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Dictionary to store user names
user_names = {}

# Function to handle incoming messages
async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text.lower()
    user_id = update.message.chat_id
    user_name = user_names.get(user_id, None)

    # Fun responses for common phrases
    if "my name is" in user_message:
        name = user_message.split("my name is")[-1].strip().capitalize()
        user_names[user_id] = name
        bot_reply = random.choice([
            f"Nice to meet you, {name}! You seem like someone with great taste. 😎",
            f"{name}? That's a solid name. What’s on your mind?",
            f"Sweet, {name}! Now that we’re on a first-name basis, what’s up?"
        ])

    elif "how are you" in user_message:
        bot_reply = "I’m just a bunch of 1s and 0s, but if I had feelings, I’d say I’m fabulous! 💅 How about you?"

    elif "what's up" in user_message:
        bot_reply = "Not much, just chilling in cyberspace. You?"

    elif "who are you" in user_message:
        bot_reply = "I’m your AI assistant! Think of me as your smart, slightly quirky digital sidekick. 😎"

    elif "tell me a joke" in user_message:
        jokes = [
            "Why don’t skeletons fight each other? They don’t have the guts.",
            "Why don’t some couples go to the gym? Because some relationships don’t work out.",
            "I told my wife she was drawing her eyebrows too high. She looked surprised.",
            "Why don’t oysters donate to charity? Because they are shellfish!",
        ]
        bot_reply = random.choice(jokes)

    elif "i love" in user_message:
        love_thing = user_message.split("i love")[-1].strip().capitalize()
        bot_reply = f"Ohhh, {love_thing}! That’s awesome. Tell me more! 😃"

    elif user_message in ["haha", "lol", "lmao", "😂", "🤣"]:
        bot_reply = random.choice([
            "Glad you liked that! You want another one? 😆",
            "Comedy level: AI-powered stand-up! 🎤 Drop the mic.",
            "I live to entertain! Want another joke or should we get philosophical? 😂"
        ])

    else:
        try:
            client = openai.OpenAI(api_key=openai.api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You're a witty, fun, helpful, and slightly cheeky assistant. Respond like you're chatting with a friend. Keep things casual and human-like."},
                    {"role": "user", "content": user_message}
                ]
            )
            bot_reply = response.choices[0].message.content.strip()

        except Exception as e:
            bot_reply = "Whoops! 🤖 My brain glitched. Maybe my dog unplugged my power cord? 🐶"
            print(f"Error: {e}")

    await update.message.reply_text(bot_reply)

# Function to start the bot with fun greetings
async def start(update: Update, context: CallbackContext):
    greetings = [
        "Hey there! 😃 I'm your friendly AI assistant. What’s up?",
        "Yo! 👋 Need some help? Or just here for my charming personality? 😏",
        "Hello, human! 🤖 Ready to chat?",
    ]
    await update.message.reply_text(random.choice(greetings))

# Main function to run the bot
def main():
    bot_token = os.environ.get("BOT_TOKEN")

    app = Application.builder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()