from aiogram import types, F, Dispatcher, Router, BaseMiddleware
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
)

from src.utils import is_manager
from src.logger import logger
from src.graph import *
import db.utils as db


class ManagerCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = event.chat.id if isinstance(event, types.Message) else event.from_user.id
        if not is_manager(user_id):
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
    # if not is_manager(user_id):
    #     await message.answer("Вы не менеджер")
    #     logger.warning(f"Попытка открыть панель менеджера не менеджером: {user_id}")
    #     return

    logger.info(f"Менеджер {user_id} открыл панель менеджера")
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Динамика удовлетворённости 📈")],
            [KeyboardButton(text="Непрочитанные отзывы 🗣️"), KeyboardButton(text="Дашборд 💻")],
            [KeyboardButton(text="Профиль менеджера 👩‍💼")]
        ],
        resize_keyboard=True
    )
    await message.answer("Панель менеджера открыта", reply_markup=keyboard)


# @manager_router.message(F.text == "Динамика удовлетворённости 📈")
# async def satisfaction_dynamics(message: types.Message):
#     """
#     Отображает динамику удовлетворённости

#     Args:
#         message (types.Message): сообщение
#     """
#     user_id = message.chat.id
#     if not is_manager(user_id):
#         await message.answer("Вы не менеджер")
#         logger.warning(f"Попытка открыть список непрочитанных отзывов не менеджером: {user_id}")
#         return
    
#     buffer = await test_graph()
#     await message.answer_photo(
#         photo=BufferedInputFile(buffer.getvalue(), filename="graph.png"),
#         caption="Динамика удовлетворённости"
#     )


@manager_router.message(F.text == "Дашборд 💻")
async def satisfaction_dynamics(message: types.Message):
    """
    Отображает динамику удовлетворённости

    Args:
        message (types.Message): сообщение
    """
    user_id = message.chat.id
    if not is_manager(user_id):
        await message.answer("Вы не менеджер")
        logger.warning(f"Попытка открыть список непрочитанных отзывов не менеджером: {user_id}")
        return
    
    buffer = await distribution_of_ratings([3, 2, 3, 5, 10])    # test data
    await message.answer_photo(
        photo=BufferedInputFile(buffer.getvalue(), filename="graph.png"),
        caption="Дашборд"
    )


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
    if not is_manager(user_id):
        await message_or_callback.answer("Вы не менеджер")
        logger.warning(f"Попытка открыть список непрочитанных отзывов не менеджером: {user_id}")
        return

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
    review_id = int(callback_query.data.split("_")[1])
    review = await db.get_review(review_id)
    if not review:
        await callback_query.message.answer("Отзыв не найден")
        return
    logger.info(f"Менеджер {callback_query.from_user.id} просматривает отзыв {review_id}")
    
    message_text = (
        f"ID: {review}\n"
        f"Оценка: {review.rating}\n"
        f"Тональность: {review.tonality}\n"
        f"Текст: {review.text}\n"
        f"Прочитан: {'Да' if review.readed else 'Нет'}"
    )
    
    if review.readed:
        message_text += f"\nПрочитано менеджером с ID {review.readed_by}"
        reply_markup = None
    else:
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard = [[InlineKeyboardButton(text="Прочитано ✅", callback_data=f"readed_{review_id}")]]
        )
    
    await callback_query.message.answer(
        message_text,
        reply_markup = reply_markup
    )


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
        review_text = f"{review.rating}🌟 - {review.tonality} - {review.text[:10]}..."
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
