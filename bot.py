import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image, ImageDraw, ImageFont

# --- Берём токен из Render Environment ---
API_TOKEN = os.getenv("API_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Храним дату пользователя
user_data = {}

# --- Кнопки ---
start_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton("Получить расчёт", callback_data="get_calc")
)

profession_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton("Получить расчет профессии (500₽)", callback_data="get_prof")
)

consult_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton("Записаться на консультацию (15000₽)", url="https://prodamus.ru/your-link")
)

# --- Хэндлеры ---
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот-нумеролог.\n"
        "Я помогу рассчитать твой квадрат Пифагора.\n\n"
        "Нажми кнопку ниже:",
        reply_markup=start_kb
    )

@dp.callback_query_handler(lambda c: c.data == "get_calc")
async def ask_birthdate(callback: types.CallbackQuery):
    await callback.message.answer("Введите дату рождения в формате ДД.MM.ГГГГ")
    await callback.answer()

@dp.message_handler(regexp=r"^\d{2}\.\d{2}\.\d{4}$")
async def calc_square(message: types.Message):
    date = message.text
    user_data[message.from_user.id] = date

    img_path = generate_square(date)

    await message.answer_photo(open(img_path, "rb"), caption="Вот твой квадрат Пифагора ✨")
    await message.answer("Хочешь узнать профессию по дате рождения?", reply_markup=profession_kb)

@dp.callback_query_handler(lambda c: c.data == "get_prof")
async def process_prof(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    date = user_data.get(user_id)

    if not date:
        await callback.message.answer("Сначала введи дату рождения 🙃")
        return

    # пока эмуляция успешной оплаты
    await callback.message.answer("✅ Оплата прошла успешно (демо-режим)\n\n" + get_profession(date))
    await callback.message.answer("Также доступна полная консультация с Алексеем Болтаевым:", reply_markup=consult_kb)
    await callback.answer()

# --- Логика расчетов ---
def get_digits(date: str):
    """Получаем список всех цифр без нулей"""
    return [int(d) for d in date if d.isdigit() and d != "0"]

def calc_work_numbers(date: str):
    digits = get_digits(date)
    first = sum(digits)
    second = sum(map(int, str(first)))
    first_digit = int(date[0])
    third = first - (first_digit * 2)
    fourth = sum(map(int, str(third)))
    return [first, second, third, fourth]

def generate_square(date: str) -> str:
    digits = get_digits(date)
    work_nums = calc_work_numbers(date)
    all_nums = digits + [int(d) for d in "".join(map(str, work_nums)) if d != "0"]

    # считаем сколько раз каждая цифра встречается
    counts = {str(i): all_nums.count(i) for i in range(1, 10)}

    # рисуем картинку 3х3
    img = Image.new("RGB", (300, 300), "white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    # координаты клеток
    cells = [
        (0, 0), (100, 0), (200, 0),
        (0, 100), (100, 100), (200, 100),
        (0, 200), (100, 200), (200, 200),
    ]

    idx = 1
    for (x, y) in cells:
        draw.rectangle([x, y, x + 100, y + 100], outline="black", width=2)
        draw.text((x + 40, y + 40), str(counts[str(idx)]), fill="black", font=font)
        idx += 1

    path = f"square_{date.replace('.', '')}.png"
    img.save(path)
    return path

def get_profession(date: str) -> str:
    digits = get_digits(date)
    first = sum(digits)
    second = sum(map(int, str(first)))
    first_digit = int(date[0])
    third = first - (first_digit * 2)
    fourth = sum(map(int, str(third)))

    return (
        f"🔮 Расчет профессии по дате {date}\n\n"
        f"Первое число: {first}\n"
        f"Второе число: {second}\n"
        f"Третье число: {third}\n"
        f"Четвертое число: {fourth}\n\n"
        f"👉 Эти числа показывают твои сильные стороны и подходящие сферы деятельности."
    )

# --- Запуск ---
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
