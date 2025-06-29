from aiogram import Router, types
from utils import load_texts

TEXTS = load_texts()
router = Router()

# Универсальный обработчик
async def send_section(message: types.Message, section_name: str):
    section = TEXTS[section_name]
    if "values" in section["data"]:
        content = "\n\n".join(section["data"]["values"])
    else:
        content = "\n\n".join(f"<b>{item['name']}:</b> {item['value']}" for item in section["data"])

    response = f"{section['title']}\n\n{content}"
    if section.get("extra"):
        response += f"\n\n{section['extra']}"
    await message.answer(response, parse_mode="HTML")

# Регистрация всех обработчиков
sections = ["documents", "schedule", "site", "contacts", "deadlines"]
for section in sections:
    @router.message(lambda msg, sec=section: msg.text == TEXTS["buttons"][sec])
    async def handler(message: types.Message, sec=section):
        await send_section(message, sec)