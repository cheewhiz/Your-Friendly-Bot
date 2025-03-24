import os
import openai
import telegram
import random
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Load API keys from environment variables
openai.api_key = os.environ.get("OPENAI_API_KEY")
tenor_api_key = os.environ.get("TENOR_API_KEY")
bot_token = os.environ.get("BOT_TOKEN")

# Dictionary to store user names
user_names = {}

# Function to fetch a GIF from Tenor
def fetch_gif(query):
    response = requests.get(
        "https://tenor.googleapis.com/v2/search",
        params={
            "q": query,
            "key": tenor_api_key,
            "limit": 1,
            "media_filter": "gif"
        }
    )
    data = response.json()
    if data.get("results"):
        return data["results"][0]["media_formats"]["gif"]["url"]
    return None

# Function to generate image with DALL·E
def generate_image(prompt):
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return response.data[0].url

# Handle /start command
async def start(update: Update, context: CallbackContext):
    greetings = [
        "Hey there! 😃 I'm your friendly AI assistant. What’s up?",
        "Yo! 👋 Need some help? Or just here for my charming personality? 😏",
        "Hello, human! 🤖 Ready to chat?",
    ]
    await update.message.reply_text(random.choice(greetings))

# Handle /meme command
async def meme_command(update: Update, context: CallbackContext):
    gif_url = fetch_gif("funny meme")
    if gif_url:
        await update.message.reply_animation(gif_url)
    else:
        await update.message.reply_text("Hmm… couldn't find a meme for that moment 😅")

# Handle user messages
async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text.lower()
    user_id = update.message.chat_id

    # Name recognition
    if "my name is" in user_message:
        name = user_message.split("my name is")[-1].strip().capitalize()
        user_names[user_id] = name
        await update.message.reply_text(f"Nice to meet you, {name}! 😄")
        return

    # Joke
    elif "tell me a joke" in user_message:
        jokes = [
            "Why don’t skeletons fight each other? They don’t have the guts.",
            "Why did the scarecrow win an award? Because he was outstanding in his field.",
        ]
        await update.message.reply_text(random.choice(jokes))
        return

    # I love...
    elif "i love" in user_message:
        love_thing = user_message.split("i love")[-1].strip().capitalize()
        await update.message.reply_text(f"Ohhh, {love_thing}!! That’s awesome. Tell me more! 😃")
        return

    # Draw me...
    elif "draw me" in user_message or "generate an image of" in user_message:
        prompt = user_message.replace("draw me", "").replace("generate an image of", "").strip()
        try:
            await update.message.reply_text("Give me a second to paint something beautiful! 🧑‍🎨")
            image_url = generate_image(prompt)
            await update.message.reply_photo(image_url)
        except Exception as e:
            print(f"DALL·E error: {e}")
            await update.message.reply_text("Oops! Couldn't generate an image 😢")
        return

    # Send me a gif of...
    elif "send me a gif of" in user_message or "gif of" in user_message:
        keyword = user_message.split("gif of")[-1].strip()
        gif_url = fetch_gif(keyword)
        if gif_url:
            await update.message.reply_animation(gif_url)
        else:
            await update.message.reply_text("Hmm, couldn't find a GIF for that 😅")
        return

    # Default GPT-4 response
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're a witty, helpful AI with personality."},
                {"role": "user", "content": user_message}
            ]
        )
        await update.message.reply_text(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"GPT-4 error: {e}")
        await update.message.reply_text("Oops! Brain cramp 😅")

# Main
def main():
    app = Application.builder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("meme", meme_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
