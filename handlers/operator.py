from aiogram import Router, types
from config import Config
from utils import load_texts

TEXTS = load_texts()
router = Router()
