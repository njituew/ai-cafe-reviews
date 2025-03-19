from aiogram import types, F, Dispatcher
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from src.utils import is_manager

from src.logger import logger
import dbtest   # тестовый модуль имитирующий функции для бд (арс, работаем)


async def manager_panel(message: types.Message):
    """
    Открывает панель менеджера

    Args:
        message (types.Message): сообщение
    """
    user_id = message.chat.id
    if not is_manager(user_id):
        await message.answer("Вы не менеджер")
        logger.warning(f"Попытка открыть панель менеджера не менеджером: {user_id}")
        return

    logger.info(f"Менеджер {user_id} открыл панель менеджера")
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Непрочитанные отзывы 🗣️")],
            [KeyboardButton(text="Дашборд 💻"), KeyboardButton(text="Динамика удовлетворённости 📈")],
            [KeyboardButton(text="Профиль менеджера 👩‍💼")]
        ],
        resize_keyboard=True
    )
    await message.answer("Панель менеджера открыта", reply_markup=keyboard)


async def unread_reviews(message: types.Message):
    """
    Открывает список непрочитанных отзывов

    Args:
        message (types.Message): сообщение
    """
    user_id = message.chat.id
    if not is_manager(user_id):
        await message.answer("Вы не менеджер")
        logger.warning(f"Попытка открыть список непрочитанных отзывов не менеджером: {user_id}")
        return

    logger.info(f"Менеджер {user_id} открыл список непрочитанных отзывов")
    text, keyboard = get_reviews_page(0)
    if keyboard is None:
        await message.answer(text)
    else:
        await message.answer(text, reply_markup=keyboard)


async def unread_reviews_pagination(callback_query: types.CallbackQuery):
    """
    Листает страницы с непрочитанными отзывами

    Args:
        callback_query (types.CallbackQuery): сообщение
    """
    page = int(callback_query.data.split("_")[2])

    text, keyboard = get_reviews_page(page)
    if keyboard is None:
        await callback_query.message.edit_text(text)
    else:
        await callback_query.message.edit_text(text, reply_markup=keyboard)
    await callback_query.answer()


async def review(callback_query: types.CallbackQuery):
    """
    Показывает один отзыв по его id

    Args:
        callback_query (types.CallbackQuery): обратный вызов
    """
    review_id = int(callback_query.data.split("_")[1])
    logger.info(f"Менеджер {callback_query.from_user.id} просматривает отзыв {review_id}")
    review = dbtest.get_review(review_id)
    await callback_query.message.answer(
        f"ID: {review['review_id']}"
        f"\nОтзыв: {review['text']}"
        f"\nОценка: {review['mark']}"
        f"\nТональность: {review['tonality']}"
        f"\nПрочитан: {'Да' if review['readed'] else 'Нет'}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Прочитано ✅", callback_data=f"readed_{review_id}")]]
        )
    )


def register_handlers(dp: Dispatcher):
    """
    Регистрация всех ручек для менеджера

    Args:
        dp (Dispatcher): диспетчер бота
    """
    dp.message.register(manager_panel, Command("manager"))
    dp.message.register(unread_reviews, F.text == "Непрочитанные отзывы 🗣️")
    dp.callback_query.register(unread_reviews_pagination, lambda c: c.data.startswith("prev_page_") or c.data.startswith("next_page_"))
    dp.callback_query.register(review, F.data.startswith("review_"))


# ================================================ Utils here ================================================
def get_reviews_page(page: int) -> tuple[str, InlineKeyboardMarkup]:
    """
    Рендерит клавиатуру нужной страницы с непрочитанными отзывами

    Args:
        page (int): номер страницы

    Returns:
        tuple[str, InlineKeyboardMarkup]: (текст шапки клавиатуры, сама клавиатура)
    """
    reviews_per_page = 5
    unread_reviews = dbtest.get_unreaded_reviews()
    total_reviews = len(unread_reviews)
    start = page * reviews_per_page
    end = start + reviews_per_page
    reviews_to_display = unread_reviews[start:end]

    if not reviews_to_display:
        return "Нет непрочитанных отзывов.", None

    buttons = []
    
    # отзывы
    for review in reviews_to_display:
        review_text = f"Оценка: {review['mark']} - {review['text'][:10]}..."
        buttons.append([InlineKeyboardButton(text=review_text, callback_data=f"review_{review['review_id']}")])

    # взад-вперёд
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"prev_page_{page - 1}"))
    if end < total_reviews:
        navigation_buttons.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"next_page_{page + 1}"))
    if navigation_buttons:
        buttons.append(navigation_buttons)

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    text = f"Непрочитанные отзывы (страница {page + 1}):"
    return text, keyboard
