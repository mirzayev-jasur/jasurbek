import os

# Telegram Bot Token
BOT_TOKEN = "7574473770:AAFeYDkFd_hgIseq8mZLZZQWgVV8cgChDqs"

# Admin User ID (should be integer, not string)
ADMIN_ID = 7309800046

# Admin Password
ADMIN_PASSWORD = "jasur08"

# Database Configuration
DB_NAME = "bot_data.db"

# Media Storage Directory
MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True)

# Channel/Group IDs (optional)
CHANNEL_ID = "@your_channel"  # Replace with your channel username
