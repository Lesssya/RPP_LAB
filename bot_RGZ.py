import asyncio
import asyncpg
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove
from dotenv import load_dotenv
import os
from datetime import datetime
import aiohttp

# Загрузка переменных окружения
load_dotenv()

# Инициализация бота и хранилища состояний
bot = Bot(token=os.getenv("BOT_TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

# ================== КЛАВИАТУРЫ ==================
start_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="/add_operation"),
         types.KeyboardButton(text="/operations")],
        [types.KeyboardButton(text="/add_category")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие"
)

type_operation_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="ДОХОД"),
         types.KeyboardButton(text="РАСХОД")]
    ],
    resize_keyboard=True
)

# Добавляем новую клавиатуру для выбора валюты
currency_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="RUB"),
         types.KeyboardButton(text="USD"),
         types.KeyboardButton(text="EUR")]
    ],
    resize_keyboard=True
)


# ================== СОСТОЯНИЯ FSM ==================
class RegistrationState(StatesGroup):
    name = State()


class CategoryState(StatesGroup):
    name = State()


class OperationState(StatesGroup):
    type = State()
    amount = State()
    date = State()
    category = State()

class OperationsState(StatesGroup):
    currency = State()


# ================== БАЗА ДАННЫХ ==================
async def get_db():
    return await asyncpg.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        host=os.getenv("DB_HOST", "localhost")
    )


async def execute(query: str, *args):
    conn = await get_db()
    try:
        await conn.execute(query, *args)
    finally:
        await conn.close()


async def fetchval(query: str, *args):
    conn = await get_db()
    try:
        result = await conn.fetchval(query, *args)
        return result
    finally:
        await conn.close()


async def fetch(query: str, *args):
    conn = await get_db()
    try:
        result = await conn.fetch(query, *args)
        return result
    finally:
        await conn.close()


async def get_currency_rate(currency: str) -> float:
    """Получение курса валюты из вашего микросервиса"""
    if currency == "RUB":
        return 1.0

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://localhost:5000/rate?currency={currency}') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['rate']
                return None
    except Exception as e:
        print(f"Currency service error: {e}")
        return None


# ================== ОБРАБОТЧИКИ КОМАНД ==================
@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    user = await fetchval("SELECT chat_id FROM users WHERE chat_id = $1", message.chat.id)

    if not user:
        await message.answer("🤩 Добро пожаловать! Введите ваше имя для регистрации:")
        await state.set_state(RegistrationState.name)
    else:
        await message.answer(
            "💰 Финансовый менеджер\n\n"
            "Доступные команды:\n"
            "/add_operation - Добавить операцию\n"
            "/add_category - Добавить категорию\n"
            "/operations - Просмотр операций",
            reply_markup=start_keyboard
        )


@router.message(RegistrationState.name)
async def process_registration(message: types.Message, state: FSMContext):
    if not message.text or len(message.text) > 100:
        await message.answer("😔 Пожалуйста, введите корректное имя (максимум 100 символов)")
        return

    try:
        await execute(
            "INSERT INTO users (chat_id, name) VALUES ($1, $2)",
            message.chat.id, message.text.strip()
        )
        await message.answer("Регистрация завершена! ✅", reply_markup=start_keyboard)
    except Exception as e:
        await message.answer("😔✋Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.")
        print(f"Registration error: {e}")
    finally:
        await state.clear()


