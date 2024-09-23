import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your bot token
TELEGRAM_BOT_TOKEN = '6315185069:AAGeIwcUzw66keUM6o0Mtv9sytWQWH_WhMI'
API_BASE_URL = 'https://api3.peaceful-wolf.workers.dev'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Send me the name of an anime to search for!')

async def search_anime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name = update.message.text
    response = requests.get(f'{API_BASE_URL}/search/{name}')

    if response.status_code == 200:
        data = response.json()
        
        # Check if there are results
        if data and isinstance(data, list) and len(data) > 0:
            anime = data[0]  # Get the first anime result
            anime_id = anime['id']  # Assuming 'id' is in the response
            
            # Get download links
            download_response = requests.get(f'{API_BASE_URL}/download/{anime_id}')
            if download_response.status_code == 200:
                download_data = download_response.json()
                
                if download_data and 'urls' in download_data:
                    download_urls = download_data['urls']
                    # For this example, we'll just take the first download URL
                    file_url = download_urls[0]
                    
                    # Download the file
                    file_response = requests.get(file_url)
                    if file_response.status_code == 200:
                        file_name = file_url.split("/")[-1]  # Extract file name from URL
                        with open(file_name, 'wb') as f:
                            f.write(file_response.content)

                        # Send the file to Telegram
                        with open(file_name, 'rb') as f:
                            await update.message.reply_document(document=f)

                        # Clean up by deleting the file after sending
                        os.remove(file_name)
                    else:
                        await update.message.reply_text('Error downloading the file.')
                else:
                    await update.message.reply_text('No download links found for that anime.')
            else:
                await update.message.reply_text('Error fetching download links.')
        else:
            await update.message.reply_text('No anime found with that name.')
    else:
        await update.message.reply_text('Error fetching data from the API.')

def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_anime))

    app.run_polling()

if __name__ == '__main__':
    main()
