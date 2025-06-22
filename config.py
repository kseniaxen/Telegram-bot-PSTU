import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    SUPPORT_TEAM_CHAT_ID = int(os.getenv("SUPPORT_TEAM_CHAT_ID", 0))
    BOT_ID = int(BOT_TOKEN.split(":")[0])  # Получаем ID из токена

    BUTTON_KEYS = {
        "main_menu": ["specialties", "documents", "deadlines", "site", "schedule", "contacts", "unique_code"], #"operator"
        "specialties_menu": ["bachelor", "specialist", "master", "aspirantura", "back"]
    }