import telebot
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ENV variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
FOLDER_ID = os.getenv("FOLDER_ID")

bot = telebot.TeleBot(BOT_TOKEN)

# Google Drive Auth
SCOPES = ['https://www.googleapis.com/auth/drive']

creds_dict = json.loads(os.getenv("GOOGLE_CREDS"))
creds = service_account.Credentials.from_service_account_info(
    creds_dict, scopes=SCOPES)

drive_service = build('drive', 'v3', credentials=creds)

# Upload function
def upload_to_drive(file_path, file_name):
    file_metadata = {'name': file_name, 'parents': [FOLDER_ID]}
    media = MediaFileUpload(file_path, resumable=True)

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return file.get('id')

# Handle files
@bot.message_handler(content_types=['document', 'photo', 'video', 'audio'])
def handle_files(message):
    try:
        if message.document:
            file_info = bot.get_file(message.document.file_id)
            file_name = message.document.file_name
        elif message.photo:
            file_info = bot.get_file(message.photo[-1].file_id)
            file_name = "photo.jpg"
        elif message.video:
            file_info = bot.get_file(message.video.file_id)
            file_name = "video.mp4"
        elif message.audio:
            file_info = bot.get_file(message.audio.file_id)
            file_name = "audio.mp3"

        downloaded_file = bot.download_file(file_info.file_path)

        with open(file_name, 'wb') as f:
            f.write(downloaded_file)

        drive_id = upload_to_drive(file_name, file_name)

        bot.reply_to(message, f"✅ Uploaded to Drive\nID: {drive_id}")

        os.remove(file_name)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Start bot
bot.infinity_polling()