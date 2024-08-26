from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from key import api


bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())


kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text='Рассчитать')
kb.add(button)

kb2 = InlineKeyboardMarkup()
button2 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button3 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')

kb2.add(button2)
kb2.add(button3)


class UserState(StatesGroup):

    age = State()
    growth = State()
    weight = State()

@dp.message_handler(text = 'Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию', reply_markup=kb2)

@dp.callback_query_handler(text='formulas')
async def formul(call):
    await call.message.answer('Формула Миффлина-Сан Жеора: для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5.')
    await call.answer()

@dp.callback_query_handler(text = 'calories') # хэндлер перехватил текст
async def set_age(call):
    await call.message.answer('Введите свой возраст.') # Реакция на текст
    await call.answer()
    await UserState.age.set() # установка состояния


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост(см).')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес(кг).')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()  # data это элемент с помощью которого мы получаем наши данные из состояния.
    w = data["weight"]
    g = data["growth"]
    a = data["age"]
    calories = 10 * int(w) + int(6.25) * int(g) - 5 * int(a) + 5
    await message.answer(f'Итого! {calories} ккал в сутки твоя норма.')
    await state.finish()





@dp.message_handler(commands = ['start'])
async def start_message(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью! Для начала расчета суточной калорийности '
                         'нажми Рассчитать', reply_markup=kb)






@dp.message_handler()
async def all_message(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)