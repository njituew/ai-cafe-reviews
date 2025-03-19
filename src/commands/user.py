import os
import io

from aiogram import types, F, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class ReviewForm(StatesGroup):
    user_name = State()
    rating = State()
    review = State()


async def default_cmd(message: types.Message):
    await message.answer(message.text)


async def cmd_start(message: types.Message):
    await message.answer(
        "Здравствуйте!\n\nЯ - MuffinMate. Выслушиваю ваши впечатления после посещения кофейни MuffinMate."
    )
    await choose_action(message)


async def choose_action(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оставить отзыв", callback_data="add_review")],
        [InlineKeyboardButton(text="Удалить отзыв", callback_data="delete_review")],
        [InlineKeyboardButton(text="Мои отзывы", callback_data="view_reviews")]
    ])
    
    await message.answer("Выберите действие:", reply_markup=keyboard)


async def process_add_review(callback: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Остаться анонимным", callback_data="anonymous")]
    ])

    await state.set_state(ReviewForm.user_name)
    await callback.message.answer(
        "Как вас зовут?",
        reply_markup=keyboard
    )
    await callback.answer()


async def process_user_name(message: types.Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1", callback_data="rating_1")],
        [InlineKeyboardButton(text="2", callback_data="rating_2")],
        [InlineKeyboardButton(text="3", callback_data="rating_3")],
        [InlineKeyboardButton(text="4", callback_data="rating_4")],
        [InlineKeyboardButton(text="5", callback_data="rating_5")],
    ])
    
    await state.set_state(ReviewForm.rating)
    await message.answer("Оцените кофейню от 1 до 5:", reply_markup=keyboard)


async def process_anonymous(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(user_name="Аноним")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1", callback_data="rating_1")],
        [InlineKeyboardButton(text="2", callback_data="rating_2")],
        [InlineKeyboardButton(text="3", callback_data="rating_3")],
        [InlineKeyboardButton(text="4", callback_data="rating_4")],
        [InlineKeyboardButton(text="5", callback_data="rating_5")],
    ])
    
    await state.set_state(ReviewForm.rating)
    await callback.message.answer("Оцените кофейню от 1 до 5:", reply_markup=keyboard)
    await callback.answer()


async def process_rating(callback: types.CallbackQuery, state: FSMContext):
    rating = int(callback.data.split("_")[1])
    await state.update_data(rating=rating)
    
    await state.set_state(ReviewForm.review)
    await callback.message.answer("Напишите ваш отзыв или отправьте голосовое сообщение:")
    await callback.answer()


async def process_review(message: types.Message, state: FSMContext, bot: Bot):
    if message.text:
        await state.update_data(review=message.text)
    elif message.voice:
        voice_file = await bot.get_file(message.voice.file_id)
        buf = io.BytesIO()

        await voice_file.download(out=buf)

        buf.name = "voice.oga"
        buf.seek(0)

        # process voice file and save tonal

        await state.update_data(review=f"Голосовое сообщение")
    else:
        await message.answer("Пожалуйста, отправьте текст или голосовое сообщение.")
        return
    
    save_data(await state.get_data())
    
    await message.answer("Спасибо за отзыв!")
    await state.clear()


def save_data(data):
    print(data) # save to db


def register_handlers(dp):
    dp.message.register(cmd_start, CommandStart())

    dp.callback_query.register(process_add_review, F.data == "add_review")
    dp.message.register(process_user_name, ReviewForm.user_name)
    dp.callback_query.register(process_anonymous, F.data == "anonymous")
    dp.callback_query.register(process_rating, ReviewForm.rating)
    dp.message.register(process_review, ReviewForm.review)

    dp.message.register(default_cmd)