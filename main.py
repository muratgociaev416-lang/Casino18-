import asyncio
import logging
import random
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в переменных окружения")

MEDIA_PATH = "media"

# Хранилище пользователей: {user_id: {"balance": int, "level": int}}
users = {}

# Уровни раздевания (от 8 до 0)
LEVELS = {
    8: "👗 Полностью одета",
    7: "🧥 Сняла верх",
    6: "👖 Без штанов",
    5: "👕 В майке",
    4: "🩲 В белье",
    3: "🍒 Без лифчика",
    2: "😳 Почти голая",
    1: "💦 Полностью голая",
    0: "🔥 Постельная сцена"
}

def main_menu():
    """Главное меню с кнопками"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎰 Играть (50)", callback_data="play")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="🔄 Новая девушка", callback_data="reset")]
    ])

async def get_media(folder: str):
    """
    Возвращает случайный файл (изображение/видео) из указанной подпапки MEDIA_PATH.
    Поддерживаются расширения: .jpg, .jpeg, .png, .mp4, .gif
    """
    path = os.path.join(MEDIA_PATH, folder)
    if not os.path.exists(path):
        logging.warning(f"Папка не существует: {path}")
        return None

    allowed_extensions = ('.jpg', '.jpeg', '.png', '.mp4', '.gif')
    files = [
        f for f in os.listdir(path)
        if f.lower().endswith(allowed_extensions)
    ]
    
    if not files:
        logging.warning(f"В папке {path} нет подходящих файлов")
        return None

    chosen = random.choice(files)
    return FSInputFile(os.path.join(path, chosen))

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    uid = str(message.from_user.id)
    if uid not in users:
        users[uid] = {"balance": 9_999_999, "level": 8}  # 9 999 999 монет
    await message.answer(
        "🎰 <b>Казино на Раздевание 18+</b>\n\n"
        "Выигрывай — раздевай девушку!",
        reply_markup=main_menu()
    )

@dp.callback_query(F.data == "play")
async def play(callback: CallbackQuery):
    uid = str(callback.from_user.id)
    
    if uid not in users:
        users[uid] = {"balance": 9_999_999, "level": 8}  # 9 999 999 монет
    
    if users[uid]["balance"] < 50:
        await callback.answer("❌ Недостаточно монет!", show_alert=True)
        return
    
    users[uid]["balance"] -= 50
    win = random.random() < 0.57  # 57% шанс выигрыша
    
    level = users[uid]["level"]
    media = None
    text = ""
    
    if win and level > 0:
        users[uid]["level"] -= 1
        new_level = users[uid]["level"]
        text = f"🎉 Выигрыш! Она раздевается...\n\n{LEVELS[new_level]}"
        media = await get_media("strip")
    
    elif win and level == 0:
        text = "🔥 Постельная сцена! Она полностью твоя..."
        media = await get_media("bed")
    
    else:
        text = "😔 Проигрыш..."
    
    if media:
        try:
            if str(media).lower().endswith(('.mp4', '.gif')):
                await callback.message.answer_video(media, caption=text)
            else:
                await callback.message.answer_photo(media, caption=text)
        except Exception as e:
            logging.error(f"Ошибка отправки медиа: {e}")
            await callback.message.answer(text + "\n\n⚠️ Не удалось загрузить изображение.")
    else:
        await callback.message.answer(text)
    
    await callback.message.answer(
        f"💰 Баланс: {users[uid]['balance']} монет\n"
        f"👠 Уровень: {LEVELS.get(users[uid]['level'], '?')}",
        reply_markup=main_menu()
    )
    
    await callback.answer()

@dp.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):
    uid = str(callback.from_user.id)
    user_data = users.get(uid, {"balance": 9_999_999, "level": 8})  # значение по умолчанию
    await callback.message.answer(
        f"💰 Баланс: {user_data['balance']}\n"
        f"👠 Уровень девушки: {LEVELS.get(user_data['level'], '?')}"
    )
    await callback.answer()

@dp.callback_query(F.data == "reset")
async def reset(callback: CallbackQuery):
    uid = str(callback.from_user.id)
    if uid in users:
        users[uid]["level"] = 8
        await callback.answer("✅ Новая девушка! Уровень сброшен.", show_alert=True)
    else:
        await callback.answer("❌ Вы не зарегистрированы. Напишите /start", show_alert=True)

async def main():
    logging.basicConfig(level=logging.INFO)
    print("🎰 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
