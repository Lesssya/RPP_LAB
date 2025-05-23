import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Словарь для хранения валют
currencies = {}


# Клавиатура с основными командами
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="/help"), KeyboardButton(text="/list")],
        [KeyboardButton(text="/save_currency"), KeyboardButton(text="/convert")],
        [KeyboardButton(text="/delete_currency"), KeyboardButton(text="/clear_all")]
    ], resize_keyboard=True)
    return keyboard


# Состояния FSM
class CurrencyStates(StatesGroup):
    waiting_for_currency_name = State()
    waiting_for_currency_rate = State()
    waiting_for_convert_currency = State()
    waiting_for_convert_amount = State()
    waiting_for_delete_currency = State()


# Обработчик комнад
# Стартовая команда
@dp.message(Command("start", "help"))
async def cmd_start(message: Message):
    await message.answer(
        "💰 <b>Currency Converter Bot</b> 💰\n\n"
        "Создатель бота приветствует тебя! Этот бот в твоем рапоряжении, "
        "теперь ты можешь спокойно забыть про таблицу умножения, калькулятор и прочие математические приблуды, "
        "и конвертировать валюты курса здесь за пару кликов! \n\n"
        "Список доступных команд:\n"
        "/save_currency - записать/сохранить курс валюты\n"
        "/convert - конвертировать валюту в рубли\n"
        "/list - показать все сохраненные валюты\n"
        "/delete_currency - удалить валюту\n"
        "/clear_all - очистить все данные\n"
        "/help - показать это сообщение",
        reply_markup=get_main_keyboard()
    )


# Список всех валют
@dp.message(Command("list"))
async def cmd_list(message: Message):
    if not currencies:
        await message.answer("Атя-тя у тебя нет сохраненных валют😏.", reply_markup=get_main_keyboard())
        return

    response = "✍️ <b>Список валют:</b>\n"
    for currency, rate in currencies.items():
        response += f"• {currency}: {rate} RUB\n"

    await message.answer(response, reply_markup=get_main_keyboard())


# Удаление валюты
@dp.message(Command("delete_currency"))
async def cmd_delete_currency(message: Message, state: FSMContext):
    if not currencies:
        await message.answer("Нет сохраненных валют чтобы что-то удалять.😯 Сначала сохрани, потом проси☝️", reply_markup=get_main_keyboard())
        return

    await message.answer("😔 Введите название валюты для удаления:", reply_markup=get_main_keyboard())
    await state.set_state(CurrencyStates.waiting_for_delete_currency)


@dp.message(CurrencyStates.waiting_for_delete_currency)
async def process_delete_currency(message: Message, state: FSMContext):
    currency = message.text.upper()
    if currency in currencies:
        del currencies[currency]
        await message.answer(f"Валюта {currency} удалена.👊", reply_markup=get_main_keyboard())
    else:
        await message.answer(f"Валюта {currency} не найдена.🙅‍♀️", reply_markup=get_main_keyboard())
    await state.clear()


# Очистка всех данных
@dp.message(Command("clear_all"))
async def cmd_clear_all(message: Message):
    currencies.clear()
    await message.answer("Все данные о валютах удалены.💁‍♀️", reply_markup=get_main_keyboard())


# Сохранение валюты
@dp.message(Command("save_currency"))
async def cmd_save_currency(message: Message, state: FSMContext):
    await message.answer("💵💴💶💷 Введите название валюты (например, USD, EUR и др.):", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(CurrencyStates.waiting_for_currency_name)


@dp.message(CurrencyStates.waiting_for_currency_name)
async def process_currency_name(message: Message, state: FSMContext):
    currency_name = message.text.upper()
    await state.update_data(currency_name=currency_name)
    await message.answer(f"🔗 Введите курс {currency_name} к рублю (например, 90.5):")
    await state.set_state(CurrencyStates.waiting_for_currency_rate)


@dp.message(CurrencyStates.waiting_for_currency_rate)
async def process_currency_rate(message: Message, state: FSMContext):
    try:
        rate = float(message.text)
        data = await state.get_data()
        currency_name = data['currency_name']
        currencies[currency_name] = rate
        await message.answer(f"✅ Курс {currency_name} сохранён: {rate} RUB", reply_markup=get_main_keyboard())
        await state.clear()
    except ValueError:
        await message.answer("❌ Ошибка! Введите число (например, 90.5).")


# Конвертация валюты
@dp.message(Command("convert"))
async def cmd_convert(message: Message, state: FSMContext):
    if not currencies:
        await message.answer("😧Нет сохранённых валют. Сначала используйте команду /save_currency.💃",
                             reply_markup=get_main_keyboard())
        return

    await message.answer(" 📝 Введите название валюты для конвертации:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(CurrencyStates.waiting_for_convert_currency)


@dp.message(CurrencyStates.waiting_for_convert_currency)
async def process_convert_currency(message: Message, state: FSMContext):
    currency_name = message.text.upper()
    if currency_name not in currencies:
        await message.answer("❌ Валюта не найдена. Попробуйте ещё раз.", reply_markup=get_main_keyboard())
        return

    await state.update_data(currency_name=currency_name)
    await message.answer(f" 🌝 Введите сумму в {currency_name}:")
    await state.set_state(CurrencyStates.waiting_for_convert_amount)


@dp.message(CurrencyStates.waiting_for_convert_amount)
async def process_convert_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        data = await state.get_data()
        currency_name = data['currency_name']
        rate = currencies[currency_name]
        result = amount * rate
        await message.answer(f"💸 {amount} {currency_name} = {result:.2f} RUB", reply_markup=get_main_keyboard())
        await state.clear()
    except ValueError:
        await message.answer("❌ Ошибка! Введите число (например, 100).")


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())