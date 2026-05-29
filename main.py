import asyncio
import logging
import random
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MEDIA_PATH = "media"

users = {}

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
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎰 Играть (50)", callback_data="play")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="🔄 Новая девушка", callback_data="reset")]
    ])

async def get_media(folder):
    path = f"{MEDIA_PATH}/{folder}"
    if not os.path.exists(path):
        return None
    files = [f for f in os.listdir(path) if f.lower().endswith(('.jpg','.png','.mp4','.gif'))]
    if not files:
        return None
    return FSInputFile(f"{path}/{random.choice(files)}")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    uid = str(message.from_user.id)
    if uid not in users:
        users[uid] = {"balance": 2000, "level": 8}
    await message.answer("🎰 <b>Казино на Раздевание 18+</b>\n\nВыигрывай — раздевай девушку!", reply_markup=main_menu())

@dp.callback_query(F.data == "play")
async def play(callback: CallbackQuery):
    uid = str(callback.from_user.id)
    if uid not in users:
        users[uid] = {"balance": 2000, "level": 8}
    
    if users[uid]["balance"] < 50:
        return await callback.answer("❌ Недостаточно монет!", show_alert=True)
    
    users[uid]["balance"] -= 50
    win = random.random() < 0.57

    level = users[uid]["level"]

    if win and level > 0:
        users[uid]["level"] -= 1
        level = users[uid]["level"]
        text = f"🎉 Выигрыш! Она раздевается...\n\n{LEVELS[level]}"
        media = await get_media("strip")
    elif win and level == 0:
        text = "🔥 Постельная сцена! Она полностью твоя..."
        media = await get_media("bed")
    else:
        text = "😔 Проигрыш..."
        media = None

    if media:
        if str(media).lower().endswith(('.mp4','.gif')):
            await callback.message.answer_video(media, caption=text)
        else:
            await callback.message.answer_photo(media, caption=text)
    else:
        await callback.message.answer(text)

    await callback.message.answer(
        f"💰 Баланс: {users[uid]['balance']} монет\n"
        f"👠 Уровень: {LEVELS.get(level)}",
        reply_markup=main_menu()
    )

@dp.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):
    uid = str(callback.from_user.id)
    u = users.get(uid, {"balance": 2000, "level": 8})
    await callback.message.answer(f"💰 Баланс: {u['balance']}\n👠 Уровень девушки: {LEVELS.get(u['level'])}")

@dp.callback_query(F.data == "reset")
async def reset(callback: CallbackQuery):
    uid = str(callback.from_user.id)
    users[uid]["level"] = 8
    await callback.answer("✅ Новая девушка!", show_alert=True)

async def main():
    logging.basicConfig(level=logging.INFO)
    print("🎰 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
