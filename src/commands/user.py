import io
import asyncio

from aiogram import types, F, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.ai_utils import get_tonality, speech_to_text
from db1test import reviews, get_user_reviews, delete_review_db, get_review # тестовый модуль имитирующий функции для бд (арс, работаем)

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
    await callback.message.answer("Введите ваше имя:", reply_markup=keyboard)
    await callback.answer()


async def process_user_name(message: types.Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    
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
    await message.answer("Оцените кофейню (выберите звёзды):", reply_markup=keyboard)


async def process_anonymous(callback: types.CallbackQuery, state: FSMContext):
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
    await callback.message.answer("Оцените кофейню (выберите звёзды):", reply_markup=keyboard)
    await callback.answer()


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
    asyncio.create_task(save_data(data, review))
    await state.clear()


async def view_reviews(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_reviews = get_user_reviews(user_id)
    
    if not user_reviews:
        await callback.message.answer("У вас пока нет отзывов.")
        await callback.answer()
        return
    
    response = "Ваши отзывы:\n"
    for review in user_reviews:
        response += f"№{review['review_id']} | Оценка: {review['mark']} | {review['text']}\n\n"
    
    await callback.message.answer(response, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Удалить отзыв", callback_data="delete_review")],
    ]))
    await callback.answer()


async def delete_review(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_reviews = get_user_reviews(user_id)
    
    if not user_reviews:
        await callback.message.answer("У вас нет отзывов для удаления.")
        await callback.answer()
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Удалить отзыв №{r['review_id']}", callback_data=f"del_{r['review_id']}")]
        for r in user_reviews
    ])
    await callback.message.answer("Выберите отзыв для удаления:", reply_markup=keyboard)
    await callback.answer()


async def confirm_delete(callback: types.CallbackQuery, state: FSMContext):
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


async def save_data(data: dict, review: io.BytesIO | str):
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
        "readed": False
    }

    reviews.append(new_review)
    

def register_handlers(dp):
    dp.message.register(cmd_start, CommandStart())

    dp.callback_query.register(process_add_review, F.data == "add_review")
    dp.message.register(process_user_name, ReviewForm.user_name)
    dp.callback_query.register(process_anonymous, F.data == "anonymous")
    dp.callback_query.register(process_rating, F.data.startswith("rating_"))
    dp.callback_query.register(confirm_rating, F.data == "confirm_rating")
    dp.message.register(process_review, ReviewForm.review)

    dp.callback_query.register(view_reviews, F.data == "view_reviews")

    dp.callback_query.register(delete_review, F.data == "delete_review")
    dp.callback_query.register(confirm_delete, F.data.startswith("del_"))

    dp.message.register(default_cmd)