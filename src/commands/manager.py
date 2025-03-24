from aiogram import types, F, Router, BaseMiddleware, Bot
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile, BotCommand
)

from db.utils import is_manager
from src.logger import logger
# from src.graph import *
import src.graph as graph
import db.utils as db
import src.ai_utils as ai

from datetime import datetime, timedelta


class ManagerForm(StatesGroup):
    waiting_for_manager_reply = State()
    waiting_for_custom_query = State()


class ManagerCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = event.chat.id if isinstance(event, types.Message) else event.from_user.id
        if not await is_manager(user_id):
            if isinstance(event, types.Message):
                await event.answer("Вы не менеджер")
            elif isinstance(event, types.CallbackQuery):
                await event.answer("Вы не менеджер", show_alert=True)
            logger.warning(f"Попытка доступа не менеджером: {user_id}")
            return
        return await handler(event, data)


manager_router = Router()
manager_router.message.middleware(ManagerCheckMiddleware())
manager_router.callback_query.middleware(ManagerCheckMiddleware())


@manager_router.message(Command("manager"))
async def manager_panel(message: types.Message):
    """
    Открывает панель менеджера

    Args:
        message (types.Message): сообщение
    """
    user_id = message.chat.id

    logger.info(f"Менеджер {user_id} открыл панель менеджера")
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Непрочитанные отзывы 🗣️")],
            [KeyboardButton(text="Дашборд 💻")],
            [KeyboardButton(text="Статистика менеджеров 👩‍💼")]
        ],
        resize_keyboard=True
    )
    await message.answer("Панель менеджера открыта", reply_markup=keyboard)


