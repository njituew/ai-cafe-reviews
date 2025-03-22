import io
import asyncio
import json

from aiogram import types, F, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from datetime import datetime

from src.ai_utils import get_tonality, speech_to_text
from db1test import reviews, get_user_reviews, delete_review_db, get_review # тестовый модуль имитирующий функции для бд (арс, работаем)
from src.logger import logger

with open("managers.json", "r") as f:
    managers_data = json.load(f)
    managers = [mgr["chat_id"] for mgr in managers_data["managers"]]

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
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Оставить отзыв")],
            [KeyboardButton(text="Удалить отзыв")],
            [KeyboardButton(text="Мои отзывы")]
        ],
        resize_keyboard=True
    )
    
    await message.answer("Выберите действие:", reply_markup=keyboard)


async def process_add_review(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Остаться анонимным", callback_data="anonymous")]
    ])
    await state.set_state(ReviewForm.user_name)
    await message.answer("Введите ваше имя:", reply_markup=keyboard)


async def process_user_name(data: types.Message | types.CallbackQuery, state: FSMContext):
    if isinstance(data, types.Message):
        await state.update_data(user_name=data.text)
    else:
        await state.update_data(user_name="Аноним")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="★ 1", callback_data="rating_1"),
            InlineKeyboardButton(text="★ 2", callback_data="rating_2"),
            InlineKeyboardButton(text="★ 3", callback_data="rating_3"),
            InlineKeyboardButton(text="★ 4", callback_data="rating_4"),
            InlineKeyboardButton(text="★ 5", callback_data="rating_5"),
        ]
    ])
    
    await state.set_state(ReviewForm.rating)

    if isinstance(data, types.Message):
        await data.answer("Оцените кофейню:", reply_markup=keyboard)
    else:
        await data.message.answer("Оцените кофейню:", reply_markup=keyboard)
        await data.answer()


async def process_rating(callback: types.CallbackQuery, state: FSMContext):
    rating = int(callback.data.split("_")[1])
    await state.update_data(temp_rating=rating)

    stars = [
        InlineKeyboardButton(text="🌟 1", callback_data="rating_1") if rating >= 1 else InlineKeyboardButton(text="★ 1", callback_data="rating_1"),
        InlineKeyboardButton(text="🌟 2", callback_data="rating_2") if rating >= 2 else InlineKeyboardButton(text="★ 2", callback_data="rating_2"),
        InlineKeyboardButton(text="🌟 3", callback_data="rating_3") if rating >= 3 else InlineKeyboardButton(text="★ 3", callback_data="rating_3"),
        InlineKeyboardButton(text="🌟 4", callback_data="rating_4") if rating >= 4 else InlineKeyboardButton(text="★ 4", callback_data="rating_4"),
        InlineKeyboardButton(text="🌟 5", callback_data="rating_5") if rating >= 5 else InlineKeyboardButton(text="★ 5", callback_data="rating_5"),
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        stars,
        [InlineKeyboardButton(text="Готово", callback_data="confirm_rating")]
    ])
    await callback.message.edit_text(f"Ваша оценка: {rating} из 5", reply_markup=keyboard)
    await callback.answer()


async def confirm_rating(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    rating = data.get("temp_rating")
    
    await state.update_data(rating=rating)
    await state.set_state(ReviewForm.review)
    await callback.message.edit_text(f"Оценка принята! Вы поставили {rating} из 5\n\nНапишите отзыв или отправьте голосовое сообщение:")
    await callback.answer()


async def process_review(message: types.Message, state: FSMContext, bot: Bot):
    review = None
    data = await state.get_data()
    data["user_id"] = message.from_user.id

    if message.text:
        review = message.text
    elif message.voice:
        voice_file = await bot.get_file(message.voice.file_id)
        file_path = voice_file.file_path
        
        buf = io.BytesIO()
        await bot.download_file(file_path, destination=buf)
        buf.name = "voice.oga"
        buf.seek(0)

        review = buf
    else:
        await message.answer("Пожалуйста, отправьте текст или голосовое сообщение.")
        return
    
    await message.answer("Спасибо за отзыв!")
    asyncio.create_task(save_data(data, review, bot))
    await state.clear()


async def view_reviews(message: types.Message):
    user_id = message.from_user.id
    user_reviews = get_user_reviews(user_id)
    
    if not user_reviews:
        await message.answer("У вас пока нет отзывов.")
        return
    
    response = "Ваши отзывы:\n\n"
    for i in range(len(user_reviews)):
        review = user_reviews[i]
        response += f"Отзыв №{i + 1} от {review['date']} | Оценка: {review['rating']} | {review['text']}\n\n"
    
    await message.answer(response)


async def delete_review(message: types.Message):
    user_id = message.from_user.id
    user_reviews = get_user_reviews(user_id)
    
    if not user_reviews:
        await message.answer("У вас нет отзывов для удаления.")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Удалить отзыв №{i + 1}", callback_data=f"del_{user_reviews[i]['review_id']}")]
        for i in range(len(user_reviews))
    ])
    await message.answer("Выберите отзыв для удаления:", reply_markup=keyboard)


async def confirm_delete(callback: types.CallbackQuery):
    review_id = int(callback.data.split("_")[1])
    review = get_review(review_id)
    
    if not review:
        await callback.message.answer("Этот отзыв не найден")
        await callback.answer()
        return
    
    if delete_review_db(review_id):
        await callback.message.answer(f"Отзыв успешно удалён!")
    else:
        await callback.message.answer("Ошибка при удалении отзыва.")
    await callback.answer()


async def save_data(data: dict, review: io.BytesIO | str, bot: Bot):
    global reviews
    if isinstance(review, io.BytesIO):
        review_text = await speech_to_text(review)
    else:
        review_text = review
    
    review_tonality = await get_tonality(review_text)

    new_review = {
        "review_id": len(reviews) + 1,
        "user_id": data["user_id"],
        "rating": data["rating"],
        "text": review_text,
        "tonality": review_tonality,
        "readed": False,
        "date": datetime.now().strftime("%d.%m.%Y %H:%M")
    }

    reviews.append(new_review)

    if review_tonality in ["Negative", "Very Negative"]:
        message = (
            f"Новый негативный отзыв!\n\n"
            f"Пользователь: {data['user_name']}\n"
            f"ID пользователя: {data['user_id']}\n"
            f"Оценка: {new_review['rating']}\n"
            f"Текст: {review_text}\n"
            f"Дата: {new_review['date']}"
        )
        for manager_id in managers:
            try:
                await bot.send_message(chat_id=manager_id, text=message)
            except Exception as e:
                logger.warning(f"Ошибка при отправке менеджеру {manager_id}: {e}")
    

def register_handlers(dp):
    dp.message.register(cmd_start, CommandStart())

    dp.message.register(process_add_review, F.text == "Оставить отзыв")
    dp.message.register(process_user_name, ReviewForm.user_name)
    dp.callback_query.register(process_user_name, F.data == "anonymous")
    dp.callback_query.register(process_rating, F.data.startswith("rating_"))
    dp.callback_query.register(confirm_rating, F.data == "confirm_rating")
    dp.message.register(process_review, ReviewForm.review)

    dp.message.register(view_reviews,F.text == "Мои отзывы")

    dp.message.register(delete_review, F.text == "Удалить отзыв")
    dp.callback_query.register(confirm_delete, F.data.startswith("del_"))

    dp.message.register(default_cmd)