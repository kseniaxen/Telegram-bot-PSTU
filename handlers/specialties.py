from aiogram import Router, types
from keyboards import specialties_menu
from utils import load_texts

TEXTS = load_texts()
router = Router()

@router.message(lambda msg: msg.text == TEXTS["buttons"]["specialties"])
async def show_specialties_menu(message: types.Message):
    await message.answer(TEXTS["specialties"]["title"], reply_markup=specialties_menu, parse_mode="HTML")

@router.message(lambda msg: msg.text in [
    TEXTS["buttons"]["bachelor"],
    TEXTS["buttons"]["specialist"],
    TEXTS["buttons"]["master"],
    TEXTS["buttons"]["aspirantura"]
])

async def handle_specialties(message: types.Message):
    info = TEXTS["specialties"]["extra"]["info_main"]
    match message.text:
        case text if text == TEXTS["buttons"]["bachelor"]:
            programs = TEXTS["specialties"]["data"]["bachelor"]
            title = "🎓 <b>Программы бакалавриата:</b>"
        case text if text == TEXTS["buttons"]["specialist"]:
            programs = TEXTS["specialties"]["data"]["specialist"]
            title = "📚 <b>Программы специалитета:</b>"
        case text if text == TEXTS["buttons"]["master"]:
            programs = TEXTS["specialties"]["data"]["master"]
            title = "👨‍🎓 <b>Программы магистратуры:</b>"
        case text if text == TEXTS["buttons"]["aspirantura"]:
            programs = TEXTS["specialties"]["data"]["aspirantura"]
            title = "👨‍🔬 <b>Программы аспирантуры:</b>"
            info = TEXTS["specialties"]["extra"]["info_asp"]
        case _:
            await message.answer("Неизвестная команда", reply_markup=specialties_menu)
            return

    response = (
            f"{title}\n\n" +
            "\n".join(f"• {program}" for program in programs) +
            f"\n\n{info}"
    )

    await message.answer(
        response,
        reply_markup=specialties_menu,
        parse_mode="HTML",
        disable_web_page_preview=True
    )