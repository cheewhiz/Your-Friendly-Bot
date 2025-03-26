import os
import openai
import random
import requests
from telegram import Update, BotCommand
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, CallbackContext
)

# Load keys from environment
openai.api_key = os.getenv("OPENAI_API_KEY")
tenor_api_key = os.getenv("TENOR_API_KEY")
bot_token = os.getenv("BOT_TOKEN")

user_preferences = {}

# ========== Utilities ==========

def fetch_gif(query):
    response = requests.get(
        "https://tenor.googleapis.com/v2/search",
        params={"q": query, "key": tenor_api_key, "limit": 1, "media_filter": "gif"}
    )
    data = response.json()
    if data.get("results"):
        return data["results"][0]["media_formats"]["gif"]["url"]
    return None

def generate_image(prompt):
    client = openai.OpenAI(api_key=openai.api_key)
    response = client.images.generate(model="dall-e-3", prompt=prompt, n=1, size="1024x1024")
    return response.data[0].url

def get_random_dog_image():
    try:
        response = requests.get("https://random.dog/woof.json")
        return response.json().get("url")
    except:
        return None

# ========== Command Handlers ==========

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hey there! 😃 I'm your friendly AI assistant. What’s up?")

async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "✨ Here's what I can do:\n"
        "/start – Greet you\n"
        "/help – Show this help message\n"
        "/dog – Send a random dog pic 🐶\n"
        "/meme – Send a funny GIF\n"
        "/funfact – Surprise you with a random fact\n"
        "/weather <city> – Simulate weather 🌤️\n"
        "Also try:\n"
        "'Draw me a sloth in space'\n"
        "'Send me a gif of pizza'\n"
        "'Remember I like sushi'\n"
        "'What do I like?'"
    )

async def about(update: Update, context: CallbackContext):
    await update.message.reply_text("I'm your AI sidekick 🤖 – powered by GPT-4, with GIFs and sass!")

async def meme(update: Update, context: CallbackContext):
    gif_url = fetch_gif("funny meme")
    if gif_url:
        await update.message.reply_animation(gif_url)
    else:
        await update.message.reply_text("Couldn’t fetch a meme right now 😅")

async def dog(update: Update, context: CallbackContext):
    dog_url = get_random_dog_image()
    if dog_url:
        await update.message.reply_photo(dog_url)
    else:
        await update.message.reply_text("No pups found 🐾")

async def funfact(update: Update, context: CallbackContext):
    facts = [
        "Octopuses have 3 hearts.",
        "Bananas are berries, strawberries aren’t.",
        "A group of flamingos is called a 'flamboyance'.",
        "Honey never spoils – archaeologists found 3,000-year-old edible honey!"
    ]
    await update.message.reply_text(random.choice(facts))

async def weather(update: Update, context: CallbackContext):
    city = " ".join(context.args) if context.args else None
    if city:
        await update.message.reply_text(f"Let’s imagine it’s sunny and 25°C in {city} 😎🌤️")
    else:
        await update.message.reply_text("Please provide a city like this: /weather sydney")

# ========== Message Handler ==========

async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.lower().strip()
    user_id = update.message.chat_id

    if "remember i like" in text:
        preference = text.split("remember i like")[-1].strip()
        user_preferences[user_id] = preference
        return await update.message.reply_text(f"Noted! You like {preference} 😄")

    if "what do i like" in text:
        if user_id in user_preferences:
            return await update.message.reply_text(f"You told me you like {user_preferences[user_id]}")
        return await update.message.reply_text("Tell me something you like and I'll remember it!")

    if "draw me" in text:
        prompt = text.split("draw me")[-1].strip()
        try:
            await update.message.reply_text("Hold on, drawing something epic 🎨...")
            url = generate_image(prompt)
            return await update.message.reply_photo(url)
        except Exception as e:
            print(e)
            return await update.message.reply_text("Couldn’t create the image 😅")

    if "gif of" in text:
        keyword = text.split("gif of")[-1].strip()
        gif_url = fetch_gif(keyword)
        if gif_url:
            return await update.message.reply_animation(gif_url)
        return await update.message.reply_text("No GIFs found 😢")

    # Fallback GPT-4 reply
    try:
        client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're a helpful, sassy, witty chatbot."},
                {"role": "user", "content": text}
            ]
        )
        await update.message.reply_text(response.choices[0].message.content.strip())
    except Exception as e:
        print("GPT error:", e)
        await update.message.reply_text("My brain just glitched out 💥")

# ========== Bot Command Setup ==========

async def set_bot_commands(app):
    commands = [
        BotCommand("start", "Greet the user"),
        BotCommand("help", "Show available commands"),
        BotCommand("about", "About the bot"),
        BotCommand("dog", "Send a random dog image 🐶"),
        BotCommand("meme", "Send a funny meme GIF 😂"),
        BotCommand("funfact", "Send a fun fact 📚"),
        BotCommand("weather", "Simulate weather info 🌦️"),
    ]
    await app.bot.set_my_commands(commands)

# ========== Main Function ==========

def main():
    app = Application.builder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("dog", dog))
    app.add_handler(CommandHandler("meme", meme))
    app.add_handler(CommandHandler("funfact", funfact))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    async def on_startup(app):  # Ensure commands are registered
        await set_bot_commands(app)

    app.post_init = on_startup

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