@manager_router.message(Command("dashboard"))
@manager_router.message(F.text == "Дашборд 💻")
async def dashboard_panel(message: types.Message):
    """
    Открывает панель дашборда

    Args:
        callback_query (types.CallbackQuery): обратный вызов
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Распределение оценок 🌟", callback_data="graph_distribution_of_ratings")],
        [InlineKeyboardButton(text="Динамика удовлетворённости 📈", callback_data="graph_dynamics_of_satisfaction")],
        [InlineKeyboardButton(text="Количество отзывов 📊", callback_data="graph_number_of_reviews")],
        [InlineKeyboardButton(text="Произвольный запрос", callback_data="custom_query")]
    ])
    await message.answer("Выберите график:", reply_markup=keyboard)


@manager_router.callback_query(F.data == "graph_distribution_of_ratings")
async def graph_distribution_of_ratings(callback_query: types.CallbackQuery):
    """
    Отображает распределение оценок

    Args:
        message (types.Message): сообщение
    """
    buffer = await graph.distribution_of_ratings()
    await callback_query.message.answer_photo(
        photo=BufferedInputFile(buffer.getvalue(), filename="graph.png"),
        caption="Распределение оценок 🌟"
    )
    await callback_query.answer()
    

@manager_router.callback_query(F.data == "graph_dynamics_of_satisfaction")
async def graph_dynamics_of_satisfaction(callback_query: types.CallbackQuery):
    """
    Отображает динамику удовлетворённости

    Args:
        message (types.Message): сообщение
    """
    buffer = await graph.dynamics_of_satisfaction()
    await callback_query.message.answer_photo(
        photo=BufferedInputFile(buffer.getvalue(), filename="graph.png"),
        caption="Динамика удовлетворённости 📈"
    )
    await callback_query.answer()


@manager_router.message(Command("unread_reviews"))
@manager_router.message(F.text == "Непрочитанные отзывы 🗣️")
@manager_router.callback_query(F.data.startswith("unread_reviews_page_"))
async def unread_reviews(message_or_callback: types.Message | types.CallbackQuery):
    """
    Отображает список непрочитанных отзывов.
    Если сообщение - открывает первую страницу, если callback - открывает нужную страницу

    Args:
        message_or_callback (types.Message | types.CallbackQuery): сообщение или callback-запрос (🩼)
    """
    user_id = message_or_callback.chat.id if isinstance(message_or_callback, types.Message) else message_or_callback.from_user.id

    # определяем текущую страницу
    if isinstance(message_or_callback, types.Message):
        page = 0
    else:
        page = int(message_or_callback.data.split("_")[3])
    
    logger.info(f"Менеджер {user_id} открыл список непрочитанных отзывов (страница {page})")

    text, keyboard = await get_reviews_page(page)
    if keyboard is None:
        if isinstance(message_or_callback, types.Message):
            await message_or_callback.answer(text)
        else:
            await message_or_callback.message.edit_text(text)
    else:
        if isinstance(message_or_callback, types.Message):
            await message_or_callback.answer(text, reply_markup=keyboard)
        else:
            await message_or_callback.message.edit_text(text, reply_markup=keyboard)
            await message_or_callback.answer()  # 🩼


@manager_router.callback_query(F.data.startswith("review_"))
async def review(callback_query: types.CallbackQuery):
    """
    Показывает один отзыв по его id

    Args:
        callback_query (types.CallbackQuery): обратный вызов
    """
    call_type, review_id = callback_query.data.split("_")[0], int(callback_query.data.split("_")[1])
    review = await db.get_review(review_id)
    if not review:
        await callback_query.message.answer("Отзыв не найден")
        return
    logger.info(f"Менеджер {callback_query.from_user.id} просматривает отзыв {review_id}")
    
    message_text = (
        f"ID: {review.id}\n"
        f"Пользователь: {review.user_name} (ID: {review.user_id})\n"
        f"Оценка: {review.rating}\n"
        f"Тональность: {review.tonality.value}\n"
        f"Текст: {review.text}\n"
        f"Прочитан: {'Да' if review.readed else 'Нет'}\n"
        f"Отвечен: {'Да' if review.answered else 'Нет'}"
    )
    
    buttons = [
        [InlineKeyboardButton(text="Прочитано ✅", callback_data=f"readed_{review_id}")]
        if not review.readed else None,
        [InlineKeyboardButton(text="Ответить 👥", callback_data=f"reply_{review.id}")]
        if not review.answered else None
    ]
    buttons = list(filter(None, buttons))

    if review.readed:
        message_text += f"\nПрочитано менеджером с ID {review.readed_by}"

    reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None
    
    if call_type == "review":
        await callback_query.message.answer(
            message_text,
            reply_markup = reply_markup
        )
    else:
        await callback_query.message.edit_text(
            message_text,
            reply_markup = reply_markup
        )


@manager_router.callback_query(F.data.startswith("readed_"))
async def mark_as_readed(callback_query: types.CallbackQuery):
    """
    Помечает отзыв как прочитанный
    
    Args:
        callback_query (types.CallbackQuery): обратный вызов
    """
    review_id = int(callback_query.data.split("_")[1])
    manager_id = callback_query.from_user.id
    await db.mark_as_readed(review_id, manager_id)
    logger.info(f"Менеджер {manager_id} пометил отзыв {review_id} как прочитанный")
    await callback_query.answer("Отзыв помечен как прочитанный")
    await review(callback_query)


async def get_reviews_page(page: int, reviews_per_page: int = 5) -> tuple[str, InlineKeyboardMarkup]:
    """
    Рендерит клавиатуру нужной страницы с непрочитанными отзывами

    Args:
        page (int): номер страницы списка отзывавов
        reviews_per_page (int, optional): кол-во отзывов на одной странице. По умолчанию 5.

    Returns:
        tuple[str, InlineKeyboardMarkup]: (текст шапки клавиатуры, сама клавиатура)
    """    
    unread_reviews = await db.unreaded_reviews()
    total_reviews = len(unread_reviews)
    total_pages = (total_reviews + reviews_per_page - 1) // reviews_per_page
    start = page * reviews_per_page
    end = start + reviews_per_page
    reviews_to_display = unread_reviews[start:end]

    if not reviews_to_display:
        return "Нет непрочитанных отзывов.", None

    buttons = []
    
    # отзывы
    for review in reviews_to_display:
        review_text = f"{review.rating}🌟 - {review.tonality.value} - {review.text[:10]}..."
        buttons.append([InlineKeyboardButton(text=review_text, callback_data=f"review_{review.id}")])

    # взад-вперёд
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"unread_reviews_page_{page - 1}"))
    if end < total_reviews:
        navigation_buttons.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"unread_reviews_page_{page + 1}"))
    if navigation_buttons:
        buttons.append(navigation_buttons)

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    text = f"Непрочитанные отзывы (страница {page + 1}/{total_pages}):"
    return text, keyboard


@manager_router.callback_query(F.data.startswith("reply_"))
async def start_manager_reply(callback: types.CallbackQuery, state: FSMContext):
    review_id = int(callback.data.split("_")[1])
    review = await db.get_review(review_id)
    
    if not review:
        await callback.message.answer("Отзыв не найден.")
        await callback.answer()
        return

    if review.answered:
        await callback.message.answer("Этот отзыв уже обработан.")
        await callback.answer()
        return
    
    await state.update_data(review_id=review_id, user_id=review.user_id, manager_id=callback.from_user.id)
    await state.set_state(ManagerForm.waiting_for_manager_reply)
    await callback.message.answer("Введите ваш ответ пользователю:")
    await callback.answer()


@manager_router.message(ManagerForm.waiting_for_manager_reply)
async def end_manager_reply(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user_id = data["user_id"]
    review_id = data["review_id"]
    manager_id = data["manager_id"]
    
    try:
        await bot.send_message(chat_id=user_id, text=f"Ответ от менеджера кофейни MuffinMate:\n\n{message.text}")
        await message.answer("Ответ успешно отправлен пользователю!")
        await db.mark_as_readed(review_id, manager_id)
        await db.mark_as_answered(review_id)
        logger.info(f"Менеджер {message.from_user.id} ответил на отзыв {review_id}")
    except Exception as e:
        await message.answer("Ошибка при отправке ответа пользователю.")
        logger.warning(f"Ошибка при отправке ответа пользователю {user_id}: {e}")
    
    await state.clear()


@manager_router.message(Command("manager_statistics"))
@manager_router.message(F.text == "Статистика менеджеров 👩‍💼")
async def manager_profile(message: types.Message):
    """
    Открывает статистику менеджеров

    Args:
        message (types.Message): сообщение
    """
    start = datetime.now() - timedelta(days=30)
    end = datetime.now()
    stats = await db.get_manager_info(start, end)
    
    stats_text = "Статистика менеджеров за последние 30 дней:\n\n"
    for manager, activity in stats:
        stats_text += f"👤 {manager.name} (ID: {manager.user_id}) — {activity} обработанных отзывов\n"

    await message.answer(stats_text)


@manager_router.callback_query(F.data == "custom_query")
async def custom_query(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите запрос:")
    await state.set_state(ManagerForm.waiting_for_custom_query)
    await callback_query.answer()
    

@manager_router.message(ManagerForm.waiting_for_custom_query)
async def process_custom_query(message: types.Message, state: FSMContext):
    query = message.text
    answer = await ai.custom_query(query)

    if answer == "graphics/graph.png":
        await message.answer_photo(photo=types.FSInputFile(answer))
    else: 
        await message.answer(answer)
        
    await state.clear()
