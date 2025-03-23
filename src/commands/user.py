import io
import asyncio
import json

from aiogram import types, F, Bot, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from src.ai_utils import get_tonality, speech_to_text
from src.logger import logger
from db.utils import *

with open("managers.json", "r") as f:
    managers_data = json.load(f)
    managers = [mgr["chat_id"] for mgr in managers_data["managers"]]


class ReviewForm(StatesGroup):
    user_name = State()
    rating = State()
    review = State()


user_router = Router()

@user_router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Здравствуйте!\n\nЯ - MuffinMate. Выслушиваю ваши впечатления после посещения кофейни MuffinMate."
    )
    await choose_action(message)


@user_router.message(F.text == "Оставить отзыв")
async def process_add_review(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Остаться анонимным", callback_data="anonymous")]
    ])
    await state.set_state(ReviewForm.user_name)
    await message.answer("Введите ваше имя:", reply_markup=keyboard)


@user_router.message(ReviewForm.user_name)
@user_router.callback_query(F.data == "anonymous")
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


@user_router.callback_query(F.data.startswith("rating_"))
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


@user_router.callback_query(F.data == "confirm_rating")
async def confirm_rating(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    rating = data.get("temp_rating")
    
    await state.update_data(rating=rating)
    await state.set_state(ReviewForm.review)
    await callback.message.edit_text(f"Оценка принята! Вы поставили {rating} из 5\n\nНапишите отзыв или отправьте голосовое сообщение:")
    await callback.answer()


@user_router.message(ReviewForm.review)
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
    logger.info(f"Пользователь {data['user_id']} оставил новый отзыв")
    asyncio.create_task(save_data(data, review, bot))
    await state.clear()


@user_router.message(F.text == "Мои отзывы")
async def view_reviews(message: types.Message):
    user_id = message.from_user.id
    user_reviews = await get_user_reviews(user_id)
    
    if not user_reviews:
        await message.answer("У вас пока нет отзывов.")
        return
    
    response = "Ваши отзывы:\n\n"
    for i, review in enumerate(user_reviews, 1):
        response += f"Отзыв №{i} от {review.created_at.strftime('%d.%m.%Y %H:%M')} | Оценка: {review.rating} | {review.text}\n\n"
    
    await message.answer(response)


@user_router.message(F.text == "Удалить отзыв")
async def process_delete_review(message: types.Message):
    user_id = message.from_user.id
    user_reviews = await get_user_reviews(user_id)
    
    if not user_reviews:
        await message.answer("У вас нет отзывов для удаления.")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Удалить отзыв №{i}", callback_data=f"del_{r.id}")]
        for i, r in enumerate(user_reviews, 1)
    ])
    await message.answer("Выберите отзыв для удаления:", reply_markup=keyboard)


@user_router.callback_query(F.data.startswith("del_"))
async def confirm_delete(callback: types.CallbackQuery):
    review_id = int(callback.data.split("_")[1])
    review = await get_review(review_id)
    
    if not review:
        await callback.message.answer("Этот отзыв не найден")
        await callback.answer()
        return
    
    try:
        await delete_review(review)
        await callback.message.answer(f"Отзыв успешно удалён!")
        logger.info(f"Пользователь {callback.from_user.id} удалил отзыв {review_id}")
    except Exception as e:
        await callback.message.answer("Ошибка при удалении отзыва.")
        logger.error(f"Ошибка при удалении отзыва {review_id}: {e}")
    
    await callback.answer()


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


async def save_data(data: dict, review: io.BytesIO | str, bot: Bot):
    if isinstance(review, io.BytesIO):
        review_text = await speech_to_text(review)
    else:
        review_text = review
    
    review_tonality = await get_tonality(review_text)

    new_review = Review(
        user_id=data["user_id"],
        rating=data["rating"],
        text=review_text,
        tonality=review_tonality,
        readed=False,
        answered=False,
        readed_by=None
    )

    await add_review(new_review)

    if review_tonality in [ToneEnum.NEG, ToneEnum.VNEG]:
        await notify_managers_of_negative_review(new_review, data["user_name"], bot)


async def notify_managers_of_negative_review(review: Review, user_name: str, bot: Bot):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ответить", callback_data=f"reply_{review.id}")]
    ])
    message = (
        f"Новый негативный отзыв!\n\n"
        f"Пользователь: {user_name}\n"
        f"ID пользователя: {review.user_id}\n"
        f"Оценка: {review.rating}\n"
        f"Текст: {review.text}\n"
        f"Дата: {review.created_at.strftime('%d.%m.%Y %H:%M')}"
    )
    for manager_id in managers:
        try:
            await bot.send_message(chat_id=manager_id, text=message, reply_markup=keyboard)
            logger.info(f"Отправлено оповещение о негативном отзыве менеджеру {manager_id}")
        except Exception as e:
            logger.warning(f"Ошибка при отправке менеджеру {manager_id}: {e}")


@user_router.message()
async def default_cmd(message: types.Message):
    await message.answer(message.text)


# вывод мои отзывы при удалении отзыва
# роутер
# добавить команду "о нас"