@router.message(Command("add_category"))
async def add_category(message: types.Message, state: FSMContext):
    await message.answer("✍️ Введите название категории:",
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(CategoryState.name)


@router.message(CategoryState.name)
async def process_category_name(message: types.Message, state: FSMContext):
    if not message.text or len(message.text) > 50:
        await message.answer("❌ Название категории должно быть от 1 до 50 символов.Введите еще раз")
        return

    try:
        existing = await fetchval(
            "SELECT id FROM categories WHERE chat_id = $1 AND name = $2",
            message.chat.id, message.text.strip()
        )

        if existing:
            await message.answer("❌ Эта категория уже существует! Выберите операцию заново, ",
                                 reply_markup=start_keyboard)
        else:
            await execute(
                "INSERT INTO categories (name, chat_id) VALUES ($1, $2)",
                message.text.strip(), message.chat.id
            )
            await message.answer(f"Категория «{message.text}» добавлена! ✅",
                                 reply_markup=start_keyboard)
    except Exception as e:
        await message.answer("‼️ Произошла ошибка при добавлении категории.")
        print(f"Category error: {e}")
    finally:
        await state.clear()


@router.message(Command("operations"))
async def show_operations(message: types.Message, state: FSMContext):
    # Проверяем, что пользователь зарегистрирован
    user = await fetchval("SELECT chat_id FROM users WHERE chat_id = $1", message.chat.id)

    if not user:
        await message.answer("⚠️Сначала зарегистрируйтесь с помощью команды /start")
        return

    # Предлагаем выбрать валюту
    await message.answer("💸 Выберите валюту для отображения операций:",
                         reply_markup=currency_keyboard)
    await state.set_state(OperationsState.currency)


@router.message(OperationsState.currency)
async def process_currency_choice(message: types.Message, state: FSMContext):
    if message.text not in ["RUB", "USD", "EUR"]:
        await message.answer("💰 Пожалуйста, выберите валюту из предложенных вариантов")
        return

    selected_currency = message.text

    # Получаем курс валюты
    rate = await get_currency_rate(selected_currency)
    if rate is None and selected_currency != "RUB":
        await message.answer("😥 Не удалось получить курс валюты. Показываю в RUB",
                             reply_markup=start_keyboard)
        selected_currency = "RUB"
        rate = 1.0

    # Получаем все операции пользователя
    operations = await fetch(
        """SELECT o.date, o.sum, o.type_operation, c.name as category 
        FROM operations o
        JOIN categories c ON o.category_id = c.id
        WHERE o.chat_id = $1
        ORDER BY o.date DESC""",
        message.chat.id
    )

    if not operations:
        await message.answer("🙏 У вас пока нет операций", reply_markup=start_keyboard)
        await state.clear()
        return

    # Формируем сообщение с операциями
    response = f"📊 Ваши операции ({selected_currency}):\n\n"
    total_income = 0
    total_expense = 0

    for op in operations:
        # Конвертируем сумму в выбранную валюту
        converted_amount = round(float(op['sum']) / rate, 2)

        if op['type_operation'] == "ДОХОД":
            total_income += converted_amount
            operation_type = "➕"
        else:
            total_expense += converted_amount
            operation_type = "➖"

        response += (
            f"{operation_type} {op['date'].strftime('%d.%m.%Y')} - "
            f"{converted_amount} {selected_currency}\n"
            f"Категория: {op['category']}\n\n"
        )

    # Добавляем итоги
    response += (
        f"Итоговый баланс (доходы минус расходы): {round(total_income - total_expense, 2)} {selected_currency}"
    )

    await message.answer(response, reply_markup=start_keyboard)
    await state.clear()


@router.message(Command("add_operation"))
async def add_operation(message: types.Message, state: FSMContext):
    await message.answer("Выберите тип операции:", reply_markup=type_operation_keyboard)
    await state.set_state(OperationState.type)


@router.message(OperationState.type)
async def process_type(message: types.Message, state: FSMContext):
    if message.text not in ["ДОХОД", "РАСХОД"]:
        await message.answer("Пожалуйста, используйте кнопки для выбора типа операции!")
        return

    await state.update_data(type=message.text)
    await message.answer("Введите сумму:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(OperationState.amount)


@router.message(OperationState.amount)
async def process_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',', '.'))
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
    except (ValueError, AttributeError):
        await message.answer("Пожалуйста, введите корректную сумму (положительное число без пробелов и знаков)")
        return

    await state.update_data(amount=amount)
    await message.answer("Введите дату в формате ДД.ММ.ГГГГ (или нажмите кнопку 'Сегодня'):",
                         reply_markup=types.ReplyKeyboardMarkup(
                             keyboard=[[types.KeyboardButton(text="Сегодня")]],
                             resize_keyboard=True
                         ))
    await state.set_state(OperationState.date)


@router.message(OperationState.date)
async def process_date(message: types.Message, state: FSMContext):
    if message.text.lower() == "сегодня":
        date = datetime.now().date()
    else:
        try:
            date = datetime.strptime(message.text, "%d.%m.%Y").date()
            if date > datetime.now().date():
                await message.answer("Дата не может быть в будущем!")
                return
        except ValueError:
            await message.answer("Неверный формат даты! Используйте ДД.ММ.ГГГГ")
            return

    await state.update_data(date=date)

    try:
        categories = await fetch(
            "SELECT name FROM categories WHERE chat_id = $1 ORDER BY name",
            message.chat.id
        )
    except Exception as e:
        await message.answer("Произошла ошибка при загрузке категорий.")
        print(f"Categories load error: {e}")
        await state.clear()
        return

    if not categories:
        await message.answer("❌ Нет доступных категорий. Создайте через /add_category",
                            reply_markup=start_keyboard)
        await state.clear()
        return

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=cat['name'])] for cat in categories],
        resize_keyboard=True
    )

    await message.answer("Выберите категорию:", reply_markup=keyboard)
    await state.set_state(OperationState.category)


@router.message(OperationState.category)
async def process_category(message: types.Message, state: FSMContext):
    data = await state.get_data()

    try:
        category_id = await fetchval(
            "SELECT id FROM categories WHERE chat_id = $1 AND name = $2",
            message.chat.id, message.text.strip()
        )

        if not category_id:
            await message.answer("❌ Категория не найдена! Пожалуйста, выберите из списка.")
            return

        await execute(
            """INSERT INTO operations 
            (date, sum, chat_id, type_operation, category_id)
            VALUES ($1, $2, $3, $4, $5)""",
            data['date'], data['amount'], message.chat.id,
            data['type'], category_id
        )

        await message.answer(
            f"✅ Операция добавлена!\n"
            f"Тип: {data['type']}\n"
            f"Сумма: {data['amount']} руб.\n"
            f"Дата: {data['date'].strftime('%d.%m.%Y')}\n"
            f"Категория: {message.text}",
            reply_markup=start_keyboard
        )
    except Exception as e:
        await message.answer("Произошла ошибка при сохранении операции. Пожалуйста, попробуйте позже.")
        print(f"Operation save error: {e}")
    finally:
        await state.clear()


# ================== ЗАПУСК БОТА ==================
async def main():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Bot error: {e}")
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())