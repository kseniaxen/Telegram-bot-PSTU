import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    OPERATOR_CHAT_ID = int(os.getenv("OPERATOR_CHAT_ID", 0))

    BUTTON_KEYS = {
        "main_menu": ["specialties", "documents", "deadlines", "site", "schedule", "contacts", "operator"],
        "specialties_menu": ["bachelor", "specialist", "master", "aspirantura", "back"]
    }